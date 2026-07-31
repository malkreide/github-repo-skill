# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Step 0 "Session-Intake": title, description, and topics are collected once, bundled in a single question, before any file is written
- Source lookup order so known values are never re-asked (session history → `.github/repo-meta.yml` → existing repo via `gh repo view` → project files → derived proposal)
- `.github/repo-meta.yml` as the single source of truth for repo metadata, reused by README generation, `gh repo create`, and topic setting
- Field-to-usage mapping table and intake items in the quality checklist

### Changed
- Step 1 now provides the *proposals* for the intake instead of asking for metadata separately
- Step 8 (`gh` CLI) reads all placeholders from `.github/repo-meta.yml` instead of prompting again

## [1.0.0] - 2025-03-09

### Added
- Initial release
- 10-step workflow: project type detection, metadata, bilingual READMEs, LICENSE, .gitignore, CHANGELOG, gh CLI, commits, releases
- Bilingual README templates (English + German, Swiss spelling conventions)
- Project-type-specific .gitignore templates (MCP server, Node.js, Raspberry Pi, Claude Skill)
- Full `gh` CLI command reference for repo creation, topic setting, and releases
- Conventional Commits and Semantic Versioning guidance
- Quality checklist for first push and releases
