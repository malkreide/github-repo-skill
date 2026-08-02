---
name: github-repo
description: Erstelle, prüfe und publiziere professionelle GitHub Repositories für technische Projekte (MCP-Server, Claude SKILLs, Raspberry Pi, Python). Verwende diesen Skill immer wenn der User (1) ein Repo erstellen, publizieren oder GitHub-ready machen will, (2) bilinguale READMEs (EN/DE) oder Standard-Dateien (LICENSE, .gitignore, CHANGELOG, SECURITY, CONTRIBUTING) braucht, (3) Repo-Metadaten wie Name, Description oder Topics definiert, (4) ein bestehendes Repo prüfen, aktualisieren oder aufräumen will, (5) einen Release oder Git-Tag erstellt, (6) ein Python-Paket oder einen MCP-Server auf PyPI bzw. in die MCP-Registry publiziert, (7) den GitHub-Workflow per gh-CLI oder MCP-Tools nutzt, (8) vor einem Push einen Secrets-, Datenschutz- oder Sicherheitscheck braucht, (9) CI-Fehler debuggt, die ohne Codeänderung auftreten. Auch bei Fragen wie «Wie stelle ich das auf GitHub?», «Kannst du das GitHub-ready machen?», «Warum ist die CI rot?» oder «Warum schlägt der Publish fehl?» diesen Skill verwenden.
---

# GitHub Repo Skill

Erstellt und pflegt GitHub Repositories mit bilingualem README (EN/DE),
Standard-Dateien, Secrets-Check, reproduzierbarer CI und Release-Gate.

## Bundle

| Datei | Wann lesen / verwenden |
|---|---|
| `scripts/validate_repo.py` | Immer vor Push und Release. Meldet Struktur-, README- und CI-Konfigurationsfehler. Ändert nichts. |
| `scripts/check_release_artifacts.py` | Im Release-Workflow, nach `python -m build`, vor dem Upload. |
| `scripts/test_c1.py` | Nach jeder Änderung an der C1-Logik in `validate_repo.py`: `python3 scripts/test_c1.py` |
| `scripts/test_emoji.py` | Nach jeder Änderung an `EMOJI_RE`: `python3 scripts/test_emoji.py` |
| `references/mcp-publishing.md` | Sobald ein `*-mcp`-Repo publiziert oder released wird. |
| `references/review-rules.md` | **Vor** jeder Änderung an einem bestehenden Repo. |
| `assets/templates/` | README-Vorlagen EN/DE |
| `assets/workflows/` | `ci.yml`, `publish.yml` (nach `.github/workflows/`), `dependabot.yml` (nach `.github/`) |
| `assets/gitignore/`, `assets/LICENSE-MIT.txt` | Standard-Dateien |

## Vier Grundregeln

1. **Metadaten einmal erfassen** (Schritt 0). Titel, Description und Topics werden pro Projekt genau einmal erfragt — gebündelt, vor der ersten Datei, festgehalten in `.github/repo-meta.yml`.
2. **Melden statt aufräumen.** Bei bestehenden Repos zuerst `references/review-rules.md` lesen. Abweichungen sind oft bewusst (Selbstbezeichnungen, präzisere Sektionstitel, deutsche Synonyme) — sie werden nicht «vereinheitlicht».
3. **Kein Push ohne Secrets-Check** (Schritt 9). Die Git-History lässt sich nicht nachträglich privat machen.
4. **Kein Release ohne Gate** (Schritt 12). PyPI-Releases sind unveränderlich; drei der häufigsten Fehler fallen erst nach dem erfolgreichen Upload auf.

---

## GitHub-Backend bestimmen — `gh` ist nicht überall vorhanden

**In Claude Code auf dem Web und in Remote-Sessions ist die `gh`-CLI nicht
installiert.** Dort stehen nur die GitHub-MCP-Tools und `git` zur Verfügung. Vor
der ersten GitHub-Operation feststellen, welches Backend gilt:

```bash
command -v gh >/dev/null && gh auth status    # Treffer → Backend A
```

| | Backend | Erkennung |
|---|---|---|
| **A** | `gh`-CLI | `command -v gh` liefert einen Pfad und `gh auth status` ist grün |
| **B** | GitHub-MCP-Tools | kein `gh`, aber Tools wie `create_repository`, `create_pull_request`, `push_files` verfügbar |
| **C** | nur `git` | weder noch — Repo-Anlage und Settings laufen manuell über github.com |

**Operationen je Backend:**

