# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- **Alle Actions in den mitgelieferten Workflows sind auf Commit-SHAs gepinnt.**
  `assets/workflows/ci.yml` und `publish.yml` referenzierten `actions/checkout@v4`,
  `actions/setup-python@v5`, `upload-`/`download-artifact@v4` — und
  `pypa/gh-action-pypi-publish@release/v1`, also einen **Branch**, der sich bei
  jedem Push des Maintainers verschiebt, in dem Schritt, der das PyPI-Token
  hält.

  Ein Tag ist kein unveränderlicher Zeiger. Wer Schreibzugriff auf das Repo
  einer Action hat, hängt ihn auf einen Backdoor-Commit um; im eigenen Repo
  ändert sich dabei keine Zeile. Bei `tj-actions/changed-files` ist das im
  März 2025 passiert — die historischen Tags zeigten auf einen Commit, der
  Secrets aus den Runner-Variablen in die Logs schrieb.

  Das wog hier schwerer als in einem einzelnen Repo: die Templates wandern in
  **jedes** Repo, das mit diesem Skill entsteht, die Exposition wurde also
  weitergereicht.

  **SHA innerhalb des deklarierten Majors aufgelöst**, nicht auf den neusten
  Major gehoben: `checkout` steht bei v7, das Template deklarierte v4. Ein
  Major-Sprung wäre eine Verhaltensänderung, keine Härtung. Jeder Hash per
  `git ls-remote` aufgelöst, keiner aus dem Gedächtnis. Neue Regel `8.5`.

- **`.github/dependabot.yml` als Vorlage** (`assets/workflows/dependabot.yml`).
  Ohne sie wäre Pinning ein Rückschritt — die Hashes frieren auf dem Stand des
  Tages ein, an dem das Repo entstand. Gruppiert alle Action-Updates zu einem
  wöchentlichen PR: bei vielen Repos ist die Zahl der PRs das Problem, nicht
  ihr Inhalt; was einzeln aufschlägt, wird weggeklickt statt gelesen.

### Added

- **`permissions`, `concurrency` und `timeout-minutes` in beiden Workflows,
  neue Regel `8.6`.** Drei Voreinstellungen, die je in die falsche Richtung
  zeigen: ohne `permissions` gilt der Repo-Default, der auch `read and write`
  sein kann — ein reiner Lese-Job trägt dann ein Token, das pushen darf. Ohne
  `concurrency` läuft der vom nächsten Push überholte Job zu Ende und wird
  abgerechnet. Ohne `timeout-minutes` gilt eine Obergrenze von sechs Stunden
  pro Job.

  `permissions` steht auf Workflow-Ebene, nicht am einzelnen Job — sonst erbt
  jeder Job, der es nicht selbst überschreibt, weiterhin den Default. Der
  `publish`-Job hebt sich `id-token: write` einzeln an.

  **`cancel-in-progress` bewusst nicht in `publish.yml`:** einen laufenden
  PyPI-Upload abzubrechen ist kein gespartes Kontingent, sondern ein halber
  Release.

- **Die CI dieses Repos ist nach denselben Regeln gehärtet** und hat eine
  eigene `.github/dependabot.yml`. Ein Skill, der Pinning vorschreibt und
  seine eigenen Workflows auf beweglichen Tags lässt, wird nicht geglaubt.

### Fixed

