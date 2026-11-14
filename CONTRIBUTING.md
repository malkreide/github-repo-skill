# Contributing

Contributions are welcome — especially rules that come from a real failure.

## What belongs in this skill

Every rule in `SKILL.md` and in `references/` exists because something actually
went wrong: a red CI run without a code change, a registry publish rejected
after the PyPI upload had already succeeded, a README section moved and the
`mcp-name` marker silently going with it.

Please keep that bar: **no precautionary rules.** If you add one, state the
failure it prevents in a sentence.

## How to contribute

1. Fork the repository and create a branch (`feat/…`, `fix/…`, `docs/…`).
2. Make your change.
3. Run the validator against a repository you maintain:
   ```bash
   python3 scripts/validate_repo.py /path/to/some-repo
   ```
   It must not crash, and its findings must still be accurate.
4. Add an entry under `## [Unreleased]` in `CHANGELOG.md`.
5. Open a pull request describing the failure your change addresses.

## Conventions

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
  `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- `SKILL.md` and `references/` are written in German with Swiss spelling
  (`ss` instead of `ß`). Templates in `assets/templates/` stay bilingual.
- Changes to `SKILL.md` that add a step or a rule need a matching entry in both
  `README.md` and `README.de.md`.
- Scripts stay read-only. A script that "cleans up" causes more damage than it
  prevents — that decision is deliberate, see `references/review-rules.md`.

## Local checks

A pre-commit hook runs the same ruff gates as CI — version, lint and format —
against what is staged, i.e. exactly what you are about to commit. Activate it
once per clone:

```bash
python -m pip install -r requirements-lint.txt
git config core.hooksPath .githooks
```

The hook only checks; it never rewrites files. If it blocks, run
`ruff format scripts/` (or fix what `ruff check scripts/` reports), stage the
files again and commit. Commits that touch neither `scripts/`,
`requirements-lint.txt` nor `ruff.toml` skip it. `core.hooksPath` replaces
`.git/hooks`, so hooks you keep there stop running.

It exists because a commit reached `main` with a formatting error that only CI
caught: `ruff check` was green, `ruff format --check` was not.

## Before you push

The skill's own rule applies to this repository too: no push without a secrets
check (Step 9 in `SKILL.md`).