| Operation | A — `gh` | B — MCP-Tools | C — nur `git` |
|---|---|---|---|
| Repo anlegen | `gh repo create` | `create_repository` | manuell auf github.com, dann `git remote add origin` |
| Description setzen | `gh repo edit --description` | Feld von `create_repository`, sonst Settings-UI | Settings-UI |
| **Topics setzen** | `gh repo edit --add-topic` | **kein Tool vorhanden** → Settings-UI, und in `repo-meta.yml` als offen markieren | Settings-UI |
| Commit + Push | `git push` | `push_files` / `create_or_update_file` oder `git push` | `git push` |
| Branch anlegen | `git checkout -b` | `create_branch` | `git checkout -b` |
| PR erstellen | `gh pr create` | `create_pull_request` | manuell |
| CI-Status prüfen | `gh run list` | `pull_request_read` (`get_check_runs`), `actions_list` | github.com |
| Default-Branch / Archivstatus | `gh repo view --json isArchived,defaultBranchRef` | `list_branches`, `search_repositories` | `git ls-remote --symref origin HEAD` |
| Tag pushen | `git push origin "v$VERSION"` | dito — in Web-/Remote-Sessions oft mit `403` blockiert, siehe unten | dito |
| Release | `gh release create` | kein Tool → Release manuell auf github.com | Release manuell auf github.com |
| Secret Scanning aktivieren | `gh api -X PATCH …` (9.6) | `run_secret_scanning` scannt, aktiviert aber nicht → Settings-UI | Settings-UI |

**Tag-Pushes können gesperrt sein, obwohl Branch-Pushes funktionieren.** In
Claude Code auf dem Web läuft `git` über einen Proxy, dessen Egress-Policy
`refs/tags/*` ablehnen kann. Symptom:

```
error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
fatal: the remote end hung up unexpectedly
```

Kontrolle: `git ls-remote --tags origin` bleibt leer, während
`git ls-remote --heads origin` den Default-Branch liefert. Das ist eine
Richtlinienentscheidung — **nicht umgehen**, sondern melden. Ein nur lokal
gesetzter Tag ist zudem verloren, sobald der ephemere Container endet. Vorgehen:
Release-Notes extrahieren (Schritt 12), Notes-Datei und die drei Befehle an den
User übergeben, Tag und Release aus einer Umgebung mit Tag-Push-Recht anlegen.

Was ein Backend nicht kann, wird **als offener Punkt in `repo-meta.yml`
vermerkt** und beim nächsten Durchlauf mit `gh` nachgezogen — nicht stillschweigend
übergangen. Alle `gh`-Blöcke in den Schritten 10–12 setzen Backend A voraus.

---

## Schritt 0: Session-Intake — Metadaten einmal vollständig erfassen

**Titel, Description und Topics werden pro Projekt genau einmal erfragt** —
gebündelt in einer Nachricht, bevor die erste Datei geschrieben wird. Nicht
verstreut über die Session, nicht Feld für Feld, nicht in jedem Folgeschritt neu.

### 0.1 Zuerst suchen, dann fragen

| Prio | Quelle | Wie |
|---|---|---|
| 1 | Angaben des Users in dieser Session | aus dem Verlauf übernehmen |
| 2 | `.github/repo-meta.yml` | Datei lesen → alles bereits erfasst |
| 3 | Bestehendes Repo | `gh repo view {user}/{repo} --json name,description,repositoryTopics,visibility,defaultBranchRef` (Backend A) |
| 4 | Projektdateien | `pyproject.toml`, `server.json`, `package.json`, SKILL-Frontmatter, bestehendes README, `LICENSE` |
| 5 | Codebase | Projekttyp, Sprache und Zweck ableiten → Vorschlag bauen |

### 0.2 Intake-Block — alles in EINER Nachricht

Zu jedem fehlenden Feld einen **konkreten Vorschlag** liefern, damit der User nur
bestätigt oder korrigiert. Keine offene Frage, wo aus dem Code ein Vorschlag
ableitbar ist.

| Feld | Pflicht | Default / Ableitung |
|---|---|---|
| `repo_name` | ja | Namenskonvention aus Schritt 1 |
| `title` | ja | Repo-Name in Title Case |
| `description` | ja | Zweck des Codes, max. 100 Zeichen, EN, ohne Schlusspunkt |
| `topics` | ja | 5–8, Regeln aus Schritt 1 |
| `project_type` | ja | Erkennung aus Schritt 1 |
| `visibility` | ja | `public` |
| `license` | nein | `MIT` |
| `author_legal_name` | nein | `git config user.name` — steht im Copyright (Schritt 5) |
| `author_label` | nein | Selbstbezeichnung im deutschen README: `Autor` / `Autorin` / `Autor·in`. Einmal festlegen, **nie** angleichen (Regel D1) |
| `github_user` | nein | `gh api user --jq .login` |
| `default_branch` | nein | `main` — nicht raten, prüfen (Regel E5) |
| `language` | nein | aus Projektdateien |
| `version` | nein | `1.0.0` |
| `pypi_package` | nur PyPI | Paketname, identisch in `pyproject.toml` |
| `mcp_name` | nur MCP | `io.github.<github_user>/<server>` für den README-Marker (A1) |

