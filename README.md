# github-repo-skill

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Skill](https://img.shields.io/badge/claude-skill-orange)

> A Claude skill that creates, reviews, and publishes professional GitHub repositories — bilingual READMEs, secrets check, reproducible CI, and a release gate.

[🇩🇪 Deutsche Version](README.de.md)

## Overview

This skill enables Claude to create and maintain complete GitHub repositories for
technical projects such as MCP servers, Claude skills, Raspberry Pi projects, and
Python libraries. It generates bilingual README files (English + German), standard
files (LICENSE, .gitignore, CHANGELOG, SECURITY, CONTRIBUTING), and guides through
the full workflow from the first commit to a PyPI or MCP registry release.

Every rule in it comes from a failure that actually occurred — most of them during
a review pass across 43 repositories. None are precautionary.

## Features

- **One-time session intake** — title, description, and topics are collected once,
  bundled, before the first file is written, and persisted to `.github/repo-meta.yml`
- **Backend-agnostic** — works with the `gh` CLI, with GitHub MCP tools (Claude Code
  on the web, where `gh` does not exist), or with plain `git`
- **Secrets check before the first push** — ignore rules, automated scan, history
  remediation, and a context-specific check for public sector projects
- **Reproducible CI** — pinned linter rule sets, per-subproject configuration, no
  blind assertions in tests
- **Release gate** — validates artifacts before an immutable PyPI upload
- Bilingual README generation (English main + German translation), cross-linked
- Review rules for existing repositories: report, never "tidy up"
- Two read-only validation scripts and ready-to-copy workflow, gitignore, and
  README templates

## Prerequisites

- Claude with skill support (Claude Code, or the skills directory of your setup)
- Git installed and configured
- Python 3.9+ for the validation scripts
- Optional: [GitHub CLI (`gh`)](https://cli.github.com/) — without it the skill
  falls back to GitHub MCP tools or plain `git`
- Optional: [`gitleaks`](https://github.com/gitleaks/gitleaks) for the automated
  secrets scan

## Installation

```bash
# Clone this repository
git clone https://github.com/malkreide/github-repo-skill.git

# Copy the whole bundle — the skill reads assets/, references/, and scripts/
cp -r github-repo-skill /path/to/your/skills/github-repo
```

## Usage / Quickstart

Once installed, trigger the skill with phrases like:

- *"Create a GitHub repo for this project"*
- *"Make this GitHub-ready"*
- *"Why is CI red without a code change?"*
- *"Publish this MCP server to the registry"*

Claude starts with the session intake, then walks through file generation, the
secrets check, and the repository setup.

Run the validator against an existing repository at any time:

```bash
python3 scripts/validate_repo.py /path/to/repo
# exit code 0 = no errors, 1 = at least one error
```

## Project Structure

```
github-repo-skill/
├── SKILL.md                          ← The skill (main file)
├── assets/
│   ├── LICENSE-MIT.txt
│   ├── gitignore/                    ← python, node, raspberry-pi, claude-skill
│   ├── templates/                    ← README.md, README.de.md
│   └── workflows/                    ← ci.yml, publish.yml
├── references/
│   ├── mcp-publishing.md             ← PyPI + MCP registry, read before a release
│   ├── review-rules.md               ← read before touching an existing repo
│   └── rpi-kernel-build.md · .de.md  ← Raspberry Pi kernel build, module, overlay
├── scripts/
│   ├── validate_repo.py              ← structure and documentation check
│   └── check_release_artifacts.py    ← release gate
├── .github/repo-meta.yml             ← this repo's own intake result
├── README.md · README.de.md
├── SECURITY.md · CONTRIBUTING.md
├── LICENSE · .gitignore · CHANGELOG.md
```

## What the Skill Covers

An intake step, twelve working steps, and a review track:

| Step | Content |
|---|---|
| 0 | **Session intake** — collect metadata once, persist to `.github/repo-meta.yml` |
| 1–2 | Project type, naming conventions, file structure |
| 3–4 | README.md (EN) and README.de.md (DE), cross-linked |
| 5–7 | LICENSE, .gitignore, CHANGELOG |
| 8 | Python and CI configuration — the three causes of CI failures without a code change |
| 9 | Secrets check before the first push |
| 10 | Repository creation and configuration |
| 11 | Commit workflow, including the branch → draft PR flow for web sessions |
| 12 | Release with gate, tag, and version-scoped release notes |
| — | Existing repositories: review rules, quality checklist, troubleshooting table |

Before any GitHub operation the skill determines its backend (`gh` CLI, MCP tools,
or plain `git`) and maps each operation accordingly. Anything the current backend
cannot do is recorded as an open item instead of being skipped silently.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). The bar for a
new rule: name the failure it prevents.

## Security

See [SECURITY.md](SECURITY.md) for the reporting process and for using the skill
safely.

## License

MIT License — see [LICENSE](LICENSE)

## Author

malkreide · [github.com/malkreide](https://github.com/malkreide)
