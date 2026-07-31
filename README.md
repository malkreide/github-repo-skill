# github-repo-skill

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Skill](https://img.shields.io/badge/claude-skill-orange)

> A Claude SKILL.md that creates and maintains professional GitHub repositories with bilingual README files, standard files, and a full `gh` CLI workflow.

[🇩🇪 Deutsche Version](README.de.md)

## Overview

This skill enables Claude to create complete, professional GitHub repositories for technical projects such as MCP servers, Claude Skills, Raspberry Pi projects, and Python libraries. It generates bilingual README files (English + German), standard files (LICENSE, .gitignore, CHANGELOG), and guides through the full `gh` CLI workflow — from initial setup to releases.

The skill is designed for developers who want consistent, well-documented repositories without having to remember every convention and command every time.

## Features

- One-time session intake: title, description, and topics are collected once, up front, and persisted to `.github/repo-meta.yml` instead of being asked again in every step
- Automatic project type detection (MCP server, Claude Skill, Raspberry Pi, Python library)
- Bilingual README generation (English main + German translation), cross-linked
- Repository metadata: name, description, and topics/tags per convention
- Standard files: MIT LICENSE, project-type-specific .gitignore, CHANGELOG.md
- Full `gh` CLI workflow: repo creation, topic setting, updates, releases
- Conventional Commits guidance and Semantic Versioning
- Quality checklist before first push and before every release

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated
- Git installed and configured
- A GitHub account

## Installation

Copy `SKILL.md` into your Claude Skills folder:

```bash
# Clone this repository
git clone https://github.com/malkreide/github-repo-skill.git

# Copy skill to your Claude skills directory
cp github-repo-skill/SKILL.md /path/to/your/skills/github-repo/SKILL.md
```

## Usage / Quickstart

Once installed as a Claude skill, trigger it with phrases like:

- *"Create a GitHub repo for this project"*
- *"Make this GitHub-ready"*
- *"How do I publish this on GitHub?"*
- *"Generate README files for my MCP server"*

Claude will then guide through all steps: metadata, file generation, and `gh` CLI commands.

## Project Structure

```
github-repo-skill/
├── SKILL.md          ← The Claude skill (main file)
├── README.md         ← This file (English)
├── README.de.md      ← German version
├── LICENSE           ← MIT License
├── .gitignore        ← Skill-appropriate ignores
└── CHANGELOG.md      ← Version history
```

## What the Skill Covers

The skill walks through an intake step and 10 working steps:

0. **Session intake** — collect title, description, topics, and visibility once, bundled, and persist them to `.github/repo-meta.yml`
1. **Project type detection** — MCP server, Claude Skill, Raspberry Pi, Python library
2. **Repo metadata** — name conventions, description, topics/tags
3. **README.md (EN)** — full template with badges, all required sections
4. **README.de.md** — German translation, Swiss spelling conventions
5. **LICENSE** — MIT standard
6. **.gitignore** — project-type-specific
7. **CHANGELOG.md** — Keep a Changelog format + Semantic Versioning
8. **`gh` CLI workflow** — repo creation, auth check, topic setting
9. **Commit workflow** — Conventional Commits, post-commit checklist
10. **Release workflow** — Git tags, `gh release create`, badge updates

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## License

MIT License — see [LICENSE](LICENSE)

## Author

malkreide · [github.com/malkreide](https://github.com/malkreide)