- **`C5` meldete Typografie als Emoji.** `EMOJI_RE` nahm ganze Unicode-Blöcke
  pauschal, darunter `U+2190–U+21FF` — den kompletten Pfeilblock. Die
  Überschrift `The UID join — Zefix ↔ Amtsblatt` (register-mcp) galt deshalb als
  emojihaltig. Das ist genau die zu breite Regel, vor der E4 warnt, nur trifft
  sie Pfeile statt Umlaute.

  Ein zweiter Bereich war noch gröber: `U+24C2–U+1F251` verschluckte nebenbei
  **den gesamten CJK-Block** — `漢` galt als Emoji. Ebenso `✓`, `✗`, `⌘` und `Ⓜ`.

  Die Erkennung folgt jetzt Unicodes Emoji_Presentation: Zeichen mit
  Emoji-Standarddarstellung (`⚡`, `✨`) zählen allein, Zeichen mit
  Textdarstellung (`⚖`, `❄`, `✈`, `↔`) erst mit dem Variantenselektor VS16.
  An allen Überschriften des Portfolios gegengeprüft — die dort vorkommenden
  Textdarstellungs-Emoji tragen ausnahmslos VS16, die Default-Emoji stehen
  ausnahmslos nackt.

  Gemessen über 50 Repos: **2 Fehlalarme weg, alle 200 echten C5-Befunde
  erhalten**, sonst keine geänderte Zeile. Neue Regel `E7`.

  Nebenwirkung mitbedacht: `normalise()` benutzt dieselbe Regex zum Strippen.
  Der Variantenselektor wird jetzt mitgenommen, sonst bliebe er als
  unsichtbarer Rest im Titel stehen und der exakte Vergleich (E3) scheiterte an
  einem Zeichen, das man nicht sieht.

- **`C1` meldete eine falsche Reihenfolge, obwohl der Schlussblock korrekt
  sortiert war.** Die Prüfung klassifizierte jede Überschrift, deren Titel in
  der Allowlist steht — unabhängig von Ebene und Position — und liess bei
  Mehrfachnennung die *erste* gewinnen. Eine Inhaltssektion mit einem
  Allowlist-Titel verdrängte damit den echten Schlussblock, und die Meldung
  zeigte mehrere hundert Zeilen daneben.

  Portfolio-weit betraf das drei Repos, mit drei verschiedenen Auslösern:
  `## Security & Compliance` (swisstopo-mcp, Z. 324 statt 618–640), `### Security`
  als Unterpunkt von `## Safety & Limits` (register-mcp) und `## Data License`
  (seco-labor-mcp). In **allen dreien war der Schlussblock korrekt** — dem
  Hinweis zu folgen und umzusortieren hätte ihn zerstört.

  Der Titel ist nie die Ursache: `news-monitor-mcp` führt
  `## Security & Compliance` *als* Schluss-Sektion und war immer sauber (D2).
  Ursache ist die Doppelbelegung desselben Klassifikationsschlüssels.

  Die Reihenfolgeprüfung filtert jetzt auf die flachste Ebene, auf der
  Schluss-Sektionen stehen, und lässt bei Mehrfachnennung die letzte gewinnen.
  Die Existenzprüfung (`Sektion '…' fehlt`) bleibt bewusst ebenenblind. Gemessen
  über alle 99 READMEs des Portfolios: 4 Fehlmeldungen weg, sonst keine einzige
  geänderte Zeile. Neue Regel `E6` in `references/review-rules.md`.

### Added

- **`scripts/test_emoji.py` — 47 Fixtures für die Emoji-Erkennung.** Hält alle
  drei Seiten fest: Typografie darf nicht gemeldet werden, echte Emoji müssen
  gefunden werden (auch die ohne Selektor), und `normalise()` darf keine
  unsichtbaren Reste hinterlassen. Enthält Regressionsfälle für beide
  entfernten Bereiche — `↔` für den Pfeilblock, `漢`/`あ`/`한` für den
  CJK-Bereich. Gegen die alte Regex laufen sieben davon rot.

- **`scripts/test_c1.py` — 14 Fixtures für die C1-Logik.** Hält beide Hälften
  einzeln fest: die Filter müssen die Fehlmeldungen beseitigen, dürfen echte
  Fehler aber nicht verstecken. Der schärfste Fall ist ein Duplikat *plus*
  tatsächlich falsch sortiertem Schlussblock — eine zu aggressive
  Last-Wins-Regel besteht alle anderen Fälle und fällt nur dort durch.

  Per Mutationstest gegengeprüft, und die erste Fassung fiel dabei durch: der
  Ebenenfilter war entfernbar, ohne dass ein Test rot wurde, weil im
  register-Muster das spätere `## Security` den Unterpunkt schon per Last-Wins
  verdrängt. Erst ein Fixture ohne spätere Dokumentsektion sichert ihn ab.
  Läuft mit und ohne pytest.

