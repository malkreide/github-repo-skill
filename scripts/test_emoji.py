#!/usr/bin/env python3
"""Regressionstests für die Emoji-Erkennung (C5) aus validate_repo.py.

Hintergrund: siehe Regel E7 in `references/review-rules.md`. Die Prüfung hat
zwei Seiten, und beide sind einzeln verletzbar:

* Sie darf **Typografie nicht als Emoji melden**. Die frühere Fassung nahm den
  kompletten Pfeilblock U+2190–U+21FF und meldete deshalb `Zefix ↔ Amtsblatt`.
* Sie muss **echte Emoji weiterhin finden** — auch die, die ohne
  Variantenselektor auskommen (`⚡`, `✨`).

Der Unterschied ist Unicodes Emoji_Presentation: Zeichen mit
Emoji-Standarddarstellung zählen allein, Zeichen mit Textdarstellung erst mit
VS16 (U+FE0F). Genau an dieser Grenze verlief der Fehlalarm.

Läuft mit pytest und ohne:

    python3 scripts/test_emoji.py
    pytest scripts/test_emoji.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_validator():
    spec = importlib.util.spec_from_file_location("vr", HERE / "validate_repo.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vr"] = mod
    spec.loader.exec_module(mod)
    return mod


vr = _load_validator()

# --- Muss SAUBER bleiben -----------------------------------------------------
# Alle diese Zeichen kommen in Überschriften des Portfolios vor oder sind die
# Umlaute, vor deren Verlust E4 warnt.
NOT_EMOJI = [
    ("–", "EN DASH"),
    ("—", "EM DASH — 66× in Portfolio-Überschriften"),
    ("→", "RIGHTWARDS ARROW"),
    ("↔", "LEFT RIGHT ARROW — der ursprüngliche Fehlalarm (register-mcp)"),
    ("·", "MIDDLE DOT — steht in `Autor·in` (D1)"),
    ("ä", "Umlaut"),
    ("ö", "Umlaut"),
    ("ü", "Umlaut"),
    ("Ü", "Umlaut gross"),
    ("ç", "Cedille"),
    ("«", "Guillemet"),
    ("…", "HORIZONTAL ELLIPSIS"),
    ("✓", "CHECK MARK — Textdarstellung, kommt in Tabellen vor"),
    ("✗", "BALLOT X — dito"),
    ("⌘", "PLACE OF INTEREST SIGN"),
    ("Ⓜ", "CIRCLED M ohne VS16"),
    # Regression für den entfernten Bereich U+24C2–U+1F251: der verschluckte
    # nebenbei den gesamten CJK-Block.
    ("漢", "CJK-Ideogramm"),
    ("字", "CJK-Ideogramm"),
    ("あ", "Hiragana"),
    ("한", "Hangul"),
]

# --- Muss GREIFEN ------------------------------------------------------------
IS_EMOJI = [
    # Emoji_Presentation=Yes — stehen im Portfolio nachweislich ohne Selektor.
    ("⚡", "HIGH VOLTAGE, nackt — swiss-energy-mcp"),
    ("✨", "SPARKLES, nackt — zurich-opendata-mcp"),
    ("⭐", "STAR"),
    ("✅", "CHECK MARK BUTTON"),
    ("❌", "CROSS MARK"),
    ("⌚", "WATCH"),
    ("☕", "HOT BEVERAGE"),
    ("⚽", "SOCCER BALL"),
    # Textdarstellung + VS16 — im Portfolio ausnahmslos so geschrieben.
    ("⚖️", "SCALES + VS16 — openlex-mcp"),
    ("⚙️", "GEAR + VS16"),
    ("⛰️", "MOUNTAIN + VS16"),
    ("✈️", "AIRPLANE + VS16"),
    ("❄️", "SNOWFLAKE + VS16"),
    ("↔️", "derselbe Pfeil MIT Selektor ist sehr wohl ein Emoji"),
    # Pictograph-Ebenen.
    ("🗺️", "WORLD MAP — swisstopo-mcp"),
    ("🏛️", "CLASSICAL BUILDING — register-mcp"),
    ("🛡️", "SHIELD"),
    ("💼", "BRIEFCASE — seco-labor-mcp"),
    ("📰", "NEWSPAPER"),
    ("🎯", "DIRECT HIT"),
    ("🇨🇭", "Flagge (Regional Indicators)"),
]

# --- normalise() darf keine unsichtbaren Reste hinterlassen ------------------
# Sonst scheitert der Titelvergleich (E3) an einem Zeichen, das man nicht sieht.
NORMALISE = [
    ("🗺️ swisstopo-mcp", "swisstopo-mcp"),
    ("⚖️ openlex-mcp", "openlex-mcp"),
    ("🛡️ Safety & Limits", "safety & limits"),
    ("📰 amtsblatt-mcp", "amtsblatt-mcp"),
    # Typografie bleibt erhalten — sie gehört zum Titel.
    ("The UID join — Zefix ↔ Amtsblatt", "the uid join — zefix ↔ amtsblatt"),
    ("Verfügbare Tools", "verfügbare tools"),
]


def test_typography_is_not_emoji():
    bad = [
        f"{c!r} ({why}) wurde als Emoji gemeldet"
        for c, why in NOT_EMOJI
        if vr.EMOJI_RE.search(c)
    ]
    assert not bad, "Fehlalarm:\n  " + "\n  ".join(bad)


def test_real_emoji_are_found():
    bad = [
        f"{c!r} ({why}) wurde NICHT erkannt"
        for c, why in IS_EMOJI
        if not vr.EMOJI_RE.search(c)
    ]
    assert not bad, "übersehen:\n  " + "\n  ".join(bad)


def test_normalise_leaves_no_invisible_remains():
    bad = []
    for title, want in NORMALISE:
        got = vr.normalise(title)
        if got != want:
            bad.append(f"{title!r} → {got!r}, erwartet {want!r}")
        stray = [hex(ord(c)) for c in got if ord(c) in (0xFE0F, 0xFE0E, 0x200D, 0x20E3)]
        if stray:
            bad.append(f"{title!r} → unsichtbarer Rest {stray}")
    assert not bad, "normalise:\n  " + "\n  ".join(bad)


def main() -> int:
    failed = 0
    for fn in (
        test_typography_is_not_emoji,
        test_real_emoji_are_found,
        test_normalise_leaves_no_invisible_remains,
    ):
        try:
            fn()
            print(f"✓ {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"✗ {fn.__name__}\n  {exc}")
    total = len(NOT_EMOJI) + len(IS_EMOJI) + len(NORMALISE)
    print(
        f"\n{total} Fälle, {'alle grün' if not failed else f'{failed} Gruppe(n) rot'}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
