#!/usr/bin/env python3
"""Build-Skript für github-repo.skill – plattformunabhängiges Gegenstück zu build_skill.sh.

Erzeugt aus den Quelldateien des Repositorys ein ZIP-Archiv, das sich in
Claude Desktop und auf claude.ai unter Einstellungen → Skills hochladen
lässt. Das Paket-Layout steht in skill-manifest.txt im Projekt-Root — dort
und nur dort werden Dateien hinzugefügt oder umbenannt.

Aufruf:  python scripts/build_skill.py

Danach `python scripts/validate_skill.py` ausführen und das Ergebnis
committen: die CI prüft, ob das eingecheckte Archiv zu den Quellen passt.

Reproduzierbar wie das Bash-Skript: fester Zeitstempel für alle Einträge,
sortierte Reihenfolge (Bytereihenfolge wie LC_ALL=C), keine Verzeichnis-
einträge, Unix-Dateiattribute 0644, Deflate mit Standardstufe.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

SKILL_NAME = "github-repo"
SOURCE_TIMESTAMP = (2024, 1, 1, 0, 0, 0)  # entspricht touch -t 202401010000.00


def read_manifest(manifest: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\r")
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            sys.exit(f"FEHLER: Manifest-Zeile ohne '=': '{line}'")
        target, source = line.split("=", 1)
        if not target or not source:
            sys.exit(f"FEHLER: leerer Ziel- oder Quellpfad in '{line}'")
        entries.append((target, source))
    return entries


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    manifest = project_root / "skill-manifest.txt"
    output = project_root / f"{SKILL_NAME}.skill"

    print(f"Building {SKILL_NAME}.skill ...\n")
    if not manifest.is_file():
        sys.exit(f"FEHLER: skill-manifest.txt fehlt in {project_root}")

    entries = read_manifest(manifest)
    if not entries:
        sys.exit("FEHLER: Manifest enthaelt keine Dateien")
    if not any(target == "SKILL.md" for target, _ in entries):
        sys.exit("FEHLER: Das Manifest muss SKILL.md enthalten")

    print("Dateien gemaess skill-manifest.txt sammeln:")
    files: dict[str, Path] = {}
    for target, source in entries:
        src = project_root / source
        if not src.is_file():
            sys.exit(f"FEHLER: Quelldatei '{source}' (-> {target}) nicht gefunden")
        arcname = f"{SKILL_NAME}/{target}"
        files[arcname] = src
        print(f"   {source} -> {target}")

    print("\nArchiv erzeugen ...")
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for arcname in sorted(files, key=lambda s: s.encode("utf-8")):
            info = zipfile.ZipInfo(arcname, date_time=SOURCE_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix, wie zip(1)
            info.external_attr = 0o100644 << 16
            zf.writestr(info, files[arcname].read_bytes())

    size_kb = output.stat().st_size / 1024
    print(f"\nOK: {output} ({size_kb:.0f}K, {len(files)} Dateien)\n")
    print("Paketinhalt:")
    for arcname in sorted(files, key=lambda s: s.encode("utf-8")):
        print(f"   {arcname}")
    print("\nInstallieren:")
    print("   Claude Desktop bzw. claude.ai -> Einstellungen -> Capabilities/Skills")
    print(f"   -> Skill hochladen -> {output.name} auswaehlen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
