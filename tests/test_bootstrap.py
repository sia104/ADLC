from __future__ import annotations

import json
from pathlib import Path

import pytest

from adlc_bootstrap.cli import (
    BootstrapError,
    install_from_checkout,
)


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source"

    (source / "bootstrap").mkdir(parents=True)
    (source / ".adlc" / "evidence").mkdir(parents=True)
    (source / ".codex" / "skills" / "spec-it").mkdir(
        parents=True
    )
    (source / ".github" / "workflows").mkdir(parents=True)

    (source / ".adlc" / "VERSION").write_text(
        "V0.5\n",
        encoding="utf-8",
    )

    (source / ".adlc" / "runtime.txt").write_text(
        "runtime\n",
        encoding="utf-8",
    )

    (source / ".adlc" / "evidence" / "private.txt").write_text(
        "do not copy\n",
        encoding="utf-8",
    )

    (
        source
        / ".codex"
        / "skills"
        / "spec-it"
        / "SKILL.md"
    ).write_text(
        "skill\n",
        encoding="utf-8",
    )

    (
        source
        / ".github"
        / "workflows"
        / "adlc.yml"
    ).write_text(
        "name: ADLC\n",
        encoding="utf-8",
    )

    (source / "AGENTS.md").write_text(
        "governance\n",
        encoding="utf-8",
    )

    manifest = {
        "schema_version": "1.0",
        "managed_paths": [
            {
                "source": ".adlc",
                "destination": ".adlc",
                "exclude": [
                    "evidence/**",
                    "install.json",
                ],
            },
            {
                "source": ".codex/skills",
                "destination": ".codex/skills",
            },
            {
                "source": ".github/workflows/adlc.yml",
                "destination": ".github/workflows/adlc.yml",
            },
            {
                "source": "AGENTS.md",
                "destination": "AGENTS.md",
            },
        ],
        "gitignore_entries": [
            ".adlc/evidence/",
            ".adlc/.venv/",
        ],
    }

    (source / "bootstrap" / "manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    return source


def install(source: Path, target: Path) -> dict[str, object]:
    return install_from_checkout(
        source,
        target,
        source_repository="https://example.invalid/ADLC.git",
        source_ref="v0.5.0",
        source_commit="abc123",
    )


def test_installs_reusable_adlc(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "project"

    record = install(source, target)

    assert (target / ".adlc" / "VERSION").read_text().strip() == "V0.5"
    assert (target / "AGENTS.md").exists()
    assert (
        target
        / ".codex"
        / "skills"
        / "spec-it"
        / "SKILL.md"
    ).exists()
    assert (
        target
        / ".github"
        / "workflows"
        / "adlc.yml"
    ).exists()

    assert not (
        target
        / ".adlc"
        / "evidence"
        / "private.txt"
    ).exists()

    assert record["source_ref"] == "v0.5.0"


def test_records_install_provenance(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "project"

    install(source, target)

    data = json.loads(
        (target / ".adlc" / "install.json").read_text(
            encoding="utf-8"
        )
    )

    assert data["adlc_version"] == "V0.5"
    assert data["source_commit"] == "abc123"
    assert data["source_ref"] == "v0.5.0"
    assert data["managed_files"]


def test_conflicting_existing_file_blocks_install(
    tmp_path: Path,
) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "project"
    target.mkdir()

    (target / "AGENTS.md").write_text(
        "user-owned contents\n",
        encoding="utf-8",
    )

    with pytest.raises(BootstrapError):
        install(source, target)

    assert not (target / ".adlc" / "VERSION").exists()

    assert (
        target / "AGENTS.md"
    ).read_text(encoding="utf-8") == "user-owned contents\n"


def test_identical_existing_file_is_allowed(
    tmp_path: Path,
) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "project"
    target.mkdir()

    (target / "AGENTS.md").write_text(
        "governance\n",
        encoding="utf-8",
    )

    install(source, target)

    assert (target / ".adlc" / "VERSION").exists()


def test_gitignore_is_extended_without_overwrite(
    tmp_path: Path,
) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "project"
    target.mkdir()

    (target / ".gitignore").write_text(
        "dist/\n",
        encoding="utf-8",
    )

    install(source, target)

    contents = (target / ".gitignore").read_text(
        encoding="utf-8"
    )

    assert "dist/" in contents
    assert ".adlc/evidence/" in contents
    assert ".adlc/.venv/" in contents


def test_second_init_is_blocked(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    target = tmp_path / "project"

    install(source, target)

    with pytest.raises(
        BootstrapError,
        match="already installed",
    ):
        install(source, target)
