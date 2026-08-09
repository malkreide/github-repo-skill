#!/usr/bin/env python3
"""Prüft das Skill-Paket: Manifest, Frontmatter und das eingecheckte Archiv.

`validate_repo.py` prüft dieses Repository als *Repository*. Dieses Skript
prüft es als *Skill-Paket* — also das, was beim Upload in Claude Desktop
tatsächlich ankommt. Beides überlappt sich nicht: ein Repo kann tadellos sein
und trotzdem ein Archiv mitliefern, das drei Commits hinterherhinkt.

Prüfungen:
  P1  skill-manifest.txt ist wohlgeformt, alle Quelldateien existieren
  P2  SKILL.md hat gültiges Frontmatter (name, description samt Längenlimit)
  P3  Jeder Skill-Pfad, den SKILL.md nennt, ist vom Manifest abgedeckt
  P4  Das eingecheckte github-repo.skill entspricht den Quelldateien
  P5  Relative Markdown-Links lösen auch im Paket-Layout auf

Aufruf:
    python3 scripts/validate_skill.py

Exit-Code 0 = alles in Ordnung, 1 = mindestens eine Prüfung fehlgeschlagen.
"""

from __future__ import annotations

import os
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "github-repo"
MANIFEST = ROOT / "skill-manifest.txt"
ARCHIVE = ROOT / f"{SKILL_NAME}.skill"

# Obergrenze der Skill-Plattform für das Frontmatter-Feld `description`.
# Der Upload wird abgewiesen, nicht gekürzt — und die description dieses Skills
# liegt mit gut 1000 Zeichen dicht darunter. Der Check ist hier also kein
# Vorsichtsmass, sondern ein Geländer an einer echten Kante.
DESCRIPTION_MAX_CHARS = 1024
DESCRIPTION_MIN_CHARS = 40

# Präfixe, unter denen SKILL.md auf Paketinhalt verweist. Alles andere in
# Backticks (`.github/workflows/`, `pyproject.toml`, Befehle) meint Dateien im
# Zielrepo, nicht im Paket.
PACKAGE_PREFIXES = ("scripts/", "references/", "assets/")

# Vorlagen sind das einzige Material, dessen Links absichtlich ins Leere zeigen:
# `assets/templates/README.md` verlinkt CHANGELOG.md und SECURITY.md des Repos,
# das damit erst erzeugt wird. Diese Links dürfen weder hier noch im Paket
# auflösen — sie werden beim Kopieren zu gültigen Links.
LINK_CHECK_SKIP_PREFIXES = ("assets/templates/",)

BACKTICK_RE = re.compile(r"`([^`\n]+)`")
LINK_RE = re.compile(r"\]\((?!https?:|mailto:|#)([^)\s]+)\)")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

# Code-Blöcke und Inline-Code werden vor der Link-Prüfung entfernt. Ohne das
# meldet der Check zwei Stellen, an denen die Markdown-Syntax *Gegenstand* des
# Textes ist und nicht Verweis: Schritt 4 in SKILL.md zitiert die Kopfzeile
# `[English Version](README.md)` als Vorgabe für erzeugte Repos, und
# review-rules.md nennt `![](...)` als Muster, auf das zu achten ist.
FENCE_RE = re.compile(r"^(?P<f>```+|~~~+)[^\n]*\n.*?^(?P=f)[ \t]*$", re.M | re.S)
CODE_SPAN_RE = re.compile(r"(?P<t>`+)[^`]*?(?P=t)")


def strip_code(text: str) -> str:
    """Entfernt Codeblöcke und Inline-Code — dort ist Markdown Zitat, kein Link."""
    return CODE_SPAN_RE.sub("", FENCE_RE.sub("", text))


