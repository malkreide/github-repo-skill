---
name: github-repo
description: Erstelle und pflege professionelle GitHub Repositories für technische Projekte (MCP-Server, Claude SKILLs, Raspberry Pi, Python, etc.). Verwende diesen Skill immer wenn der User (1) ein neues GitHub Repo erstellen oder publizieren möchte, (2) README-Dateien auf Englisch und Deutsch benötigt, (3) Repo-Metadaten (Name, Description, Topics/Tags) definieren will, (4) Standard-Dateien (LICENSE, .gitignore, CHANGELOG) generieren lassen möchte, (5) ein bestehendes Repo nach neuen Commits aktualisieren will, (6) einen Release mit Versionsnummer erstellen möchte, (7) den gh-CLI-Workflow für GitHub-Operationen nutzen will. Auch wenn der User fragt "Wie stelle ich das auf GitHub?", "Kannst du das GitHub-ready machen?" oder ähnliches — dann diesen Skill verwenden.
---

# GitHub Repo Skill

Erstellt vollständige, professionelle GitHub Repositories mit bilingualem README (EN/DE), Standard-Dateien und `gh`-CLI-Workflow.

---

## Schritt 1: Projekttyp und Metadaten bestimmen

Erkenne den Projekttyp aus dem Kontext oder frage nach:

| Typ | Erkennungsmerkmale |
|---|---|
| `mcp-server` | MCP, Model Context Protocol, Tools für LLMs |
| `claude-skill` | SKILL.md, Claude Skills, Prompting-Framework |
| `raspberry-pi` | Pi, GPIO, Edge AI, Hailo, Sensor |
| `python-lib` | Python-Package, Library, Module |
| `other` | Alles andere |

**Repo-Metadaten generieren** (falls nicht angegeben):

- **Name**: `kebab-case`, präzise, kein "my-" Präfix
  - MCP: `{service}-mcp` (z.B. `fedlex-mcp`, `swiss-transport-mcp`)
  - Skill: `{name}-skill` (z.B. `github-repo-skill`)
  - Pi: `{function}-pi` (z.B. `classroom-sensor-pi`)
- **Description**: Max. 100 Zeichen, Englisch, ohne Punkt am Ende
- **Topics/Tags**: 5–8 Stück, lowercase, relevant für Auffindbarkeit
  - Immer dabei: Projekttyp-Tag + Sprachtag (z.B. `python`, `typescript`)
  - Für MCP: `mcp`, `model-context-protocol`, `llm`
  - Für Skill: `claude`, `anthropic`, `prompt-engineering`
  - Für Pi: `raspberry-pi`, `edge-ai`, `iot`
  - Spezifische Tags: Thema/Domain (z.B. `swiss-open-data`, `education`)

---

## Schritt 2: Dateistruktur erstellen

### Pflichtdateien (immer)

```
repo-name/
├── README.md           ← Englisch (Hauptdatei)
├── README.de.md        ← Deutsch (verlinkt mit README.md)
├── LICENSE             ← MIT (Standard) oder nach Vorgabe
├── .gitignore          ← Projekttyp-spezifisch
└── CHANGELOG.md        ← Versionsverlauf
```

### Optionale Dateien (nach Bedarf)

```
├── CONTRIBUTING.md     ← Falls externe Beiträge erwünscht
├── .github/
│   └── ISSUE_TEMPLATE/ ← Falls Issue-Tracking gewünscht
└── docs/               ← Erweiterte Dokumentation
```

---

## Schritt 3: README.md (Englisch) erstellen

**Struktur – verpflichtend in dieser Reihenfolge:**

```markdown
# {Repo Name}

{Badges: Version | License | Last Commit | Language}

> {One-liner description — max. 1 Satz}

[🇩🇪 Deutsche Version](README.de.md)

## Overview

{Was macht das Projekt? Warum existiert es? 2–4 Sätze}

## Features

- Feature 1
- Feature 2

## Prerequisites

{Was muss installiert/vorhanden sein?}
- Item 1 (Version X+)
- Item 2

## Installation

\`\`\`bash
{Konkrete Installationsbefehle}
\`\`\`

## Usage / Quickstart

\`\`\`bash
{Minimales Beispiel das sofort funktioniert}
\`\`\`

## Configuration

{Falls vorhanden: Umgebungsvariablen, Config-Files}

## Project Structure

\`\`\`
{Verzeichnisstruktur mit Kommentaren}
\`\`\`

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## License

MIT License — see [LICENSE](LICENSE)

## Author

{Name} · [{GitHub}](https://github.com/{username})
```

**Badges-Vorlage:**
```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)
```

---

## Schritt 4: README.de.md (Deutsch) erstellen

**Identische Struktur wie README.md**, aber:
- Alle Texte auf Deutsch (Schweizer Rechtschreibung: kein ß → ss)
- Header-Zeile am Anfang:

```markdown
[🇬🇧 English Version](README.md)
```

- Technische Begriffe, Befehle, Code-Blöcke bleiben auf Englisch
- Sektionen-Titel können eingedeutscht werden:
  - Overview → Übersicht
  - Features → Funktionen
  - Prerequisites → Voraussetzungen
  - Installation → Installation (gleich)
  - Usage → Verwendung
  - Configuration → Konfiguration
  - Project Structure → Projektstruktur

---

## Schritt 5: LICENSE erstellen

**MIT License (Standard):**

