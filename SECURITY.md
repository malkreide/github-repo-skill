# Security Policy

## Scope

This repository contains a Claude skill: Markdown instructions, file templates,
and two read-only Python scripts (`scripts/validate_repo.py`,
`scripts/check_release_artifacts.py`). It is not a service and processes no
user data. Neither script writes to the repository it inspects — both report
only.

## Reporting a vulnerability

Report security-relevant issues — for example a template that would leak
credentials, or a script that could be made to execute untrusted input —
through GitHub's private reporting: **Security → Report a vulnerability** in
this repository.

Please do not open a public issue for anything that could expose secrets in
someone else's repository.

Expect an acknowledgement within 14 days.

## Using this skill safely

- The skill instructs Claude to run a secrets check before the first push
  (Step 9). Treat it as mandatory: Git history cannot be made private after
  the fact.
- `assets/gitignore/*` covers `.env`, `*.key`, `*.pem`, `credentials.json`,
  `secrets.yaml`, and `config.local.*`. If you adapt a template, keep those
  patterns.
- A pushed secret counts as compromised. Rotate it first, clean the history
  second (Step 9.5).
- `.github/repo-meta.yml` is meant for public metadata only — never store
  tokens, internal hostnames, or personal data in it.