- **`.gitignore` für dieses Repo — es hatte bisher keine.** Aufgefallen durch
  Schritt 9.1 (`git add -A --dry-run`) vor dem Push: eine
  `scripts/__pycache__/*.pyc` wäre mitgegangen. Die mitgelieferte Vorlage
  `assets/gitignore/claude-skill.gitignore` deckte Python-Bytecode nicht ab,
  obwohl Skill-Repos regelmässig Skripte in `scripts/` ausliefern — sie ist um
  `__pycache__/`, `*.py[cod]` und `.pytest_cache/` ergänzt, damit derselbe
  Fehler nicht in jedes künftige Skill-Repo weitergereicht wird.

- **Neuer Check `C8` — Versionsanker gegen die oberste CHANGELOG-Release-Überschrift.**
  Die Version steht je nach Repo an bis zu vier Orten: im Badge jeder
  README-Sprachfassung, in einer `**Version:**`-Zeile, im `version`-Feld von
  `.github/repo-meta.yml` — und im CHANGELOG. Zusammengehalten hat sie nichts,
  und entsprechend sind sie auseinander: Im Audit-Repo des Portfolios stand die
  Statuszeile drei Releases lang auf `v1.0.0`, in diesem Repo mussten beim
  v1.2.0-Release drei Anker von Hand nachgezogen werden.

  **WARN, nicht ERROR.** Eine veraltete Versionsangabe ist ein Doku-Mangel und
  kein Baufehler, und der Check läuft über ein gewachsenes Portfolio, in dem ein
  ERROR reihenweise blockieren würde, ohne dass etwas kaputt ist.

  Still, wo es nichts zu vergleichen gibt: ohne `CHANGELOG.md`, ohne
  Release-Überschrift (Repo vor dem ersten Release) oder ohne jeden Anker. Der
  letzte Fall wird als INFO gemeldet — «nichts gefunden» soll nicht wie «alles
  in Ordnung» aussehen. Die READMEs kommen per `glob("README*.md")`, damit eine
  dritte Sprachfassung keinen weiteren Eingriff braucht.

  Jeder Ankertyp einzeln gegengeprobt: Badge, `**Version:**`-Zeile,
  `repo-meta.yml`, beide Sprachfassungen gleichzeitig, gar kein Anker, und ein
  Repo vor dem ersten Release.

- **Dieses Repo stuft `C8` zum Fehlschlag hoch.** Es ist die Quelle der Regel,
  und beim letzten Release hat genau diese Drift zugeschlagen. Die CI liest die
  `--json`-Ausgabe des eigenen Validators und scheitert, sobald dort ein
  C8-Finding oberhalb von INFO steht — eine Implementation, zwei Schweregrade,
  statt derselben Logik an zwei Stellen.

## [1.2.0] - 2026-08-01

Zwei Fehlalarme in E1, beide derselben Klasse: Der Check las Dokumentation als
Code, und er las nur eine von zwei Sprachfassungen. Dazu die `.gitattributes`,
die diesem Repo als letztem im Portfolio fehlte.

### Added
- **`.gitattributes` pinning text files to LF.** This repository was the last in the portfolio without one. It matters more here than elsewhere: `assets/` holds the templates copied into every repository created with this skill — gitignores, workflows, READMEs, the MIT licence — so a template that picks up CRLF seeds it into each repository it starts. The index was already LF-clean, so nothing was rewritten; this keeps a Windows checkout from introducing CRLF on a later commit. Covers `.toml` and `*.gitignore` beyond the portfolio's usual set, because both exist here, and the file itself, so the one file that states the rules is not the one without them.

