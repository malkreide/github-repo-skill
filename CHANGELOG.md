# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