**Fragestil:** Steht `AskUserQuestion` zur Verfügung, damit die Auswahlfelder
(`visibility`, `license`, `project_type`) abfragen — abgeleiteter Wert als erste
Option. Freitextfelder in derselben Nachricht als bestätigbare Vorschlagsliste.
Sagt der User «mach einfach»: Vorschläge übernehmen, `confirmed: false` setzen
und am Schluss die Zusammenfassung aus 0.4 zeigen.

### 0.3 Antworten festhalten — `.github/repo-meta.yml`

Sofort nach dem Intake schreiben. Ab dann **einzige Quelle der Wahrheit**; alle
Folgeschritte lesen daraus, statt erneut zu fragen.

```yaml
# .github/repo-meta.yml — von der github-repo Skill gepflegt
repo_name: fedlex-mcp
title: Fedlex MCP Server
description: MCP server for Swiss federal law data from Fedlex
topics: [mcp, model-context-protocol, swiss-open-data, python, llm]
project_type: mcp-server
visibility: public
license: MIT
author_legal_name: Vorname Nachname
author_label: Autor·in
github_user: malkreide
default_branch: main
language: python
version: 1.0.0
pypi_package: fedlex-mcp
mcp_name: io.github.malkreide/fedlex-mcp
confirmed: true          # false = aus Vorschlägen übernommen, unbestätigt
offen:                   # was das aktuelle Backend nicht setzen konnte
  - topics (Backend B: kein MCP-Tool — Settings-UI oder später mit gh)
```

Ändert sich später ein Wert: **Datei aktualisieren**, nicht neu fragen. In einer
neuen Session ist das Lesen dieser Datei der erste Schritt.

### 0.4 Gate und Verwendung

Erst weiter zu Schritt 2, wenn alle Pflichtfelder gesetzt sind. Danach
Zusammenfassung ausgeben (Name · Description · Topics · Visibility) und die Werte
konsequent wiederverwenden:

| Feld | Wird verwendet in |
|---|---|
| `repo_name` | Verzeichnisname, README-H1, Repo-Anlage (Schritt 10) |
| `title` | README-H1 falls abweichend, Release-Titel |
| `description` | Repo-Description, README-One-Liner, `server.json` (≤ 100 Zeichen) |
| `topics` | Topics setzen (Schritt 10) |
| `visibility` | `--public` / `--private` |
| `license`, `author_legal_name` | LICENSE (Schritt 5) |
| `author_label` | `## Autor·in` in `README.de.md` (Schritt 4) |
| `default_branch` | Push- und Workflow-Trigger (Schritt 8, 11) |
| `mcp_name` | README-Marker (Schritt 3) |
| `version`, `pypi_package` | Badge, CHANGELOG, Tag, Release-Gate (Schritt 12) |

---

## Schritt 1: Projekttyp und Metadaten bestimmen

Regeln für die **Vorschläge** aus dem Intake (0.2). Liegen die Werte bereits in
`.github/repo-meta.yml`, ist dieser Schritt übersprungen.

| Typ | Erkennungsmerkmale |
|---|---|
| `mcp-server` | MCP, Model Context Protocol, Tools für LLMs |
| `claude-skill` | SKILL.md, Claude Skills, Prompting-Framework |
| `raspberry-pi` | Pi, GPIO, Edge AI, Hailo, Sensor |
| `python-lib` | Python-Package, Library, Module |
| `other` | Alles andere |

**Repo-Metadaten vorschlagen** (nur für Felder, die 0.1 nicht geliefert hat):

- **Name**: `kebab-case`, präzise, kein `my-` Präfix
  - MCP: `{service}-mcp` · Skill: `{name}-skill` · Pi: `{function}-pi`
- **Description**: max. 100 Zeichen, Englisch, ohne Punkt am Ende
  - Bei MCP-Servern gilt dieselbe Grenze für `server.json` → `description`. Die Registry lehnt längere mit `422 expected length <= 100` ab, und zwar erst **nach** dem PyPI-Upload.
- **Topics/Tags**: 5–8, lowercase
  - Immer: Projekttyp-Tag + Sprachtag (`python`, `typescript`)
  - MCP: `mcp`, `model-context-protocol`, `llm` · Skill: `claude`, `anthropic`, `prompt-engineering` · Pi: `raspberry-pi`, `edge-ai`, `iot`
  - Domain-Tags: `swiss-open-data`, `education`

---

## Schritt 2: Dateistruktur erstellen