### Fixed
- **E1 reads the AST instead of the raw text, so a docstring example is no longer mistaken for a registered tool.** `list_tool_names` matched `@<x>.tool(...)` directly above a `def` with a regex over the file's raw text, which cannot tell code from documentation. A reference file whose module docstring showed the usage pattern was therefore reported as registering a tool: `mcp-data-source-probe-skill` — a skill repository with no tools at all — was flagged for an undocumented `my_tool` for as long as that example existed. Verified against that exact file: two hits before, none after.
- **E1 no longer loses tools whose decorator arguments contain a parenthesis.** The same regex bounded the argument list with `[^)]*` and stopped at the first `)`, so `@mcp.tool(name=" ".join(...))` or a `description` containing a parenthetical went unseen. Both cases are covered by a fixture; the old implementation found four tools where five exist and invented a fifth, the new one finds exactly the five.
- Files that fail to parse — templates with placeholders, fixtures, Python 2 remnants — are skipped for E1 and **named in an INFO line**. A path that nothing checks and nobody sees is the same error one level up.
- **E1 reads every README language version, not only `README.md`.** Since the portfolio went bilingual, a tool documented in `README.de.md` alone was reported as undocumented — the same class of false alarm as the docstring example, one function further down. The READMEs come from `glob("README*.md")` rather than a fixed pair, so a third language is covered without another edit.
- **«Documented nowhere» and «missing from one language version» are now separate findings.** The old check collapsed them into one message, which made the real gap and the translation gap indistinguishable. A tool absent from every README still reports `Tools nicht im README dokumentiert`; one that exists in some but not all reports `<file>: Tools fehlen in dieser Sprachfassung`, naming the file that lacks it. Verified on a fixture with all three states — documented in both, in German only, in neither.

## [1.1.0] - 2026-07-31

### Added
- Step 0 "Session intake": title, description, and topics are collected once, bundled in a single question, before any file is written; persisted to `.github/repo-meta.yml` as the single source of truth, including `author_label` (never normalized, rule D1), `default_branch`, `pypi_package`, and `mcp_name`
- Backend detection before any GitHub operation, with an operation-by-operation mapping for `gh` CLI, GitHub MCP tools, and plain `git` — the `gh` CLI does not exist in Claude Code web and remote sessions
- Step 11.1: branch → push → draft PR flow for web sessions, push retry guidance, ephemeral-container warning, and how to continue after a merged PR
- Bundle from the maintained working copy: `assets/` (LICENSE, gitignore, README templates, CI and publish workflows), `references/` (MCP publishing, review rules), `scripts/` (`validate_repo.py`, `check_release_artifacts.py`)
- Steps 8, 9, and 12: CI configuration, mandatory secrets check, and release gate
- Backend section and troubleshooting entry for blocked tag pushes: a session's egress policy can reject `refs/tags/*` with `403` while branch pushes succeed, which leaves the tag local only — and the container is ephemeral
- This repository's own missing standard files: `.gitignore`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/repo-meta.yml`, `ruff.toml`, and a CI workflow that runs the skill's own validator against itself

### Changed
- Three ground rules became four — "collect metadata once" is now rule 1
- Step 1 provides the *proposals* for the intake instead of asking for metadata separately
- Step 10 reads all placeholders from `.github/repo-meta.yml`
- README (EN/DE) rewritten for the 0–12 step structure and the bundle

### Fixed
- `assets/gitignore/claude-skill.gitignore` and `raspberry-pi.gitignore` were missing secret patterns that step 9.1 claims all variants cover (`.env.*`, `*.key`, `*.pem`, `credentials.json`, `secrets.yaml`, `config.local.*`)
- Unused import in `scripts/validate_repo.py` that would have failed the repository's own lint step
- README files documented a `.gitignore` that did not exist in the repository
- LICENSE copyright names the legal copyright holder instead of the GitHub handle (rule C7)

## [1.0.0] - 2025-03-09

### Added
- Initial release
- 10-step workflow: project type detection, metadata, bilingual READMEs, LICENSE, .gitignore, CHANGELOG, gh CLI, commits, releases
- Bilingual README templates (English + German, Swiss spelling conventions)
- Project-type-specific .gitignore templates (MCP server, Node.js, Raspberry Pi, Claude Skill)
- Full `gh` CLI command reference for repo creation, topic setting, and releases
- Conventional Commits and Semantic Versioning guidance
- Quality checklist for first push and releases
