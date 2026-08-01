#!/usr/bin/env python3
"""Regressionstests für den C1-Check (Schluss-Sektionen) aus validate_repo.py.

Hintergrund: siehe Regel E6 in `references/review-rules.md`. Ein
C1-Reihenfolgefehler bedeutet nicht, dass der Schlussblock falsch sortiert ist —
in allen drei real aufgetretenen Fällen war er korrekt, und gemeldet wurde eine
gleich klassifizierte Sektion weiter oben. Die Prüfung filtert deshalb auf die
flachste Ebene und lässt bei Mehrfachnennung die letzte gewinnen.

Diese Datei hält beide Hälften fest, denn beide sind einzeln verletzbar:

* Die Filter dürfen die **Fehlmeldungen** beseitigen (Fälle 3–5, 7, 9).
* Sie dürfen dabei **echte** Fehler nicht verstecken (Fälle 1, 2, 6, 8, 10).

Fall 2 ist der schärfste: ein echt falsch sortierter Schlussblock *mit*
zusätzlichem Duplikat. Eine Last-Wins-Regel, die zu viel kollabiert, besteht
alle anderen Fälle und fällt nur hier durch.

Läuft mit pytest und ohne:

    python scripts/test_c1.py
    pytest scripts/test_c1.py
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


def _findings(md: str, lang: str) -> list[str]:
    """C1-Meldungen für ein README-Fragment, in einem Wegwerf-Verzeichnis."""
    d = Path(tempfile.mkdtemp())
    try:
        name = "README.md" if lang == "en" else "README.de.md"
        (d / name).write_text(md, encoding="utf-8")
        rep = vr.Report()
        vr.check_readme(d / name, lang, d, rep)
        return [i["message"] for i in rep.items if i["rule"] == "C1"]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def misordered(md: str, lang: str = "en") -> bool:
    return any("Reihenfolge" in m for m in _findings(md, lang))


def missing(md: str, lang: str = "en") -> list[str]:
    """Nur die 'Sektion X fehlt'-Meldungen — nicht der Sprachumschalter-Link."""
    return [m for m in _findings(md, lang) if "Sektion '" in m]


# --- Reihenfolge -------------------------------------------------------------
# (Name, Sprache, erwartet_Fehler, Markdown)
ORDER_CASES = [
    # Echte Fehler: der Schlussblock selbst ist falsch sortiert.
    ("echt falsch sortiert (Security vor Contributing)", "en", True,
     "# t\n## Security\nx\n## Contributing\nx\n## License\nx\n## Author\nx\n"),
    # Der schärfste Fall: Duplikat UND falsch sortierter Schlussblock. Last-Wins
    # darf den echten Fehler nicht mitkollabieren.
    ("Duplikat + Schlussblock echt falsch sortiert", "en", True,
     "# t\n## Data License\nx\n## Security\nx\n## Contributing\nx\n"
     "## License\nx\n## Author\nx\n"),
    ("Author vor License", "en", True,
     "# t\n## Contributing\nx\n## Security\nx\n## Author\nx\n## License\nx\n"),
    ("DE echt falsch sortiert", "de", True,
     "# t\n## Lizenz\nx\n## Mitwirken\nx\n## Sicherheit\nx\n## Autor\nx\n"),
    # Begründet, warum der Ebenenfilter nicht hart auf `##` steht: ein README mit
    # durchgehend tieferer Gliederung muss weiterhin geprüft werden.
    ("Schlussblock durchgehend h3, falsch sortiert", "en", True,
     "# t\n### Security\nx\n### Contributing\nx\n### License\nx\n### Author\nx\n"),

    # Fehlmeldungen: Schlussblock korrekt, Auslöser steht weiter oben.
    ("swisstopo-Muster: '## Security & Compliance' als Inhaltssektion", "en", False,
     "# t\n## Security & Compliance\nx\n## Contributing\nx\n## Security\nx\n"
     "## License\nx\n## Author\nx\n"),
    ("register-Muster: '### Security' als Unterpunkt", "en", False,
     "# t\n## Safety & Limits\nx\n### Security\nx\n## Contributing\nx\n"
     "## Security\nx\n## License\nx\n## Author\nx\n"),
    # Dieser Fall ist der einzige, der den EBENENFILTER isoliert absichert. Im
    # register-Muster oben verdrängt das spätere `## Security` den Unterpunkt
    # schon per Last-Wins — der Ebenenfilter wäre dort entfernbar, ohne dass ein
    # Test rot wird (per Mutationstest festgestellt). Erst ohne spätere
    # Dokumentsektion trägt der Unterpunkt die Klassifikation allein und würde
    # ungefiltert einen Reihenfolgefehler erfinden.
    ("'### Security' als Unterpunkt, ohne späteres '## Security'", "en", False,
     "# t\n## Safety & Limits\nx\n### Security\nx\n## Contributing\nx\n"
     "## License\nx\n## Author\nx\n"),
    ("seco-Muster: '## Data License' als Inhaltssektion", "en", False,
     "# t\n## Data License\nx\n## Contributing\nx\n## Security\nx\n"
     "## License\nx\n## Author\nx\n"),
    ("DE seco-Muster: '## Datenlizenz' vorne", "de", False,
     "# t\n## Datenlizenz\nx\n## Mitwirken\nx\n## Sicherheit\nx\n"
     "## Lizenz\nx\n## Autor\nx\n"),
    ("Schlussblock durchgehend h3, korrekt", "en", False,
     "# t\n### Contributing\nx\n### Security\nx\n### License\nx\n### Author\nx\n"),
    # D2: derselbe Titel ist als Schluss-Sektion völlig in Ordnung. Nicht der
    # Titel ist die Ursache, sondern die Doppelbelegung (news-monitor-mcp).
    ("D2: '## Security & Compliance' ALS Schluss-Sektion", "en", False,
     "# t\n## Contributing\nx\n## Security & Compliance\nx\n"
     "## License\nx\n## Author\nx\n"),
]

# --- Existenz ----------------------------------------------------------------
# Die Existenzprüfung ist bewusst ebenenblind: eine vorhandene Sektion als
# fehlend zu melden wäre schlimmer als eine tief verschachtelte durchzulassen.
EXIST_CASES = [
    ("h3-Schlussblock gilt als vorhanden", "en", 0,
     "# t\n### Contributing\nx\n### Security\nx\n### License\nx\n### Author\nx\n"),
    ("echt fehlende Sektionen werden gemeldet", "en", 2,
     "# t\n## Contributing\nx\n## License\nx\n"),  # security + author fehlen
]


def test_c1_order():
    bad = []
    for name, lang, want, md in ORDER_CASES:
        got = misordered(md, lang)
        if got != want:
            bad.append(f"{name}: erwartet {'ERROR' if want else 'sauber'}, "
                       f"bekommen {'ERROR' if got else 'sauber'}")
    assert not bad, "C1-Reihenfolge:\n  " + "\n  ".join(bad)


def test_c1_missing_is_level_blind():
    bad = []
    for name, lang, want_n, md in EXIST_CASES:
        got = missing(md, lang)
        if len(got) != want_n:
            bad.append(f"{name}: erwartet {want_n} 'fehlt'-Meldungen, "
                       f"bekommen {len(got)} → {got}")
    assert not bad, "C1-Existenz:\n  " + "\n  ".join(bad)


def main() -> int:
    failed = 0
    for fn in (test_c1_order, test_c1_missing_is_level_blind):
        try:
            fn()
            print(f"✓ {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"✗ {fn.__name__}\n  {exc}")
    total = len(ORDER_CASES) + len(EXIST_CASES)
    print(f"\n{total} Fälle, {'alle grün' if not failed else f'{failed} Gruppe(n) rot'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
