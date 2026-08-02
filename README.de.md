# github-repo-skill

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Skill](https://img.shields.io/badge/claude-skill-orange)

> Ein Claude Skill, der professionelle GitHub Repositories erstellt, prüft und publiziert — zweisprachige READMEs, Secrets-Check, reproduzierbare CI und Release-Gate.

[🇬🇧 English Version](README.md)

## Übersicht

Dieser Skill ermöglicht Claude, vollständige GitHub Repositories für technische
Projekte zu erstellen und zu pflegen — MCP-Server, Claude Skills,
Raspberry-Pi-Projekte, Python-Bibliotheken. Er generiert zweisprachige READMEs
(Englisch + Deutsch), Standard-Dateien (LICENSE, .gitignore, CHANGELOG, SECURITY,
CONTRIBUTING) und führt durch den gesamten Ablauf vom ersten Commit bis zum
Release auf PyPI oder in der MCP-Registry.

Jede Regel darin geht auf einen real aufgetretenen Fehler zurück — die meisten aus
einem Prüfdurchlauf über 43 Repositories. Keine davon ist vorsorglich.

## Funktionen

- **Einmaliger Session-Intake** — Titel, Description und Topics werden einmal
  gebündelt erfasst, bevor die erste Datei entsteht, und in `.github/repo-meta.yml`
  festgehalten
- **Backend-unabhängig** — funktioniert mit der `gh`-CLI, mit GitHub-MCP-Tools
  (Claude Code im Web, wo `gh` nicht existiert) oder mit reinem `git`
- **Secrets-Check vor dem ersten Push** — Ignore-Regeln, automatisierter Scan,
  History-Bereinigung und eine kontextspezifische Prüfung für die öffentliche
  Verwaltung
- **Reproduzierbare CI** — gepinnte Linter-Regelsätze, Konfiguration je
  Subprojekt, keine blinden Assertions in Tests
- **Release-Gate** — prüft die Artefakte vor dem unveränderlichen PyPI-Upload
- Zweisprachige README-Generierung (Englisch als Hauptdatei + deutsche Fassung),
  gegenseitig verlinkt
- Prüfregeln für bestehende Repositories: melden statt «aufräumen»
- Zwei ausschliesslich lesende Prüfskripte sowie fertige Vorlagen für Workflows,
  .gitignore und READMEs

## Voraussetzungen

- Claude mit Skill-Unterstützung (Claude Code oder das Skills-Verzeichnis deines
  Setups)
- Git installiert und konfiguriert
- Python 3.9+ für die Prüfskripte
- Optional: [GitHub CLI (`gh`)](https://cli.github.com/) — ohne sie weicht der
  Skill auf GitHub-MCP-Tools oder reines `git` aus
- Optional: [`gitleaks`](https://github.com/gitleaks/gitleaks) für den
  automatisierten Secrets-Scan

## Installation

```bash
# Repository klonen
git clone https://github.com/malkreide/github-repo-skill.git

# Ganzes Bundle kopieren — der Skill liest assets/, references/ und scripts/
cp -r github-repo-skill /pfad/zu/deinen/skills/github-repo
```

## Verwendung

Nach der Installation lässt sich der Skill so auslösen:

- *«Erstelle ein GitHub-Repo für dieses Projekt»*
- *«Kannst du das GitHub-ready machen?»*
- *«Warum ist die CI rot, obwohl sich nichts geändert hat?»*
- *«Publiziere diesen MCP-Server in der Registry»*

Claude beginnt mit dem Session-Intake und führt danach durch Dateigenerierung,
Secrets-Check und Repo-Einrichtung.

Der Validator lässt sich jederzeit gegen ein bestehendes Repo laufen:

```bash
python3 scripts/validate_repo.py /pfad/zum/repo
# Exit-Code 0 = keine Fehler, 1 = mindestens ein Fehler
```

## Projektstruktur

```
github-repo-skill/
├── SKILL.md                          ← Der Skill (Hauptdatei)
├── assets/
│   ├── LICENSE-MIT.txt
│   ├── gitignore/                    ← python, node, raspberry-pi, claude-skill
│   ├── templates/                    ← README.md, README.de.md
│   └── workflows/                    ← ci.yml, publish.yml
├── references/
│   ├── mcp-publishing.md             ← PyPI + MCP-Registry, vor jedem Release lesen
│   ├── review-rules.md               ← vor Änderungen an bestehenden Repos lesen
│   └── rpi-kernel-build.md · .de.md  ← Raspberry-Pi-Kernel: Build, Modul, Overlay
├── scripts/
│   ├── validate_repo.py              ← Struktur- und Dokumentationsprüfung
│   └── check_release_artifacts.py    ← Release-Gate
├── .github/repo-meta.yml             ← Intake-Ergebnis dieses Repos
├── README.md · README.de.md
├── SECURITY.md · CONTRIBUTING.md
├── LICENSE · .gitignore · CHANGELOG.md
```

## Was der Skill abdeckt

Ein Intake-Schritt, zwölf Arbeitsschritte und eine Prüfspur:

| Schritt | Inhalt |
|---|---|
| 0 | **Session-Intake** — Metadaten einmal erfassen, in `.github/repo-meta.yml` ablegen |
| 1–2 | Projekttyp, Namenskonventionen, Dateistruktur |
| 3–4 | README.md (EN) und README.de.md (DE), gegenseitig verlinkt |
| 5–7 | LICENSE, .gitignore, CHANGELOG |
| 8 | Python- und CI-Konfiguration — die drei Ursachen für CI-Fehler ohne Codeänderung |
| 9 | Secrets-Check vor dem ersten Push |
| 10 | Repo erstellen und konfigurieren |
| 11 | Commit-Workflow inklusive Branch → Draft-PR für Web-Sessions |
| 12 | Release mit Gate, Tag und versionsgenauen Release-Notes |
| — | Bestehende Repos: Prüfregeln, Qualitätscheckliste, Troubleshooting-Tabelle |

Vor jeder GitHub-Operation bestimmt der Skill sein Backend (`gh`-CLI, MCP-Tools
oder reines `git`) und ordnet jede Operation entsprechend zu. Was das aktuelle
Backend nicht kann, wird als offener Punkt vermerkt statt stillschweigend
übergangen.

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md)

## Mitwirken

Beiträge sind willkommen — siehe [CONTRIBUTING.md](CONTRIBUTING.md). Der Massstab
für eine neue Regel: den Fehler benennen, den sie verhindert.

## Sicherheit

[SECURITY.md](SECURITY.md) beschreibt den Meldeweg und den sicheren Einsatz des
Skills.

## Lizenz

MIT License — siehe [LICENSE](LICENSE)

## Autor

malkreide · [github.com/malkreide](https://github.com/malkreide)