### Pflichtdateien

```
repo-name/
├── README.md           ← Englisch (Hauptdatei, enthält den mcp-name-Marker)
├── README.de.md        ← Deutsch
├── LICENSE             ← MIT (Standard), bürgerlicher Name im Copyright
├── .gitignore          ← aus assets/gitignore/
└── CHANGELOG.md
```

### Wenn die Datei erzeugt wird, gehört der Verweis ins README

Häufigster Mangel im Durchlauf über 43 Repos: **10 Repos hatten eine
`SECURITY.md`, auf die kein README verwies** — für Besucher der Startseite also
unerreichbar. Dasselbe bei `CONTRIBUTING.md`. Datei anlegen genügt nicht.

```
├── SECURITY.md         ← verlinkt aus der Sektion Security / Sicherheit
├── CONTRIBUTING.md     ← verlinkt aus Contributing / Mitwirken
├── docs/demo.png       ← wenn vorhanden: in BEIDEN Sprachfassungen einbinden
├── .github/workflows/  ← ci.yml, publish.yml aus assets/workflows/
└── .github/dependabot.yml  ← hält die SHA-Pins aktuell (8.5)
```

### Zusätzlich bei MCP-Servern

```
├── server.json         ← name, version, description (≤ 100 Zeichen)
├── pyproject.toml      ← readme = "README.md", version identisch zu server.json
└── scripts/check_release_artifacts.py
```

---

## Schritt 3: README.md (Englisch)

Vorlage: `assets/templates/README.md`. Struktur verpflichtend, Schluss-Sektionen
in dieser Reihenfolge:

```
Contributing → Security → License → Author
```

**Regeln:**

- **`mcp-name`-Marker** direkt unter dem Titel, bei jedem MCP-Server:
  `<!-- mcp-name: io.github.<user>/<server> -->`
  Er muss in der Datei stehen, die `pyproject.toml` als `readme` deklariert —
  ein Marker nur in `README.de.md` zählt nicht. Details: `references/mcp-publishing.md`.
- **Author als Überschrift** (`## Author`), nicht als Fettdruck (`**Author**`).
  Fettdruck sieht gleich aus, erzeugt aber keine Gliederungsebene.
- **Keine Emoji in Überschriften.** Im Fliesstext (Sprachumschalter, Warnhinweise) sind sie in Ordnung.
- **Demo**: `### Demo` plus Bild. Die referenzierte Datei muss existieren, und der Abschnitt gehört in **beide** Sprachfassungen.
- **Tool-Tabelle**: die **registrierten** Namen verwenden. Bei
  `@mcp.tool(name="gazette_get_publication")` heisst die Funktion trotzdem
  `get_publication` — der registrierte Name gehört ins README.

**Badges:**

```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
```

---

## Schritt 4: README.de.md (Deutsch)

Vorlage: `assets/templates/README.de.md`. Identische Struktur, aber:

- Schweizer Rechtschreibung: kein `ß` → `ss`
- Kopfzeile `🇬🇧 [English Version](README.md)`
- Technische Begriffe, Befehle und Code-Blöcke bleiben englisch
- **Überschriften werden eingedeutscht** — eine englische Überschrift in einer
  sonst durchgehend deutschen Datei ist ein Fehler (kam zweimal vor):

| EN | DE |
|---|---|
| Overview | Übersicht |
| Features | Funktionen |
| Prerequisites | Voraussetzungen |
| Usage | Verwendung |
| Configuration | Konfiguration |
| Project Structure | Projektstruktur |
| Contributing | Mitwirken (auch: Mitmachen, Beitragen) |
| Security | Sicherheit |
| License | Lizenz |
| Author | Autor / Autorin / Autor·in |

Die Varianten in den letzten drei Zeilen sind gleichwertig. Bei einem
bestehenden Repo wird die gewählte Variante **nicht** angeglichen — siehe
`references/review-rules.md`.

---

## Schritt 5: LICENSE

`assets/LICENSE-MIT.txt` kopieren, `{YEAR}` und `{AUTHOR_LEGAL_NAME}` ersetzen.

Im Copyright steht der **bürgerliche Name**, nicht der GitHub-Handle.

---

## Schritt 6: .gitignore

Passende Datei aus `assets/gitignore/` kopieren
(`python`, `node`, `raspberry-pi`, `claude-skill`). Alle Varianten enthalten
bereits die Secret-Muster aus Schritt 9.

---

## Schritt 7: CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - {YYYY-MM-DD}

