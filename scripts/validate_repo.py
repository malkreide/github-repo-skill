#!/usr/bin/env python3
"""
validate_repo.py — Struktur- und Dokumentationsprüfung für ein Repo.

Meldet, ändert nichts. Auto-Fixes sind bewusst nicht implementiert:
bewusste Abweichungen (Selbstbezeichnung, präzisere Sektionstitel,
deutsche Synonyme) dürfen nicht "aufgeräumt" werden.

Aufruf:
    python3 validate_repo.py [REPO_PFAD]
    python3 validate_repo.py --json [REPO_PFAD]

Exit-Code: 0 = keine ERROR-Findings, 1 = mindestens ein ERROR.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# --- Sektions-Vokabular ------------------------------------------------------
# Schluss-Sektionen in verbindlicher Reihenfolge (C1).
CLOSING_EN = ["contributing", "security", "license", "author"]
CLOSING_DE = ["contributing", "security", "license", "author"]

# Erlaubte Überschriften je logischer Sektion. Exakter Vergleich (E3),
# ergänzt um bewusst präzisere Titel (D2) und deutsche Synonyme (D1/D3).
HEADINGS = {
    "en": {
        "contributing": {"contributing", "contributing & support"},
        "security": {"security", "security & compliance", "security and compliance",
                     "security & privacy", "security policy"},
        "license": {"license", "licence", "licenses", "licences",
                    "software licence", "software license",
                    "data licence", "data license", "license & data licence"},
        "author": {"author", "authors", "maintainer", "maintainers"},
    },
    "de": {
        "contributing": {"mitwirken", "mitmachen", "beitragen", "mitarbeit"},
        "security": {"sicherheit", "sicherheit & compliance", "sicherheit und compliance",
                     "sicherheit & datenschutz", "sicherheitsrichtlinie"},
        "license": {"lizenz", "lizenzen", "software-lizenz", "softwarelizenz",
                    "datenlizenz", "daten-lizenz", "lizenz & datenlizenz"},
        # D1: Selbstbezeichnungen sind keine Formatabweichung — alle Varianten gelten.
        "author": {"autor", "autorin", "autor·in", "autor:in", "autor*in",
                   "autor/in", "autorin / autor", "autor / autorin", "autoren"},
    },
}

# Englische Sektionstitel, die in einer deutschen Datei ein Fehler sind (C6).
# 'Changelog' und 'Installation' fehlen bewusst: beides sind im Deutschen
# gebräuchliche Titel, technische Begriffe bleiben englisch.
EN_ONLY_IN_DE = {"contributing", "security", "license", "licence", "author",
                 "overview", "features", "prerequisites", "usage",
                 "configuration", "project structure", "available tools"}

EMOJI_RE = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002190-\U000021FF" "\U00002300-\U000023FF"
    "\U000024C2-\U0001F251" "\U00002600-\U000027BF" "\U0000FE0F" "\U0001F1E6-\U0001F1FF"
    "]"
)
MARKER_RE = re.compile(r"<!--\s*mcp-name:\s*([^\s>]+)\s*-->")
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
HTML_IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)
BADGE_HOSTS = ("shields.io", "badge.fury.io", "badgen.net", "codecov.io",
               "github.com/.*/workflows/.*badge", "img.shields.io")
ANCHOR_LINK_RE = re.compile(r"\]\(#([^)]+)\)")
BOLD_AUTHOR_RE = re.compile(r"^\*\*(author|autor|autorin|autor·in|maintainer)[^*]*\*\*\s*$",
                            re.IGNORECASE | re.MULTILINE)


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, level: str, rule: str, msg: str) -> None:
        self.items.append({"level": level, "rule": rule, "message": msg})

    error = lambda self, rule, msg: self.add("ERROR", rule, msg)      # noqa: E731
    warn = lambda self, rule, msg: self.add("WARN", rule, msg)        # noqa: E731
    info = lambda self, rule, msg: self.add("INFO", rule, msg)        # noqa: E731

    @property
    def failed(self) -> bool:
        return any(i["level"] == "ERROR" for i in self.items)


def strip_code_fences(text: str) -> str:
    """Entfernt ```-Blöcke, damit Kommentare im Code nicht als Überschrift zählen."""
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        out.append("" if fence else line)
    return "\n".join(out)


def headings(text: str) -> list[tuple[int, str]]:
    """(Ebene, Roh-Titel) für alle ATX-Überschriften ausserhalb von Code-Blöcken."""
    res = []
    for line in strip_code_fences(text).splitlines():
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", line)
        if m:
            res.append((len(m.group(1)), m.group(2).strip()))
    return res


def normalise(title: str) -> str:
    """Kleinschreibung ohne Emoji und Randzeichen — für den EXAKTEN Vergleich (E3)."""
    return EMOJI_RE.sub("", title).strip().strip("#").strip().lower()


def classify(title: str, lang: str) -> str | None:
    n = normalise(title)
    for key, variants in HEADINGS[lang].items():
        if n in variants:
            return key
    if lang == "de":
        # Englischer Titel in deutscher Datei: für die Reihenfolgeprüfung
        # trotzdem zuordnen — als Fehler meldet ihn separat C6.
        for key, variants in HEADINGS["en"].items():
            if n in variants:
                return key
    return None


def images(text: str) -> list[str]:
    """Bilder in BEIDEN Syntaxformen, Badges herausgefiltert (E2)."""
    found = MD_IMG_RE.findall(text) + HTML_IMG_RE.findall(text)
    return [s for s in found if not any(re.search(h, s) for h in BADGE_HOSTS)]


def check_readme(path: Path, lang: str, repo: Path, rep: Report) -> None:
    if not path.exists():
        rep.error("C1", f"{path.name} fehlt")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    hs = headings(text)

    # C1 — Reihenfolge der Schluss-Sektionen
    order = [classify(t, lang) for _, t in hs]
    order = [o for o in order if o]
    expected = CLOSING_EN if lang == "en" else CLOSING_DE
    present = [o for o in order if o in expected]
    for want in expected:
        if want not in present:
            level = "WARN" if want == "contributing" else "ERROR"
            rep.add(level, "C1", f"{path.name}: Sektion '{want}' fehlt")
    dedup = list(dict.fromkeys(present))
    ranked = [expected.index(o) for o in dedup]
    if ranked != sorted(ranked):
        rep.error("C1", f"{path.name}: Schluss-Sektionen in falscher Reihenfolge: {dedup}")

    # C3 — Author als Überschrift, nicht als Fettdruck
    if BOLD_AUTHOR_RE.search(strip_code_fences(text)):
        rep.error("C3", f"{path.name}: Author/Autor als Fettdruck statt als Überschrift")

    # C5 + E4 — Emoji in Überschriften, mit Anker-Warnung
    anchors = set(ANCHOR_LINK_RE.findall(text))
    for lvl, title in hs:
        if EMOJI_RE.search(title):
            hint = ""
            slug = re.sub(r"[^a-z0-9\- ]", "", title.lower()).strip().replace(" ", "-")
            if any(slug in a or a in slug for a in anchors):
                hint = "  → ACHTUNG: Anker-Link zeigt auf diese Überschrift (E4)"
            rep.warn("C5", f"{path.name}: Emoji in Überschrift '{title}'{hint}")

    # C6 — englische Überschrift in deutscher Datei
    if lang == "de":
        for _, title in hs:
            if normalise(title) in EN_ONLY_IN_DE:
                rep.error("C6", f"{path.name}: englische Überschrift '{title}' in deutscher Datei")

    # C2 — vorhandene Dokumente müssen verlinkt sein
    for doc in ("SECURITY.md", "CONTRIBUTING.md"):
        if (repo / doc).exists() and doc not in text:
            rep.error("C2", f"{path.name}: {doc} existiert, wird aber nicht verlinkt")

    # Sprachumschalter
    other = "README.de.md" if lang == "en" else "README.md"
    if other not in text:
        rep.error("C1", f"{path.name}: Link auf {other} fehlt")

    # C4 — referenzierte Bilder müssen existieren
    for src in images(text):
        if src.startswith(("http://", "https://", "data:")):
            continue
        if not (repo / src.split("#")[0]).exists():
            rep.error("C4", f"{path.name}: Bild '{src}' referenziert, Datei fehlt")

    if lang == "de" and "ß" in text:
        rep.error("DE", f"{path.name}: 'ß' gefunden — Schweizer Rechtschreibung verwendet 'ss'")


def check_demo_parity(repo: Path, rep: Report) -> None:
    """C4 — Demo in beiden Sprachfassungen oder in keiner."""
    en, de = repo / "README.md", repo / "README.de.md"
    if not (en.exists() and de.exists()):
        return
    has = {}
    for p in (en, de):
        t = p.read_text(encoding="utf-8", errors="replace")
        has[p.name] = bool(images(t)) or any(
            normalise(x) == "demo" for _, x in headings(t))
    if has["README.md"] != has["README.de.md"]:
        missing = [k for k, v in has.items() if not v]
        rep.error("C4", f"Demo/Bild nur in einer Sprachfassung — fehlt in {missing[0]}")


def check_mcp_marker(repo: Path, rep: Report) -> None:
    """A1 — mcp-name-Marker in der Datei, die pyproject als readme deklariert."""
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return
    raw = pyproject.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'^\s*readme\s*=\s*["\']([^"\']+)["\']', raw, re.MULTILINE)
    readme_name = m.group(1) if m else "README.md"
    target = repo / readme_name
    if not target.exists():
        rep.error("A1", f"pyproject deklariert readme = {readme_name}, Datei fehlt")
        return
    markers = MARKER_RE.findall(target.read_text(encoding="utf-8", errors="replace"))
    rep.info("A1", f"mcp-name-Marker in {readme_name}: {len(markers)} → {markers}")
    if not markers:
        rep.error("A1", f"{readme_name} hat keinen <!-- mcp-name: ... --> Marker. "
                        "PyPI-Releases sind unveränderlich — vor dem Release ergänzen.")
    elif len(markers) > 1:
        rep.warn("A1", f"{readme_name} hat {len(markers)} Marker — genau einer erwartet")

    sj = repo / "server.json"
    if sj.exists() and markers:
        try:
            name = json.loads(sj.read_text(encoding="utf-8")).get("name", "")
            if name and name != markers[0]:
                rep.error("A1", f"Marker '{markers[0]}' ≠ server.json name '{name}'")
        except json.JSONDecodeError as exc:
            rep.error("A2", f"server.json nicht parsebar: {exc}")


def check_server_json(repo: Path, rep: Report) -> None:
    """A2 — Registry lehnt description > 100 Zeichen mit 422 ab."""
    sj = repo / "server.json"
    if not sj.exists():
        return
    try:
        data = json.loads(sj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rep.error("A2", f"server.json nicht parsebar: {exc}")
        return
    desc = data.get("description", "")
    if len(desc) > 100:
        rep.error("A2", f"server.json description ist {len(desc)} Zeichen "
                        f"(max. 100) — Registry antwortet sonst mit 422")
    else:
        rep.info("A2", f"server.json description: {len(desc)}/100 Zeichen")

    pyproject = repo / "pyproject.toml"
    if pyproject.exists() and data.get("version"):
        raw = pyproject.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'^\s*version\s*=\s*["\']([^"\']+)["\']', raw, re.MULTILINE)
        if m and m.group(1) != data["version"]:
            rep.error("A4", f"Versionsdrift: pyproject {m.group(1)} ≠ "
                            f"server.json {data['version']}")


def check_ruff_config(repo: Path, rep: Report) -> None:
    """B1/B2 — jeder pyproject-Block braucht einen eigenen expliziten select."""
    for py in sorted(repo.rglob("pyproject.toml")):
        if any(part in {".venv", "venv", "node_modules", ".git"} for part in py.parts):
            continue
        raw = py.read_text(encoding="utf-8", errors="replace")
        rel = py.relative_to(repo)
        if "[tool.ruff" in raw or "ruff" in raw:
            if not re.search(r"\[tool\.ruff\.lint\][^\[]*select\s*=", raw, re.DOTALL):
                rep.error("B1", f"{rel}: kein expliziter [tool.ruff.lint] select — "
                                "CI wird bei ruff-Updates ohne Codeänderung rot")
        if re.search(r'ruff\s*>=\s*[\d.]+["\']', raw) and "<" not in raw.split("ruff")[1][:40]:
            rep.warn("B1", f"{rel}: ruff ohne Obergrenze gepinnt")


def check_blind_assertions(repo: Path, rep: Report) -> None:
    """B3 — pytest.raises(Exception) besteht auch bei einem Tippfehler."""
    for py in sorted(repo.rglob("test_*.py")) + sorted(repo.rglob("*_test.py")):
        raw = py.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(raw.splitlines(), 1):
            if re.search(r"pytest\.raises\(\s*(Exception|BaseException)\s*[),]", line):
                rep.error("B3", f"{py.relative_to(repo)}:{n}: blinde Assertion "
                                "pytest.raises(Exception) — konkrete Exception verwenden")


def list_tool_names(repo: Path, rep: Report) -> None:
    """E1 — registrierte Namen ausgeben, nicht die Funktionsnamen."""
    registered: list[str] = []
    for py in sorted(repo.rglob("*.py")):
        if any(p in {".venv", "venv", "build", "dist"} for p in py.parts):
            continue
        raw = py.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"@\w+\.tool\(([^)]*)\)\s*\n\s*(?:async\s+)?def\s+(\w+)",
                             raw, re.MULTILINE):
            args, func = m.group(1), m.group(2)
            explicit = re.search(r'name\s*=\s*["\']([^"\']+)["\']', args)
            registered.append(explicit.group(1) if explicit else func)
    if registered:
        rep.info("E1", f"Registrierte Tool-Namen ({len(registered)}): {sorted(registered)}")
        readme = repo / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8", errors="replace")
            missing = [t for t in registered if t not in text]
            if missing:
                rep.warn("E1", f"Tools nicht im README dokumentiert: {missing}")


def check_license_name(repo: Path, rep: Report) -> None:
    """C7 — LICENSE nennt den bürgerlichen Namen, nicht den GitHub-Handle."""
    lic = repo / "LICENSE"
    if not lic.exists():
        rep.error("C7", "LICENSE fehlt")
        return
    handle = git(repo, "config", "--get", "remote.origin.url") or ""
    m = re.search(r"[:/]([^/]+)/[^/]+?(?:\.git)?$", handle)
    if m:
        owner = m.group(1)
        for line in lic.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("copyright") and owner.lower() in line.lower():
                rep.warn("C7", f"LICENSE nennt vermutlich den GitHub-Handle '{owner}' — "
                               "bürgerlichen Namen verwenden")


def git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def check_branch(repo: Path, rep: Report) -> None:
    """E5 — der Default-Branch ist nicht immer main."""
    head = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    branch = head.rsplit("/", 1)[-1] if head else git(repo, "branch", "--show-current")
    if branch:
        rep.info("E5", f"Default-Branch: {branch}")
        if branch != "main":
            rep.warn("E5", f"Default-Branch ist '{branch}', nicht 'main' — "
                           "Push- und Workflow-Befehle anpassen")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    repo = Path(args[0] if args else ".").resolve()
    rep = Report()

    check_readme(repo / "README.md", "en", repo, rep)
    check_readme(repo / "README.de.md", "de", repo, rep)
    check_demo_parity(repo, rep)
    check_mcp_marker(repo, rep)
    check_server_json(repo, rep)
    check_ruff_config(repo, rep)
    check_blind_assertions(repo, rep)
    list_tool_names(repo, rep)
    check_license_name(repo, rep)
    check_branch(repo, rep)

    if as_json:
        print(json.dumps(rep.items, ensure_ascii=False, indent=2))
    else:
        icons = {"ERROR": "✗", "WARN": "!", "INFO": "·"}
        for level in ("ERROR", "WARN", "INFO"):
            for item in [i for i in rep.items if i["level"] == level]:
                print(f"{icons[level]} [{item['rule']}] {item['message']}")
        n_err = sum(1 for i in rep.items if i["level"] == "ERROR")
        n_warn = sum(1 for i in rep.items if i["level"] == "WARN")
        print(f"\n{repo.name}: {n_err} ERROR, {n_warn} WARN")
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