errors: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def read_manifest() -> dict[str, str]:
    """P1 — liest skill-manifest.txt als {Zielpfad im Paket: Quellpfad im Repo}."""
    if not MANIFEST.exists():
        fail("skill-manifest.txt fehlt.")
        return {}

    mapping: dict[str, str] = {}
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    for lineno, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            fail(
                f"skill-manifest.txt:{lineno}: erwartet 'ziel=quelle', "
                f"gefunden '{line}'"
            )
            continue
        target, source = (part.strip() for part in line.split("=", 1))
        if not target or not source:
            fail(f"skill-manifest.txt:{lineno}: leerer Ziel- oder Quellpfad")
            continue
        if target.startswith("/") or ".." in PurePosixPath(target).parts:
            fail(f"skill-manifest.txt:{lineno}: Zielpfad '{target}' verlässt das Paket")
            continue
        if target in mapping:
            fail(f"skill-manifest.txt:{lineno}: Zielpfad '{target}' doppelt vergeben")
            continue
        mapping[target] = source
    return mapping


def check_manifest_sources(mapping: dict[str, str]) -> None:
    """P1 — jede Manifest-Quelle existiert, SKILL.md ist dabei."""
    for target, source in sorted(mapping.items()):
        if not (ROOT / source).is_file():
            fail(f"Manifest: Quelldatei '{source}' (-> {target}) existiert nicht.")
    if "SKILL.md" not in mapping:
        fail(
            "Manifest: Eintrag für SKILL.md fehlt — ohne ihn ist das Paket kein Skill."
        )


def check_frontmatter() -> None:
    """P2 — Frontmatter von SKILL.md gegen die Vorgaben der Skill-Plattform."""
    path = ROOT / "SKILL.md"
    if not path.is_file():
        fail("SKILL.md fehlt im Repository-Root.")
        return

    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        fail("SKILL.md: kein YAML-Frontmatter am Dateianfang gefunden.")
        return

    block = match.group(1)
    name = re.search(r"^name:\s*(\S.*)$", block, re.M)
    description = re.search(r"^description:\s*(\S.*)$", block, re.M)

    if not name:
        fail("SKILL.md: Frontmatter-Feld 'name' fehlt.")
    elif name.group(1).strip() != SKILL_NAME:
        fail(
            f"SKILL.md: 'name' ist '{name.group(1).strip()}', "
            f"erwartet '{SKILL_NAME}' — der Name muss zum Paketverzeichnis passen."
        )

    if not description:
        fail("SKILL.md: Frontmatter-Feld 'description' fehlt.")
        return

    length = len(description.group(1).strip())
    if length < DESCRIPTION_MIN_CHARS:
        fail(
            "SKILL.md: 'description' ist zu kurz, um den Skill zuverlässig auszulösen."
        )
    elif length > DESCRIPTION_MAX_CHARS:
        fail(
            f"SKILL.md: 'description' hat {length} Zeichen, erlaubt sind höchstens "
            f"{DESCRIPTION_MAX_CHARS}. Der Upload wird sonst abgewiesen."
        )
    else:
        notes.append(f"description: {length}/{DESCRIPTION_MAX_CHARS} Zeichen")


def check_skill_references(mapping: dict[str, str]) -> None:
    """P3 — jeder Paketpfad aus SKILL.md steht auch im Manifest.

    SKILL.md nennt seine Begleitdateien in Backticks, mal als Datei
    (`scripts/validate_repo.py`), mal als Verzeichnis (`assets/gitignore/`).
    Beide Formen werden geprüft: eine Datei muss als Zielpfad vorkommen, ein
    Verzeichnis mindestens einen Eintrag unter sich haben.
    """
    path = ROOT / "SKILL.md"
    if not path.is_file():
        return

    targets = set(mapping)
    tokens = {
        token
        for token in BACKTICK_RE.findall(path.read_text(encoding="utf-8"))
        if token.startswith(PACKAGE_PREFIXES)
    }
    if not tokens:
        notes.append(
            "SKILL.md nennt keine Begleitdateien — Manifest nicht gegengeprüft"
        )
        return

    for token in sorted(tokens):
        if token.endswith("/"):
            if not any(t.startswith(token) for t in targets):
                fail(
                    f"SKILL.md verweist auf das Verzeichnis '{token}', "
                    "das Manifest packt daraus keine einzige Datei."
                )
        elif token not in targets:
            fail(f"SKILL.md verweist auf '{token}', das Manifest packt es nicht.")