### Added
- Initial release
```

**SemVer:** PATCH = Bugfix · MINOR = neues Feature, rückwärtskompatibel ·
MAJOR = Breaking Change.

---

## Schritt 8: Python- und CI-Konfiguration

8.1–8.3 verursachen CI-Fehler, die **ohne Codeänderung** auftreten oder Fehler
durchlassen. 8.5–8.6 betreffen nicht die Korrektheit des Laufs, sondern das,
was er darf und was er kostet.

### 8.1 Linter-Regelsatz explizit pinnen

Ohne `[tool.ruff.lint] select` gilt ruffs Default-Regelsatz — und der ändert
sich zwischen Releases. Mit `ruff>=0.4.0` ohne Obergrenze installiert die CI die
jeweils neuste Version. Ein Repo war fünf Tage nach dem letzten grünen Lauf rot,
ohne dass sich eine Zeile geändert hatte.

```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP"]
ignore = ["E501"]
```

Und in der CI mit Obergrenze installieren: `pip install "ruff>=0.6,<0.7"`.

### 8.2 Subprojekte erben nichts

Ein Unterverzeichnis mit eigener `pyproject.toml` und eigenem
`[tool.ruff]`-Block ignoriert die Wurzelkonfiguration **vollständig**. Jedes
Subprojekt braucht seinen eigenen `select`-Block. Bei Monorepos beim
Scaffolding mitgenerieren; `assets/workflows/ci.yml` lintet Subprojekte separat.

### 8.3 Keine blinden Assertions in Tests

`pytest.raises(Exception)` um eine Pydantic-Konstruktion besteht auch bei einem
Tippfehler im Modellnamen. Immer die konkrete Exception:

```python
with pytest.raises(ValidationError):
    ...
```

### 8.4 Workflows kopieren

`assets/workflows/ci.yml` und — bei Python-Paketen — `publish.yml` nach
`.github/workflows/`. `ci.yml` triggert auf `main` **und** `master`.

`assets/workflows/dependabot.yml` gehört nach **`.github/dependabot.yml`**,
nicht nach `.github/workflows/`. Es liegt nur deshalb im selben Ordner, weil
das Bundle alle `.github`-Vorlagen an einem Ort hält.

### 8.5 Actions auf den Commit-SHA pinnen, nicht auf den Tag

**Ein Git-Tag ist verschiebbar.** Wer Schreibzugriff auf das Repo einer Action
hat, kann einen Backdoor-Commit pushen und den bestehenden Versions-Tag darauf
umhängen — `@v4` zeigt dann auf anderen Code als gestern, ohne dass sich im
eigenen Repo eine Zeile geändert hat. Bei `tj-actions/changed-files` ist genau
das im März 2025 passiert: sämtliche historischen Tags wurden auf einen Commit
umgehängt, der Secrets aus den Runner-Umgebungsvariablen in die Logs schrieb,
und die abhängigen Repos zogen ihn beim nächsten regulären Lauf.

Ein Branch-Ref ist noch schwächer als ein Tag — er bewegt sich bei jedem Push.
`pypa/gh-action-pypi-publish@release/v1` ist so eine Referenz, und der Schritt
dahinter hält das PyPI-Token.

```yaml
- uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
```

Der Versionskommentar ist kein Schmuck: ohne ihn ist nicht erkennbar, welche
Version läuft. Dependabot zieht Hash und Kommentar gemeinsam nach.

**SHA innerhalb des bereits deklarierten Majors auflösen.** Beim Pinnen eines
`@v4` auf den SHA von `v7` wird aus einer Härtung eine Verhaltensänderung:

```bash
git ls-remote --tags https://github.com/actions/checkout \
  | grep -vE '\^\{\}$' | grep -E 'v4\.[0-9]+\.[0-9]+$' | sort -k2 -V | tail -1
