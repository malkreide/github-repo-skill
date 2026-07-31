[🇬🇧 English Version](README.md)

# github-repo-skill

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Skill](https://img.shields.io/badge/claude-skill-orange)

> Eine Claude SKILL.md, die professionelle GitHub Repositories mit zweisprachigen README-Dateien, Standarddateien und einem vollständigen `gh`-CLI-Workflow erstellt und pflegt.

## Übersicht

Dieser Skill ermöglicht es Claude, vollständige, professionelle GitHub Repositories für technische Projekte wie MCP-Server, Claude Skills, Raspberry-Pi-Projekte und Python-Bibliotheken zu erstellen. Er generiert zweisprachige README-Dateien (Englisch + Deutsch), Standarddateien (LICENSE, .gitignore, CHANGELOG) und führt durch den vollständigen `gh`-CLI-Workflow — vom ersten Setup bis zu Releases.

Der Skill ist für Entwicklerinnen und Entwickler konzipiert, die konsistente, gut dokumentierte Repositories wollen, ohne sich bei jeder Gelegenheit alle Konventionen und Befehle merken zu müssen.

## Funktionen

- Einmaliger Session-Intake: Titel, Description und Topics werden einmal am Anfang gesammelt und in `.github/repo-meta.yml` festgehalten, statt in jedem Schritt neu erfragt zu werden
- Automatische Projekttyp-Erkennung (MCP-Server, Claude Skill, Raspberry Pi, Python-Bibliothek)
- Zweisprachige README-Generierung (Englisch als Hauptdatei + deutsche Übersetzung), gegenseitig verlinkt
- Repository-Metadaten: Name, Description und Topics/Tags nach Konvention
- Standarddateien: MIT LICENSE, projekttyp-spezifische .gitignore, CHANGELOG.md
- Vollständiger `gh`-CLI-Workflow: Repo-Erstellung, Topics setzen, Updates, Releases
- Conventional-Commits-Anleitung und Semantic Versioning
- Qualitätscheckliste vor dem ersten Push und vor jedem Release

## Voraussetzungen

- [GitHub CLI (`gh`)](https://cli.github.com/) installiert und authentifiziert
- Git installiert und konfiguriert
- Ein GitHub-Konto

## Installation

`SKILL.md` in den Claude-Skills-Ordner kopieren:

```bash
# Repository klonen
git clone https://github.com/malkreide/github-repo-skill.git

# Skill in das Claude-Skills-Verzeichnis kopieren
cp github-repo-skill/SKILL.md /pfad/zu/deinen/skills/github-repo/SKILL.md
```

## Verwendung / Quickstart

Nach der Installation als Claude Skill wird er durch folgende Formulierungen ausgelöst:

- *"Erstelle ein GitHub Repo für dieses Projekt"*
- *"Mach das GitHub-ready"*
- *"Wie stelle ich das auf GitHub?"*
- *"Generiere README-Dateien für meinen MCP-Server"*

Claude führt dann durch alle Schritte: Metadaten, Dateigenerierung und `gh`-CLI-Befehle.

## Projektstruktur

```
github-repo-skill/
├── SKILL.md          ← Der Claude Skill (Hauptdatei)
├── README.md         ← Englische Version
├── README.de.md      ← Diese Datei (Deutsch)
├── LICENSE           ← MIT-Lizenz
├── .gitignore        ← Skill-spezifische Ignores
└── CHANGELOG.md      ← Versionsverlauf
```

## Was der Skill abdeckt

Der Skill führt durch einen Intake-Schritt und 10 Arbeitsschritte:

0. **Session-Intake** — Titel, Description, Topics, Visibility einmalig gebündelt erfassen und in `.github/repo-meta.yml` festhalten
1. **Projekttyp-Erkennung** — MCP-Server, Claude Skill, Raspberry Pi, Python-Bibliothek
2. **Repo-Metadaten** — Namenskonventionen, Description, Topics/Tags
3. **README.md (EN)** — vollständiges Template mit Badges und allen Pflichtabschnitten
4. **README.de.md** — Deutsche Übersetzung, Schweizer Rechtschreibung
5. **LICENSE** — MIT Standard
6. **.gitignore** — projekttyp-spezifisch
7. **CHANGELOG.md** — Keep-a-Changelog-Format + Semantic Versioning
8. **`gh`-CLI-Workflow** — Repo-Erstellung, Auth-Check, Topics setzen
9. **Commit-Workflow** — Conventional Commits, Post-Commit-Checkliste
10. **Release-Workflow** — Git Tags, `gh release create`, Badge-Updates

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md)

## Lizenz

MIT-Lizenz — siehe [LICENSE](LICENSE)

## Autorin

malkreide · [github.com/malkreide](https://github.com/malkreide)
