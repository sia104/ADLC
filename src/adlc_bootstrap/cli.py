from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Any

DEFAULT_SOURCE = "https://github.com/sia104/ADLC.git"


class BootstrapError(RuntimeError):
    """Raised when an ADLC bootstrap operation cannot safely continue."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(value: str) -> Path:
    pure = PurePosixPath(value)

    if pure.is_absolute() or ".." in pure.parts:
        raise BootstrapError(f"unsafe manifest path: {value}")

    return Path(*pure.parts)


def _excluded(relative: Path, patterns: list[str]) -> bool:
    value = relative.as_posix()

    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if value == prefix or value.startswith(prefix + "/"):
                return True

        if fnmatch.fnmatch(value, pattern):
            return True

    return False


def _run(command: list[str], cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise BootstrapError(
            f"required command is not available: {command[0]}"
        ) from error

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise BootstrapError(message or f"{command[0]} failed")

    return result.stdout.strip()


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.adlc-tmp-{uuid.uuid4().hex}"
    )

    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        f".{destination.name}.adlc-tmp-{uuid.uuid4().hex}"
    )

    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _load_manifest(source_root: Path) -> dict[str, Any]:
    path = source_root / "bootstrap" / "manifest.json"

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise BootstrapError(
            "bootstrap manifest is missing from the ADLC source"
        ) from error
    except json.JSONDecodeError as error:
        raise BootstrapError(
            f"invalid bootstrap manifest: {error.msg}"
        ) from error

    if not isinstance(manifest, dict):
        raise BootstrapError("bootstrap manifest must contain an object")

    managed = manifest.get("managed_paths")
    if not isinstance(managed, list) or not managed:
        raise BootstrapError(
            "bootstrap manifest contains no managed paths"
        )

    return manifest


def _collect_plan(
    source_root: Path,
    manifest: dict[str, Any],
) -> list[tuple[Path, Path]]:
    plan: list[tuple[Path, Path]] = []

    managed_paths = manifest["managed_paths"]

    for item in managed_paths:
        if not isinstance(item, dict):
            raise BootstrapError("invalid managed-path entry")

        source_relative = _safe_relative_path(str(item["source"]))
        destination_relative = _safe_relative_path(
            str(item["destination"])
        )

        excludes = [str(value) for value in item.get("exclude", [])]

        source = source_root / source_relative

        if not source.exists():
            raise BootstrapError(
                f"managed source does not exist: {source_relative}"
            )

        if source.is_symlink():
            raise BootstrapError(
                f"managed source may not be a symlink: {source_relative}"
            )

        if source.is_file():
            plan.append((source, destination_relative))
            continue

        for candidate in sorted(source.rglob("*")):
            if candidate.is_symlink():
                raise BootstrapError(
                    f"managed source contains symlink: {candidate}"
                )

            if not candidate.is_file():
                continue

            child = candidate.relative_to(source)

            if _excluded(child, excludes):
                continue

            plan.append(
                (
                    candidate,
                    destination_relative / child,
                )
            )

    return sorted(plan, key=lambda pair: pair[1].as_posix())


def _check_conflicts(
    target: Path,
    plan: list[tuple[Path, Path]],
) -> None:
    conflicts: list[str] = []

    install_metadata = target / ".adlc" / "install.json"

    if install_metadata.exists():
        raise BootstrapError(
            "ADLC is already installed; upgrade is not implemented yet"
        )

    for source, relative in plan:
        destination = target / relative

        if not destination.exists():
            continue

        if not destination.is_file():
            conflicts.append(relative.as_posix())
            continue

        if _sha256(source) != _sha256(destination):
            conflicts.append(relative.as_posix())

    gitignore = target / ".gitignore"

    if gitignore.exists() and not gitignore.is_file():
        conflicts.append(".gitignore")

    if conflicts:
        formatted = "\n".join(f"  - {item}" for item in conflicts)
        raise BootstrapError(
            "bootstrap would overwrite existing files:\n"
            f"{formatted}"
        )


def _merge_gitignore(
    target: Path,
    entries: list[str],
) -> None:
    path = target / ".gitignore"

    existing = (
        path.read_text(encoding="utf-8")
        if path.exists()
        else ""
    )

    current = {
        line.strip()
        for line in existing.splitlines()
        if line.strip()
    }

    additions = [
        entry
        for entry in entries
        if entry not in current
    ]

    if not additions:
        return

    updated = existing

    if updated and not updated.endswith("\n"):
        updated += "\n"

    updated += "".join(f"{entry}\n" for entry in additions)

    _atomic_write_bytes(path, updated.encode("utf-8"))


def install_from_checkout(
    source_root: Path,
    target: Path,
    *,
    source_repository: str,
    source_ref: str,
    source_commit: str,
) -> dict[str, Any]:
    source_root = source_root.resolve()
    target = target.resolve()

    target_existed = target.exists()

    if target.exists() and not target.is_dir():
        raise BootstrapError(
            f"target is not a directory: {target}"
        )

    target.mkdir(parents=True, exist_ok=True)

    manifest = _load_manifest(source_root)
    plan = _collect_plan(source_root, manifest)

    _check_conflicts(target, plan)

    version_file = source_root / ".adlc" / "VERSION"

    if not version_file.is_file():
        raise BootstrapError("ADLC VERSION file is missing")

    adlc_version = version_file.read_text(
        encoding="utf-8"
    ).strip()

    ignore_entries = [
        str(value)
        for value in manifest.get("gitignore_entries", [])
    ]

    created_files: list[Path] = []

    gitignore = target / ".gitignore"
    gitignore_existed = gitignore.exists()
    gitignore_before = (
        gitignore.read_bytes()
        if gitignore_existed
        else None
    )

    try:
        for source, relative in plan:
            destination = target / relative

            if destination.exists():
                continue

            _atomic_copy(source, destination)
            created_files.append(destination)

        _merge_gitignore(target, ignore_entries)

        hashes = {
            relative.as_posix(): _sha256(target / relative)
            for _, relative in plan
        }

        install_record: dict[str, Any] = {
            "schema_version": "1.0",
            "adlc_version": adlc_version,
            "source_repository": source_repository,
            "source_ref": source_ref,
            "source_commit": source_commit,
            "installed_at": datetime.now(UTC).isoformat(),
            "managed_files": hashes,
        }

        install_path = target / ".adlc" / "install.json"

        _atomic_write_bytes(
            install_path,
            (
                json.dumps(
                    install_record,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8"),
        )

        created_files.append(install_path)

        return install_record

    except Exception:
        if target_existed:
            for path in reversed(created_files):
                path.unlink(missing_ok=True)

            if gitignore_existed and gitignore_before is not None:
                _atomic_write_bytes(
                    gitignore,
                    gitignore_before,
                )
            elif not gitignore_existed:
                gitignore.unlink(missing_ok=True)
        else:
            shutil.rmtree(target, ignore_errors=True)

        raise


def _default_ref() -> str:
    try:
        package_version = version("adlc-bootstrap")
    except PackageNotFoundError:
        return "master"

    return f"v{package_version}"


def bootstrap_from_git(
    target: Path,
    *,
    source_repository: str,
    source_ref: str,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(
        prefix="adlc-bootstrap-"
    ) as temporary_directory:
        checkout = Path(temporary_directory) / "source"

        _run(
            [
                "git",
                "clone",
                "--quiet",
                "--depth",
                "1",
                "--branch",
                source_ref,
                "--single-branch",
                source_repository,
                str(checkout),
            ]
        )

        commit = _run(
            [
                "git",
                "-C",
                str(checkout),
                "rev-parse",
                "HEAD",
            ]
        )

        return install_from_checkout(
            checkout,
            target,
            source_repository=source_repository,
            source_ref=source_ref,
            source_commit=commit,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="adlc-bootstrap",
        description="Install a versioned ADLC into a project.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    init_parser = subparsers.add_parser(
        "init",
        help="Install ADLC into a new or existing project.",
    )

    init_parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory.",
    )

    init_parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help="Canonical ADLC Git repository.",
    )

    init_parser.add_argument(
        "--ref",
        default=_default_ref(),
        help="ADLC Git tag or branch.",
    )

    args = parser.parse_args()

    if args.command != "init":
        parser.error("unsupported command")

    try:
        result = bootstrap_from_git(
            Path(args.target),
            source_repository=str(args.source),
            source_ref=str(args.ref),
        )
    except BootstrapError as error:
        parser.exit(
            2,
            f"adlc-bootstrap: {error}\n",
        )

    print(
        f"Installed {result['adlc_version']} "
        f"into {Path(args.target).resolve()}"
    )
    print(
        f"Source: {result['source_repository']} "
        f"@ {result['source_ref']}"
    )


if __name__ == "__main__":
    main()