def check_archive_is_current(mapping: dict[str, str]) -> None:
    """P4 — vergleicht das eingecheckte Archiv inhaltlich mit den Quelldateien.

    Verglichen werden Dateiinhalte, nicht ZIP-Bytes. Der Build ist zwar
    reproduzierbar, aber ein Byte-Vergleich würde bei jeder zip-Version neu
    scheitern und dabei nichts aussagen, was der Inhaltsvergleich nicht sagt.
    """
    if not ARCHIVE.exists():
        fail(
            f"{ARCHIVE.name} fehlt. './scripts/build_skill.sh' ausführen und committen."
        )
        return

    try:
        with zipfile.ZipFile(ARCHIVE) as zf:
            members = {n for n in zf.namelist() if not n.endswith("/")}
            expected = {f"{SKILL_NAME}/{t}" for t in mapping}

            for extra in sorted(members - expected):
                fail(f"{ARCHIVE.name} enthält '{extra}', das nicht im Manifest steht.")
            for missing in sorted(expected - members):
                fail(f"{ARCHIVE.name} fehlt '{missing}'.")

            for target, source in sorted(mapping.items()):
                member = f"{SKILL_NAME}/{target}"
                src = ROOT / source
                if member not in members or not src.is_file():
                    continue
                if zf.read(member) != src.read_bytes():
                    fail(
                        f"{ARCHIVE.name}: '{target}' weicht von '{source}' ab. "
                        "'./scripts/build_skill.sh' ausführen und das Ergebnis "
                        "committen."
                    )
    except zipfile.BadZipFile:
        fail(f"{ARCHIVE.name} ist kein gültiges ZIP-Archiv.")


def check_links_resolve_in_package(mapping: dict[str, str]) -> None:
    """P5 — relative Links der gepackten Dateien im Paket-Layout auflösen.

    Heute ist das Mapping 1:1, ein Link, der im Repo auflöst, löst also auch im
    Paket auf. Das ist eine Eigenschaft des Manifests, keine Garantie: sobald
    eine Datei beim Packen an eine andere Stelle wandert, verschiebt sich jeder
    relative Link darin mit — und im Repo fällt davon nichts auf, weil dort
    weiterhin alles stimmt. Genau diese Lücke schliesst dieser Check.
    """
    packaged = set(mapping)

    for target, source in sorted(mapping.items()):
        if target.startswith(LINK_CHECK_SKIP_PREFIXES):
            continue
        src = ROOT / source
        if not src.is_file() or src.suffix != ".md":
            continue
        pkg_dir = PurePosixPath(target).parent
        body = strip_code(src.read_text(encoding="utf-8"))
        for match in LINK_RE.finditer(body):
            link = match.group(1).split("#")[0]
            if not link:
                continue
            resolved = os.path.normpath(str(pkg_dir / link)).replace(os.sep, "/")
            if resolved not in packaged:
                fail(
                    f"{source}: Link '{link}' löst im Paket nicht auf "
                    f"(erwartet '{resolved}' unterhalb von {SKILL_NAME}/)."
                )


def main() -> int:
    mapping = read_manifest()
    if mapping:
        check_manifest_sources(mapping)
        check_skill_references(mapping)
        check_archive_is_current(mapping)
        check_links_resolve_in_package(mapping)
    check_frontmatter()

    for note in notes:
        print(f"   {note}")

    if errors:
        print(f"\n{len(errors)} Problem(e) gefunden:\n")
        for err in errors:
            print(f"   - {err}")
        return 1

    print(f"\nOK — {ARCHIVE.name} ist aktuell ({len(mapping)} Dateien im Paket).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