```

**Ohne `dependabot.yml` ist Pinning ein Rückschritt** — die Hashes frieren auf
dem Stand des Tages ein, an dem das Repo entstand. Beides gehört zusammen.

### 8.6 `permissions`, `concurrency`, `timeout-minutes`

Drei Zeilen, die je einen Defekt der Voreinstellung beheben:

| Block | Voreinstellung ohne ihn | Folge |
|---|---|---|
| `permissions: contents: read` | Repo-Default, je nach Alter und Organisation `read and write` | ein reiner Lese-Job trägt ein Token, das pushen und Releases anlegen darf |
| `concurrency` + `cancel-in-progress` | keine | ein neuer Push auf denselben PR lässt den alten Lauf zu Ende laufen — beide werden abgerechnet |
| `timeout-minutes` | 6 Stunden pro Job | eine Endlosschleife oder ein hängender Netzwerkaufruf leert das Monatskontingent unbemerkt |

`permissions` gehört auf **Workflow-Ebene**. Steht es nur an einem Job, erbt
jeder andere Job weiterhin den Repo-Default. Jobs heben sich einzeln an, was
sie zusätzlich brauchen — in `publish.yml` etwa `id-token: write` für OIDC.

**`cancel-in-progress` nicht in Release-Workflows.** Einen laufenden
PyPI-Upload abzubrechen ist kein gespartes Kontingent, sondern ein halber
Release. `assets/workflows/publish.yml` setzt deshalb bewusst nur
`timeout-minutes`.

---

## Schritt 9: Secrets-Check vor dem ersten Push

**Verbindlich, auch bei privaten Repos** — die Sichtbarkeit lässt sich später
ändern, die Git-History nicht.

### 9.1 Ignore-Regeln vor dem ersten `git add`

`.gitignore` muss mindestens `.env`, `.env.*`, `*.key`, `*.pem`,
`credentials.json`, `secrets.yaml`, `config.local.*` abdecken (in
`assets/gitignore/` enthalten). Dann prüfen, was tatsächlich getrackt würde:

```bash
git add -A --dry-run | head -50
```

### 9.2 Automatisierter Scan

```bash
gitleaks detect --source . --no-git --redact --verbose   # Arbeitsverzeichnis
gitleaks detect --source . --redact --verbose            # gesamte History
```

Exit-Code `0` = sauber, `1` = Findings. **Bei Findings: nicht pushen.**

### 9.3 Manueller Kontroll-Check

```bash
git grep -nEI '(api[_-]?key|secret|passwo?rd|token|bearer|BEGIN [A-Z ]*PRIVATE KEY)' | head -30
git config user.name && git config user.email    # welche Adresse wird publiziert?
```

### 9.4 Kontextspezifische Prüfung (öffentliche Verwaltung)

- [ ] Keine Personendaten in Code, Testdaten oder Fixtures
- [ ] Keine internen Hostnames, IP-Ranges, Pfade oder Systembezeichnungen
- [ ] Keine internen Dokumente oder Auszüge daraus in `docs/`
- [ ] Testdaten synthetisch, nicht kopierte Echtdaten
- [ ] Commit-Messages ohne Ticketinhalte oder Klarnamen Dritter

### 9.5 Wenn ein Secret bereits committet wurde

1. **Zuerst rotieren.** Ein gepushtes Secret gilt als kompromittiert — auch nach dem Löschen (Forks, Caches, Crawler).
2. Danach History bereinigen: `git filter-repo --path .env --invert-paths`
3. Force-Push, alle Klone neu ziehen lassen.

`git rm` oder ein Folge-Commit entfernt das Secret **nicht** aus der History.

### 9.6 Schutz auf GitHub aktivieren

```bash
gh api -X PATCH repos/{owner}/{repo} \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'
```

---

## Schritt 10: Repo erstellen und konfigurieren

Alle Platzhalter stammen aus `.github/repo-meta.yml` (Schritt 0) — hier nicht
erneut nachfragen. Der folgende Block setzt **Backend A** voraus; für B und C
gilt die Mapping-Tabelle oben.

```bash
gh --version && gh auth status          # Voraussetzungen

git init && git add . && git commit -m "Initial commit: {Beschreibung}"

gh repo create {repo-name} \
  --public \                            # oder --private
  --description "{max. 100 Zeichen}" \
  --source=. --remote=origin --push

gh repo edit {user}/{repo} --add-topic mcp --add-topic python --add-topic llm
```

**Bei MCP-Servern jetzt den Pending Publisher auf PyPI anlegen** — vor dem
ersten Workflow-Lauf. Felder und Fallstricke: `references/mcp-publishing.md` (A3).

---

## Schritt 11: Update-Workflow nach Commits

```bash
git add .
git commit -m "{type}: {kurze Beschreibung}"
git push origin "$(git symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's|.*/||')"
```

Der Default-Branch ist **nicht immer `main`** — drei Repos nutzen `master`.

**Conventional Commits:** `feat` · `fix` · `docs` · `refactor` · `test` · `chore`

### 11.1 Web- und Remote-Sessions: Branch statt direktem Push

In Claude Code auf dem Web läuft jede Änderung über Branch → Push → Draft-PR.
Ein direkter Push auf den Default-Branch ist dort weder vorgesehen noch immer
erlaubt.

```bash
git checkout -b {branch-name}
git add -A && git commit -m "{type}: {Beschreibung}"
git push -u origin {branch-name}
```

- **Draft-PR eröffnen**, sobald der Branch gepusht ist — Backend A: `gh pr create --draft`, Backend B: `create_pull_request` mit `draft: true`.
- **PR-Template prüfen** (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, Wurzel, `docs/`) und dessen Sektionen übernehmen, falls vorhanden.
- **Push-Fehler durch Netzwerk**: bis zu vier Versuche mit 2 s, 4 s, 8 s, 16 s Wartezeit. Ein `403` ohne Netzwerkfehler ist meist ein archiviertes Repo (F2), keine fehlende Berechtigung.
- **Der Container ist ephemer.** Nicht gepushte Arbeit ist nach Sessionende verloren — vor dem Abschluss committen und pushen.
- **Ist der PR eines Branches bereits gemergt**, wird für Folgearbeit nicht auf der gemergten History weitergebaut: Branch vom aktuellen Default-Branch neu aufsetzen (`git checkout -B {branch} origin/{default}`) und einen neuen PR eröffnen.

**Nach jedem relevanten Commit:**

1. `CHANGELOG.md` → Eintrag unter `[Unreleased]`
2. README aktualisieren, falls Funktionen oder Struktur geändert haben
3. Bei README-Änderungen: Marker-Anzahl vorher/nachher vergleichen
   (`grep -c 'mcp-name:' README.md`) — ein Blockverschieben am Dateiende hat den
   Marker einmal stillschweigend mitgerissen
4. `python3 scripts/validate_repo.py .`

---

## Schritt 12: Release erstellen

**Vorher:** `python3 scripts/validate_repo.py .` muss ohne ERROR durchlaufen.
Bei MCP-Servern zusätzlich `references/mcp-publishing.md` lesen.

```bash
VERSION=1.0.0