```
MIT License

Copyright (c) {YEAR} {AUTHOR_NAME}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Schritt 6: .gitignore erstellen

Wähle nach Projekttyp:

**Python / MCP-Server:**
```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.env
.venv/
venv/
*.log
.DS_Store
```

**Node.js / TypeScript:**
```
node_modules/
dist/
.env
*.log
.DS_Store
```

**Raspberry Pi (Python-basiert):**
```
__pycache__/
*.py[cod]
.env
*.log
.DS_Store
/data/
/logs/
*.sqlite
```

**Claude SKILL:**
```
.DS_Store
*.log
/tmp/
```

---

## Schritt 7: CHANGELOG.md erstellen

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - {YYYY-MM-DD}

### Added
- Initial release
- {Feature 1}
- {Feature 2}
```

**Semantic Versioning Konvention:**
- `MAJOR.MINOR.PATCH`
- PATCH (1.0.**1**): Bugfixes, keine neuen Features
- MINOR (1.**1**.0): Neue Features, rückwärtskompatibel
- MAJOR (**2**.0.0): Breaking Changes

---

## Schritt 8: gh CLI — Repo erstellen und konfigurieren

### Voraussetzungen prüfen
```bash
# gh installiert?
gh --version

# Eingeloggt?
gh auth status

# Falls nicht: Login
gh auth login
```

### Neues Repo erstellen

```bash
# Lokal: Git initialisieren (falls noch nicht)
cd /pfad/zu/projekt
git init
git add .
git commit -m "Initial commit: {kurze Beschreibung}"

# Repo auf GitHub erstellen und pushen
gh repo create {repo-name} \
  --public \
  --description "{Description max. 100 Zeichen}" \
  --source=. \
  --remote=origin \
  --push

# Alternativ: Privates Repo
gh repo create {repo-name} \
  --private \
  --description "{Description}" \
  --source=. \
  --remote=origin \
  --push
```

### Topics/Tags setzen (nach Repo-Erstellung)

```bash
gh repo edit {username}/{repo-name} \
  --add-topic {topic1} \
  --add-topic {topic2} \
  --add-topic {topic3}

# Beispiel MCP-Server:
gh repo edit malkreide/fedlex-mcp \
  --add-topic mcp \
  --add-topic model-context-protocol \
  --add-topic swiss-open-data \
  --add-topic python \
  --add-topic llm
```

### Repo-Details anzeigen
```bash
gh repo view {username}/{repo-name}
```

---

## Schritt 9: Update-Workflow nach Commits

**Standard-Commit-Ablauf:**

```bash
# 1. Änderungen hinzufügen
git add .

# 2. Commit mit konventioneller Nachricht
git commit -m "{type}: {kurze Beschreibung}"

# 3. Pushen
git push origin main
```

**Conventional Commits — Typen:**
| Typ | Verwendung |
|---|---|
| `feat` | Neues Feature |
| `fix` | Bugfix |
| `docs` | Nur Dokumentation |
| `refactor` | Code-Umstrukturierung |
| `test` | Tests hinzufügen/ändern |
| `chore` | Build, Abhängigkeiten, Konfiguration |

**Nach jedem relevanten Commit:**
1. `CHANGELOG.md` → Eintrag unter `[Unreleased]` hinzufügen
2. README aktualisieren falls Funktionen/Struktur geändert
3. Badge-Versionsnummer ggf. anpassen

---

## Schritt 10: Release erstellen

```bash
# 1. CHANGELOG: [Unreleased] → [1.x.x] - DATUM umbenennen
# (manuell oder mit sed)

# 2. Git Tag erstellen und pushen
git tag -a v1.0.0 -m "Release v1.0.0: {kurze Beschreibung}"
git push origin v1.0.0

# 3. GitHub Release erstellen (aus CHANGELOG generieren)
gh release create v1.0.0 \
  --title "v1.0.0 — {Release-Titel}" \
  --notes-file CHANGELOG.md \
  --latest

# 4. Badge in README aktualisieren
# version-1.0.0 → version-1.1.0
```

---

## Qualitätscheckliste

Vor dem ersten Push / vor einem Release prüfen:

**README.md (EN)**
- [ ] Alle Pflichtabschnitte vorhanden
- [ ] Badges korrekt (Version, License)
- [ ] Link zu README.de.md funktioniert
- [ ] Installation-Befehl getestet / plausibel
- [ ] Quickstart-Beispiel vorhanden

**README.de.md**
- [ ] Link zu README.md funktioniert
- [ ] Alle Sektionen übersetzt
- [ ] Schweizer Rechtschreibung (kein ß)

**Repo-Metadaten**
- [ ] Description gesetzt (max. 100 Zeichen, Englisch)
- [ ] Topics/Tags gesetzt (5–8 Stück)
- [ ] LICENSE vorhanden
- [ ] .gitignore passend zum Projekttyp

**Versionierung**
- [ ] CHANGELOG.md vollständig
- [ ] Semantic Versioning eingehalten
- [ ] Git Tag entspricht CHANGELOG-Version

---

## Schnellreferenz: Häufige gh-Befehle

```bash
# Repo anzeigen
gh repo view

# Topics anzeigen/bearbeiten
gh repo edit --add-topic {topic}
gh repo edit --remove-topic {topic}

# Alle eigenen Repos auflisten
gh repo list

# Repo klonen
gh repo clone {username}/{repo-name}

# Issue erstellen
gh issue create --title "{Titel}" --body "{Beschreibung}"

# Pull Request erstellen
gh pr create --title "{Titel}" --body "{Beschreibung}"

# Release auflisten
gh release list

# Letzten Release anzeigen
gh release view
```
