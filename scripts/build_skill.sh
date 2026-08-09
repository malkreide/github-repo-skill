#!/usr/bin/env bash
#
# Build-Skript für github-repo.skill
#
# Erzeugt aus den Quelldateien des Repositorys ein ZIP-Archiv, das sich in
# Claude Desktop und auf claude.ai unter Einstellungen → Skills hochladen
# lässt. Das Paket-Layout steht in skill-manifest.txt im Projekt-Root — dort
# und nur dort werden Dateien hinzugefügt oder umbenannt.
#
# Aufruf:  ./scripts/build_skill.sh
#
# Danach `python3 scripts/validate_skill.py` ausführen und das Ergebnis
# committen: die CI prüft, ob das eingecheckte Archiv zu den Quellen passt.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
SKILL_NAME="github-repo"
OUTPUT_FILE="$PROJECT_ROOT/${SKILL_NAME}.skill"
MANIFEST="$PROJECT_ROOT/skill-manifest.txt"

# Fester Zeitstempel für alle Archiv-Einträge, siehe ZIP-Schritt unten.
SOURCE_TIMESTAMP="202401010000.00"

echo "Building ${SKILL_NAME}.skill ..."
echo ""

if [ ! -f "$MANIFEST" ]; then
    echo "FEHLER: skill-manifest.txt fehlt in $PROJECT_ROOT" >&2
    exit 1
fi

if ! command -v zip >/dev/null 2>&1; then
    echo "FEHLER: 'zip' ist nicht installiert (Debian/Ubuntu: apt install zip)" >&2
    exit 1
fi

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/$SKILL_NAME"

echo "Dateien gemaess skill-manifest.txt kopieren:"
COUNT=0
while IFS= read -r raw || [ -n "$raw" ]; do
    line="${raw%%$'\r'}"
    case "$line" in
        ''|'#'*) continue ;;
    esac
    case "$line" in
        *'='*) ;;
        *)
            echo "FEHLER: Manifest-Zeile ohne '=': '$line'" >&2
            exit 1
            ;;
    esac

    target="${line%%=*}"
    source="${line#*=}"
    if [ -z "$target" ] || [ -z "$source" ]; then
        echo "FEHLER: leerer Ziel- oder Quellpfad in '$line'" >&2
        exit 1
    fi
    if [ ! -f "$PROJECT_ROOT/$source" ]; then
        echo "FEHLER: Quelldatei '$source' (-> $target) nicht gefunden" >&2
        exit 1
    fi

    mkdir -p "$(dirname "$BUILD_DIR/$SKILL_NAME/$target")"
    cp "$PROJECT_ROOT/$source" "$BUILD_DIR/$SKILL_NAME/$target"
    printf '   %s -> %s\n' "$source" "$target"
    COUNT=$((COUNT + 1))
done < "$MANIFEST"

if [ "$COUNT" -eq 0 ]; then
    echo "FEHLER: Manifest enthaelt keine Dateien" >&2
    exit 1
fi

if [ ! -f "$BUILD_DIR/$SKILL_NAME/SKILL.md" ]; then
    echo "FEHLER: Das Manifest muss SKILL.md enthalten" >&2
    exit 1
fi

# ZIP erzeugen.
#
# Der Build ist bit-identisch reproduzierbar: alle Eintraege bekommen einen
# festen Zeitstempel, -X unterdrueckt die zusaetzlichen Dateiattribute, und
# die Eintragsreihenfolge ist sortiert. Gleicher Inhalt ergibt damit immer
# dasselbe Archiv — nur so ist ein eingechecktes Archiv im Diff lesbar und in
# der CI ueberhaupt pruefbar.
echo ""
echo "Archiv erzeugen ..."
find "$BUILD_DIR" -exec touch -t "$SOURCE_TIMESTAMP" {} +
rm -f "$OUTPUT_FILE"
(cd "$BUILD_DIR" && find "$SKILL_NAME" -type f | LC_ALL=C sort | zip -X -q -@ "$OUTPUT_FILE")

rm -rf "$BUILD_DIR"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "FEHLER: Build fehlgeschlagen" >&2
    exit 1
fi

echo ""
echo "OK: $OUTPUT_FILE ($(du -h "$OUTPUT_FILE" | cut -f1), $COUNT Dateien)"
echo ""
echo "Paketinhalt:"
unzip -Z1 "$OUTPUT_FILE" | grep -v '/$' | sed 's/^/   /'
echo ""
echo "Installieren:"
echo "   Claude Desktop bzw. claude.ai -> Einstellungen -> Capabilities/Skills"
echo "   -> Skill hochladen -> $(basename "$OUTPUT_FILE") auswaehlen"