# 1. CHANGELOG: [Unreleased] → [VERSION] - DATUM
sed -i '' "s/^## \[Unreleased\]/## [Unreleased]\n\n## [$VERSION] - $(date +%F)/" CHANGELOG.md
# Linux: sed -i "s/..."   ·   portabel: perl -pi -e

# 2. Version in pyproject.toml und server.json angleichen (müssen identisch sein)

# 3. Tag setzen
git tag -a "v$VERSION" -m "Release v$VERSION: {Beschreibung}"
git push origin "v$VERSION"
# 403 hier = Tag-Push von der Session-Policy gesperrt (siehe Backend-Abschnitt).
# Prüfen mit: git ls-remote --tags origin

# 4. Nur den Abschnitt DIESER Version extrahieren
awk -v v="## [$VERSION]" '
  index($0, v) == 1 { flag = 1; next }
  flag && /^## \[/  { exit }
  flag              { print }
' CHANGELOG.md > /tmp/release-notes.md
test -s /tmp/release-notes.md || { echo "FEHLER: kein CHANGELOG-Abschnitt für $VERSION"; exit 1; }

# 5. GitHub Release
gh release create "v$VERSION" \
  --title "v$VERSION — {Titel}" \
  --notes-file /tmp/release-notes.md --latest

# 6. Badge in README.md UND README.de.md aktualisieren
```

**Warum nicht `--notes-file CHANGELOG.md`:** das hängt den gesamten
Versionsverlauf an jeden Release. Alternative ohne CHANGELOG-Pflege:
`gh release create "v$VERSION" --generate-notes`.

**Wenn der Publish-Workflow fehlschlägt:** einen alten Tag-Lauf **nicht**
erneut starten — ein Re-Run checkt den alten Commit aus und reproduziert
denselben Fehler. Stattdessen `workflow_dispatch` auf dem Default-Branch oder
einen neuen Tag setzen.

---

## Bestehende Repos bearbeiten

**Zuerst `references/review-rules.md` lesen.** Diese Regeln haben jeweils eine
falsche Änderung oder einen Fehlalarm verhindert:

| Regel | Kurzfassung |
|---|---|
| D1 | Selbstbezeichnungen (`Autor`, `Autorin`, `Autor·in`) nie umschreiben |
| D2 | Präzisere Titel (`Software Licence`, `Security & Compliance`) behalten |
| D3 | Deutsche Synonyme sind alle legitim — nur englische Titel in deutschen Dateien sind falsch |
| E1 | Tool-Namen gegen den registrierten Namen prüfen, nicht gegen `def` |
| E2 | Bilder in `![]()` **und** `<img src="">` suchen, Badges herausfiltern |
| E3 | Überschriften exakt vergleichen — `## Sicherheit & Grenzen` ≠ `## Sicherheit` |
| E4 | Vor Emoji-Entfernung Anker-Links prüfen; Unicode-Bereiche eng fassen, sonst fallen Umlaute weg |
| E5 | Default-Branch ist nicht immer `main` |
| E6 | C1-Reihenfolgefehler zeigt oft auf eine Inhaltssektion, nicht auf den Schlussblock — vor dem Umsortieren prüfen, wo die gemeldete Sektion steht |
| E7 | Emoji ≠ «Zeichen über U+2000». `↔` ist Typografie, `↔️` ein Emoji — Textdarstellungs-Zeichen zählen erst mit VS16 |
| F2 | 403 beim Push: zuerst Archiv-Status prüfen, nicht Berechtigungen |

