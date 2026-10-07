#!/usr/bin/env python3
"""Regressionstests für den A1-Check (mcp-name-Marker) aus validate_repo.py.

Hintergrund: A1 verlangte den Marker bei jedem Repo mit `pyproject.toml` und
meldete deshalb eine reine Python-Bibliothek (personakit) mit ERROR — ein
Fehlalarm, der das Release-Gate blockiert. Der Marker ist MCP-spezifisch.

Die Prüfung hat zwei Seiten, und beide sind einzeln verletzbar:

* Sie darf **Nicht-MCP-Repos nicht blockieren**: ohne `server.json` und mit
  `project_type` ≠ `mcp-server` in `repo-meta.yml` kein ERROR (Fälle 1, 2).
* Sie darf **MCP-Server nicht durchlassen**: `server.json` oder
  `project_type: mcp-server` erzwingen den Marker weiterhin, und ohne
  `repo-meta.yml` bleibt die Prüfung aktiv (Fälle 3–6).

Fall 4 ist der schärfste: `project_type` sagt `python-lib`, aber ein
`server.json` liegt im Repo. Eine Ausnahme, die nur das Intake-Feld liest,
besteht alle anderen Fälle und fällt nur hier durch.

Läuft mit pytest und ohne:

    python3 scripts/test_a1.py
    pytest scripts/test_a1.py
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_validator():
    spec = importlib.util.spec_from_file_location("vr", HERE / "validate_repo.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vr"] = mod
    spec.loader.exec_module(mod)
    return mod


vr = _load_validator()

PYPROJECT = '[project]\nname = "x"\nreadme = "README.md"\n'
MARKER = "<!-- mcp-name: io.github.u/x -->\n"


def a1_errors(
    meta: str | None, server_json: bool, marker: bool
) -> tuple[list[str], list[str]]:
    """(ERROR-, INFO-Meldungen) von A1 für ein Wegwerf-Repo."""
    d = Path(tempfile.mkdtemp())
    try:
        (d / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
        readme = (MARKER if marker else "") + "# x\n"
        (d / "README.md").write_text(readme, encoding="utf-8")
        if meta is not None:
            (d / ".github").mkdir()
            (d / ".github" / "repo-meta.yml").write_text(meta, encoding="utf-8")
        if server_json:
            (d / "server.json").write_text('{"name": "io.github.u/x"}', "utf-8")
        rep = vr.Report()
        vr.check_mcp_marker(d, rep)
        a1 = [i for i in rep.items if i["rule"] == "A1"]
        return (
            [i["message"] for i in a1 if i["level"] == "ERROR"],
            [i["message"] for i in a1 if i["level"] == "INFO"],
        )
    finally:
        shutil.rmtree(d, ignore_errors=True)


# (Name, repo-meta.yml oder None, server.json?, Marker?, ERROR erwartet?)
CASES = [
    ("1 python-lib ohne Marker", "project_type: python-lib\n", False, False, False),
    (
        "2 Wert mit Anführungszeichen und Kommentar",
        'project_type: "claude-skill"   # Intake\n',
        False,
        False,
        False,
    ),
    ("3 mcp-server ohne Marker", "project_type: mcp-server\n", False, False, True),
    ("4 python-lib, aber server.json", "project_type: python-lib\n", True, False, True),
    ("5 ohne repo-meta.yml", None, False, False, True),
    ("6 repo-meta.yml ohne project_type", "repo_name: x\n", False, False, True),
    ("7 mcp-server mit Marker", "project_type: mcp-server\n", False, True, False),
]


def test_a1_marker_only_for_mcp():
    bad = []
    for name, meta, sj, marker, want in CASES:
        errors, _ = a1_errors(meta, sj, marker)
        if bool(errors) != want:
            bad.append(
                f"{name}: erwartet {'ERROR' if want else 'sauber'}, "
                f"bekommen {errors or 'sauber'}"
            )
    assert not bad, "A1:\n  " + "\n  ".join(bad)


def test_a1_skip_is_reported():
    """Die Ausnahme ist sichtbar, nicht still — sonst fehlt im Bericht, warum."""
    _, info = a1_errors("project_type: python-lib\n", False, False)
    assert any("kein MCP-Server" in m for m in info), info


def main() -> int:
    failed = 0
    for fn in (test_a1_marker_only_for_mcp, test_a1_skip_is_reported):
        try:
            fn()
            print(f"✓ {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"✗ {fn.__name__}\n  {exc}")
    total = len(CASES) + 1
    print(
        f"\n{total} Fälle, {'alle grün' if not failed else f'{failed} Gruppe(n) rot'}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
