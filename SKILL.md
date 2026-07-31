---
name: github-repo
description: Erstelle und pflege professionelle GitHub Repositories für technische Projekte (MCP-Server, Claude SKILLs, Raspberry Pi, Python, etc.). Verwende diesen Skill immer wenn der User (1) ein neues GitHub Repo erstellen oder publizieren möchte, (2) README-Dateien auf Englisch und Deutsch benötigt, (3) Repo-Metadaten (Name, Description, Topics/Tags) definieren will, (4) Standard-Dateien (LICENSE, .gitignore, CHANGELOG) generieren lassen möchte, (5) ein bestehendes Repo nach neuen Commits aktualisieren will, (6) einen Release mit Versionsnummer erstellen möchte, (7) den gh-CLI-Workflow für GitHub-Operationen nutzen will. Auch wenn der User fragt "Wie stelle ich das auf GitHub?", "Kannst du das GitHub-ready machen?" oder ähnliches — dann diesen Skill verwenden.
---

# GitHub Repo Skill

Erstellt vollständige, professionelle GitHub Repositories mit bilingualem README (EN/DE), Standard-Dateien und `gh`-CLI-Workflow.

---

## Schritt 0: Session-Intake — Metadaten einmal vollständig erfassen

**Regel: Titel, Description und Topics werden pro Projekt genau einmal erfragt — gebündelt, am Anfang, bevor irgendeine Datei geschrieben wird.** Nicht verstreut über die Session, nicht Feld für Feld, nicht in jedem Folgeschritt erneut.

### 0.1 Zuerst suchen, dann fragen

Nie nach etwas fragen, das bereits vorliegt. Quellen in dieser Reihenfolge prüfen:

| Prio | Quelle | Wie |
|---|---|---|
| 1 | Angaben des Users in dieser Session | Aus dem Verlauf übernehmen |
| 2 | `.github/repo-meta.yml` im Projekt | Datei lesen → alles bereits erfasst |
| 3 | Bestehendes GitHub-Repo | `gh repo view {user}/{repo} --json name,description,repositoryTopics,visibility` |
| 4 | Projektdateien | `pyproject.toml`, `package.json`, `SKILL.md`-Frontmatter, bestehendes README, `LICENSE` |
| 5 | Codebase | Projekttyp, Sprache und Zweck aus dem Code ableiten → Vorschlag bauen |

### 0.2 Intake-Block — alles in EINER Nachricht

Für jedes fehlende Feld einen **konkreten Vorschlag** liefern, damit der User nur bestätigt oder korrigiert. Keine offene Frage stellen, wo aus dem Code ein Vorschlag ableitbar ist.

| Feld | Pflicht | Default / Ableitung | Beispiel |
|---|---|---|---|
| `repo_name` | ja | Namenskonvention aus Schritt 1 | `fedlex-mcp` |
| `title` | ja | Repo-Name in Title Case | `Fedlex MCP Server` |
| `description` | ja | Aus Zweck des Codes, max. 100 Zeichen, EN, ohne Schlusspunkt | `MCP server for Swiss federal law data from Fedlex` |
| `topics` | ja | 5–8, Regeln aus Schritt 1 | `mcp, model-context-protocol, swiss-open-data, python, llm` |
| `project_type` | ja | Erkennung aus Schritt 1 | `mcp-server` |
| `visibility` | ja | `public` | `public` |
| `license` | nein | `MIT` | `MIT` |
| `author_name` | nein | Aus `git config user.name` | `malkreide` |
| `github_user` | nein | Aus `gh api user --jq .login` | `malkreide` |
| `language` | nein | Aus Projektdateien | `python` |
| `version` | nein | `1.0.0` bei Erstrelease | `1.0.0` |

**Fragestil:**
- Steht `AskUserQuestion` zur Verfügung: für Auswahlfelder (`visibility`, `license`, `project_type`) nutzen — mit dem abgeleiteten Wert als erster Option.
- Freitextfelder (`title`, `description`, `topics`) in derselben Nachricht als bestätigbare Vorschlagsliste ausgeben.
- Sagt der User «mach einfach» / «passt so»: alle Vorschläge übernehmen, nicht nachfragen — die finale Zusammenfassung in Schritt 0.4 dient als Kontrolle.

### 0.3 Antworten festhalten — `.github/repo-meta.yml`

Sofort nach dem Intake schreiben. Diese Datei ist ab dann die **einzige Quelle der Wahrheit**; alle Folgeschritte lesen daraus statt erneut zu fragen.

```yaml
# .github/repo-meta.yml — von der github-repo Skill gepflegt
repo_name: fedlex-mcp
title: Fedlex MCP Server
description: MCP server for Swiss federal law data from Fedlex
topics:
  - mcp
  - model-context-protocol
  - swiss-open-data
  - python
  - llm
project_type: mcp-server
visibility: public
license: MIT
author_name: malkreide
github_user: malkreide
language: python
version: 1.0.0
confirmed: true      # false = aus Vorschlägen übernommen, noch nicht bestätigt
```

Ändert sich später ein Wert, **Datei aktualisieren** — nicht erneut von vorne fragen. In einer neuen Session ist das Lesen dieser Datei der erste Schritt.

### 0.4 Gate und Verwendung

Erst weiter zu Schritt 2, wenn alle Pflichtfelder gesetzt sind. Danach Zusammenfassung ausgeben (Name · Description · Topics · Visibility) und die Werte konsequent wiederverwenden:

| Feld | Wird verwendet in |
|---|---|
| `repo_name` | Verzeichnisname, README-H1, `gh repo create` |
| `title` | README-H1 (falls abweichend vom Repo-Namen), Release-Titel |
| `description` | `gh repo create --description`, README-One-Liner, README.de.md |
| `topics` | `gh repo edit --add-topic` (Schritt 8) |
| `visibility` | `gh repo create --public` / `--private` |
| `license`, `author_name` | LICENSE (Schritt 5), README-Author-Sektion |
| `version` | Badge, CHANGELOG, Git-Tag (Schritt 10) |

---

## Schritt 1: Projekttyp und Metadaten bestimmen

Regeln für die **Vorschläge** aus dem Intake (Schritt 0.2). Liegen die Werte bereits in `.github/repo-meta.yml`, ist dieser Schritt übersprungen.

Erkenne den Projekttyp aus dem Kontext oder frage nach:

| Typ | Erkennungsmerkmale |
|---|---|
| `mcp-server` | MCP, Model Context Protocol, Tools für LLMs |
| `claude-skill` | SKILL.md, Claude Skills, Prompting-Framework |
| `raspberry-pi` | Pi, GPIO, Edge AI, Hailo, Sensor |
| `python-lib` | Python-Package, Library, Module |
| `other` | Alles andere |

**Repo-Metadaten vorschlagen** (nur für Felder, die Schritt 0.1 nicht geliefert hat):

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
│   ├── repo-meta.yml   ← Intake-Ergebnis aus Schritt 0 (empfohlen)
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

Alle Platzhalter unten stammen aus `.github/repo-meta.yml` (Schritt 0) — an dieser Stelle nicht erneut nachfragen.

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

**Session-Intake (Schritt 0)**
- [ ] Alle Pflichtfelder erfasst — Titel, Description, Topics wurden genau einmal erfragt
- [ ] `.github/repo-meta.yml` vorhanden und aktuell (`confirmed: true`)
- [ ] Werte in README, `gh repo create` und Topics identisch zur Intake-Datei

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