---

## Qualitätscheckliste

`python3 scripts/validate_repo.py .` deckt die meisten Punkte automatisch ab.

**Blocker — ohne diese Punkte kein Push**
- [ ] `gitleaks detect` ohne Findings
- [ ] Keine Personendaten oder internen Systembezeichnungen im Repo
- [ ] Commit-Identität (`user.email`) bewusst gewählt
- [ ] Secret Scanning + Push Protection aktiviert

**Session-Intake (Schritt 0)**
- [ ] Pflichtfelder erfasst — Titel, Description, Topics genau einmal erfragt
- [ ] `.github/repo-meta.yml` vorhanden und aktuell (`confirmed: true`)
- [ ] Werte in README, Repo-Description und Topics identisch zur Intake-Datei
- [ ] Was das Backend nicht setzen konnte, steht unter `offen`

**README (beide Sprachfassungen)**
- [ ] Schluss-Sektionen in der Reihenfolge Contributing → Security → License → Author
- [ ] `SECURITY.md` und `CONTRIBUTING.md` verlinkt, nicht nur vorhanden
- [ ] `## Author` als Überschrift, nicht als Fettdruck
- [ ] Keine Emoji in Überschriften
- [ ] Demo in beiden Fassungen, referenzierte Datei existiert
- [ ] Sprachumschalter in beiden Richtungen
- [ ] DE: deutsche Überschriften, kein `ß`
- [ ] Tool-Namen = registrierte Namen

**Repo-Metadaten**
- [ ] Description ≤ 100 Zeichen · Topics 5–8 · LICENSE mit bürgerlichem Namen · `.gitignore` passend

**CI**
- [ ] `[tool.ruff.lint] select` explizit, in **jedem** pyproject
- [ ] ruff mit Obergrenze gepinnt
- [ ] Keine `pytest.raises(Exception)`

**Release (MCP/PyPI)**
- [ ] `mcp-name`-Marker in der als `readme` deklarierten Datei
- [ ] `server.json` description ≤ 100 Zeichen
- [ ] Version in pyproject = server.json = Tag
- [ ] Pending Publisher angelegt, Environment-Name eingetragen
- [ ] Release-Notes enthalten nur den Abschnitt dieser Version

---

## Troubleshooting

| Symptom | Ursache | Vorgehen |
|---|---|---|
| `invalid-publisher: valid token, but no corresponding publisher` | Pending Publisher fehlt oder Environment-Feld leer | `references/mcp-publishing.md` → A3 |
| `422 expected length <= 100` beim Registry-Publish | `server.json` description zu lang — fällt erst nach erfolgreichem PyPI-Upload auf | A2 |
| Registry findet das Paket nicht | `mcp-name`-Marker fehlt im publizierten README | A1 |
| Publish erfolgreich, `/pypi/<paket>/json` zeigt alte Version | JSON-API liefert gecachte Antworten | gegen `https://pypi.org/simple/<paket>/` prüfen (F1) |
| Re-Run schlägt identisch fehl | alter Tag-Lauf checkt alten Commit aus | `workflow_dispatch` oder neuer Tag (A4) |
| CI rot ohne Codeänderung | ruff-Default-Regelsatz hat sich geändert | `select` pinnen (8.1) |
| Lint übersieht Subprojekt | eigene `pyproject.toml` erbt nichts | eigener `select` (8.2) |
| `403` beim Push, Lesen geht | Repo archiviert | `gh repo view --json isArchived` (F2) |
| `gh: command not found` | Web-/Remote-Session ohne CLI | Backend B oder C, siehe Mapping-Tabelle oben |
| `403` beim Tag-Push, Branch-Push geht | Egress-Policy der Session lehnt `refs/tags/*` ab | nicht umgehen: Notes extrahieren, Tag und Release lokal anlegen (Backend-Abschnitt) |
| Topics lassen sich nicht setzen | Backend B hat kein Topic-Tool | Settings-UI, in `repo-meta.yml` unter `offen` vermerken |
| Nach «Titel? Description? Tags?» in jeder Session | Schritt 0 übersprungen | `.github/repo-meta.yml` anlegen (0.3) |

---

## Schnellreferenz: gh (Backend A)

```bash
gh repo view {user}/{repo}
gh repo view {user}/{repo} --json isArchived,defaultBranchRef
gh repo edit --add-topic {topic} / --remove-topic {topic}
gh repo list
gh issue create --title "{Titel}" --body "{Text}"
gh pr create --title "{Titel}" --body "{Text}"
gh release list / gh release view
gh run list --workflow publish.yml
gh run rerun {run-id}          # Achtung: checkt den alten Commit aus (A4)
```
