# Enforcing rules across many repositories: rulesets and IaC

*English translation of `repo-governance.md`, which stays the canonical version.*

Read this file when a rule should apply **across a portfolio** rather than to a
single repository — protected branches, required reviews, forbidden file types,
a mandatory workflow. For one new repository, steps 8–10 of `SKILL.md` are
enough.

Unlike `mcp-publishing.md` and `review-rules.md`, this file does not come from
findings across the portfolio. It comes from GitHub's documentation and from the
source of the Terraform provider. Every statement here was checked against one
of those; anything that was only available second-hand was left out.

---

## First: the question that settles half the rest

**Are the repositories owned by an organization or by a personal account?**

The most interesting mechanisms — one ruleset hitting hundreds of repositories,
target selection by custom properties, required workflows — exist **only at the
organization level** and require a paid organization plan (Team or Enterprise;
GitHub's own pages name different tiers for individual features, so check your
own settings before planning around one).

```bash
gh api "repos/{owner}/{repo}" --jq .owner.type     # "User" or "Organization"
```

**If it returns `User`, the entire organization layer is gone.** There is no
central lever: rulesets are created per repository, and "across the portfolio"
simply means "in every repository, one at a time, by script". That is not a lack
of diligence — it is the boundary of the account type, and the reason that in
such a portfolio `scripts/validate_repo.py` and the templates in `assets/` are
the actual enforcement instruments, not the platform.

---

## Rulesets instead of branch protection

Classic branch protection allows **one** rule per branch. Rulesets solve that
because they layer:

> «if multiple rulesets target the same branch or tag in a repository, the
> rules in each of these rulesets are aggregated»

Where two rules contradict each other, the documentation states that «the most
restrictive version of the rule applies». The practical consequence: rulesets
can be stacked — a base set for all branches, a stricter one for `releases/**`.
You never have to open and rewrite an existing set to add a requirement.

### Three states, and one of them is the way in

| `enforcement` | Effect |
|---|---|
| `active` | rule applies and blocks |
| `evaluate` | rule does **not** block, but every violation is recorded |
| `disabled` | off, without deleting the ruleset |

`evaluate` is how you point a ruleset at a grown portfolio without breaking
every push on day one: observe what *would* have broken, then switch it on. In a
portfolio of repositories of different ages, that is the difference between a
rollout and an outage.

### Bypass

Exceptions go through `bypass_actors` — roles (e.g. repository admin), teams, or
GitHub Apps. Relevant for automated repositories: when an app (release bot,
Dependabot) trips over a rule, the fix is a bypass for **that app**, not
loosening the rule for everyone.

### Push rulesets reach further than the rest

Push rules are not tied to a target branch but to the repository — and per the
documentation they «apply to the entire fork network for a repository, ensuring
every entry point to the repository is protected». For forks there is one
addition: only people with bypass permissions in the root repository have them.

That makes push rules the right instrument against exactly the failures step 9
catches — accidentally committed secrets, oversized files, file types that never
belong in a repository. A push rule applies no matter which branch someone
pushes to.

---

## Target selection at the organization level

Only relevant when the account type is `Organization`. An organization ruleset
selects its repositories through exactly one of three conditions:

| Condition | When |
|---|---|
| `repository_name` | fixed naming patterns |
| `repository_id` | a hand-picked list |
| `repository_property` | **custom properties**, e.g. every repository with `deployed = true` |

The third is the only one that grows with the portfolio: new repositories
inherit the rule as soon as the property is set, without anyone touching the
ruleset. The three are mutually exclusive (declared as `ConflictsWith` in the
provider); branch and tag rulesets additionally take `ref_name`, push rulesets
do not.

---

## Terraform: `integrations/github`

Verified against the provider source, not written from memory:

```hcl
resource "github_organization_ruleset" "example" {
  name        = "example"
  target      = "branch"
  enforcement = "active"          # active | evaluate | disabled

  conditions {
    ref_name {
      include = ["~ALL"]
      exclude = []
    }
  }

  bypass_actors {
    actor_id    = 13473
    actor_type  = "Integration"   # Integration = GitHub App
    bypass_mode = "always"
  }

  rules {
    creation                = true
    deletion                = true
    required_linear_history = true
    required_signatures     = true
  }
}
```

`github_repository_ruleset` has the same shape but without the `repository_*`
conditions — it applies to its own repository. **That is the variant that also
works without an organization**, applied with `for_each` over a list of repos.

Also useful: `github_repository_environment` separates staging from production
and enforces manual approval before critical deployments — the same
`environment: name: pypi` that `assets/workflows/publish.yml` uses and that,
per `references/mcp-publishing.md` (A3), must match the PyPI pending publisher
exactly.

**Limit of the provider:** it does not create workflow YAML inside the
repositories. To roll out CI along with the repository you need a **repository
template** that already contains `ci.yml` and `dependabot.yml` — Terraform
creates the repository from the template, the template supplies the workflows.

---

## Backend: rulesets have no MCP tool

Matching the backend table in `SKILL.md`:

| Operation | A — `gh` | B — MCP tools | C — plain `git` |
|---|---|---|---|
| List rulesets | `gh ruleset list` (`--org`, `--parents`) | **no tool** → settings UI | settings UI |
| View a ruleset | `gh ruleset view` | **no tool** | settings UI |
| Check what applies to a branch | `gh ruleset check` | **no tool** | settings UI |
| Create / change a ruleset | `gh api -X POST /repos/{owner}/{repo}/rulesets` | **no tool** | settings UI |

`gh ruleset check` answers the question that matters day to day — "which rules
apply on *this* branch" — and is the fastest way to explain a rejected push
without needing admin rights.

In web and remote sessions `gh` does not exist (backend B). The rule from
`SKILL.md` applies there: **record it as an open item in
`.github/repo-meta.yml`** and pick it up on the next pass with `gh` — do not
skip it silently.

---

## What does not get centralised

The D rules from `references/review-rules.md` apply here unchanged, and a
central ruleset does not improve them. A ruleset enforcing commit-message or
branch-naming patterns imposes a format across repositories that differ for
good reasons. Before switching one on, ask the same question as before any bulk
pass: **does the rule prevent a real failure, or does it only make things
uniform?**

The approach that leaves no regret: switch on `evaluate`, read for a week what
would have broken, and only then decide — one rule at a time.
