# Regeln über viele Repos hinweg durchsetzen: Rulesets und IaC

Lies diese Datei, wenn eine Regel **portfolioweit** gelten soll statt in einem
Repo — geschützte Branches, erzwungene Reviews, verbotene Dateitypen, ein
Pflicht-Workflow. Für ein einzelnes neues Repo genügen die Schritte 8–10 der
`SKILL.md`.

Anders als `mcp-publishing.md` und `review-rules.md` stammt diese Datei nicht
aus Portfolio-Befunden, sondern aus der GitHub-Dokumentation und dem Quellcode
des Terraform-Providers. Die Angaben sind gegengeprüft; wo eine Aussage nur aus
zweiter Hand vorlag, steht sie nicht drin.

---

## Zuerst: die Frage, die den halben Rest erledigt

**Gehören die Repos einer Organisation oder einem persönlichen Konto?**

Die interessantesten Mechanismen — ein Regelsatz, der hunderte Repos auf
einmal trifft, Zielauswahl über Custom Properties, erzwungene Workflows —
existieren **nur auf Organisationsebene** und setzen einen bezahlten
Organisationsplan voraus (Team bzw. Enterprise; die Doku-Seiten nennen für
einzelne Funktionen unterschiedliche Stufen, deshalb vor dem Planen in den
eigenen Settings nachsehen).

```bash
gh api "repos/{owner}/{repo}" --jq .owner.type     # "User" oder "Organization"
```

**Bei `User` fällt die gesamte Organisationsebene weg.** Dann gibt es keinen
zentralen Hebel: Rulesets werden pro Repo angelegt, und «portfolioweit» heißt
schlicht «in jedem Repo einzeln, per Skript». Das ist kein Mangel an
Sorgfalt, sondern die Grenze des Kontotyps — und der Grund, warum in so einem
Portfolio `scripts/validate_repo.py` und die Vorlagen aus `assets/` die
eigentlichen Durchsetzungsinstrumente sind, nicht die Plattform.

---

## Rulesets statt Branch Protection

Klassische Branch Protection erlaubt **eine** Regel pro Branch. Rulesets lösen
das, weil sie sich überlagern:

> «if multiple rulesets target the same branch or tag in a repository, the
> rules in each of these rulesets are aggregated»

Widersprechen sich zwei Regeln, gilt laut Doku «the most restrictive version of
the rule applies». Praktische Folge: Regelsätze lassen sich schichten — ein
Basissatz für alle Branches, ein schärferer für `releases/**`. Man muss keinen
Satz aufmachen und umschreiben, um eine Anforderung zu ergänzen.

### Drei Zustände, und einer davon ist der Einstieg

| `enforcement` | Wirkung |
|---|---|
| `active` | Regel greift und blockiert |
| `evaluate` | Regel greift **nicht**, aber jeder Verstoß wird protokolliert |
| `disabled` | aus, ohne den Regelsatz zu löschen |

`evaluate` ist der Weg, einen Regelsatz auf ein gewachsenes Portfolio
loszulassen, ohne am ersten Tag jeden Push zu brechen: erst beobachten, was
gebrochen *wäre*, dann scharf schalten. Bei einem Portfolio mit
unterschiedlich alten Repos ist das der Unterschied zwischen einer Einführung
und einem Ausfall.

### Bypass

Ausnahmen laufen über `bypass_actors` — Rollen (z. B. Repo-Admin), Teams oder
GitHub Apps. Wichtig für automatisierte Repos: Wenn eine App (Release-Bot,
Dependabot) an einer Regel scheitert, ist der Bypass für **diese App** die
Lösung, nicht das Aufweichen der Regel für alle.

### Push-Rulesets greifen weiter als der Rest

Push-Regeln hängen nicht am Ziel-Branch, sondern am Repo — und laut Doku
«apply to the entire fork network for a repository, ensuring every entry point
to the repository is protected». Für Forks gilt zusätzlich: Bypass-Rechte hat
nur, wer sie im Wurzel-Repo hat.

Damit sind sie das richtige Mittel gegen genau die Fehler, die Schritt 9
abfängt — versehentlich committete Secrets, übergroße Dateien, Dateitypen, die
nie ins Repo gehören. Eine Push-Regel wirkt unabhängig davon, auf welchen
Branch jemand pusht.

---

## Zielauswahl auf Organisationsebene

Nur relevant, wenn der Kontotyp `Organization` ist. Ein Organisations-Ruleset
wählt seine Repos über genau eine der drei Bedingungen:

| Bedingung | Wann |
|---|---|
| `repository_name` | feste Namensmuster |
| `repository_id` | eine handverlesene Liste |
| `repository_property` | **Custom Properties**, z. B. alle Repos mit `deployed = true` |

Die dritte ist die einzige, die mitwächst: neue Repos erben die Regel, sobald
die Property gesetzt ist — ohne dass jemand den Regelsatz anfasst. Die drei
schließen einander aus (im Provider als `ConflictsWith` hinterlegt); für
Branch- und Tag-Rulesets kommt `ref_name` hinzu, für Push-Rulesets nicht.

---

## Terraform: `integrations/github`

Verifiziert am Quellcode des Providers, nicht aus dem Gedächtnis:

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

`github_repository_ruleset` hat dieselbe Form, aber ohne die
`repository_*`-Bedingungen — es gilt für sein eigenes Repo. **Das ist die
Variante, die auch ohne Organisation funktioniert**, angewandt per `for_each`
über eine Repo-Liste.

Weiter nützlich: `github_repository_environment` trennt Staging von Production
und erzwingt manuelle Freigaben vor kritischen Deployments — dasselbe
`environment: name: pypi`, das `assets/workflows/publish.yml` verwendet und das
laut `references/mcp-publishing.md` (A3) beim Pending Publisher exakt
übereinstimmen muss.

**Grenze des Providers:** Er legt keine Workflow-YAML in den Repos an. Wer CI
mitausrollen will, braucht ein **Repository-Template**, das `ci.yml` und
`dependabot.yml` bereits enthält — Terraform erzeugt das Repo aus dem Template,
den Inhalt der Workflows liefert das Template.

---

## Backend: Rulesets haben kein MCP-Tool

Passend zur Backend-Tabelle in `SKILL.md`:

| Operation | A — `gh` | B — MCP-Tools | C — nur `git` |
|---|---|---|---|
| Rulesets auflisten | `gh ruleset list` (`--org`, `--parents`) | **kein Tool** → Settings-UI | Settings-UI |
| Ruleset ansehen | `gh ruleset view` | **kein Tool** | Settings-UI |
| Prüfen, was auf einem Branch gilt | `gh ruleset check` | **kein Tool** | Settings-UI |
| Ruleset anlegen / ändern | `gh api -X POST /repos/{owner}/{repo}/rulesets` | **kein Tool** | Settings-UI |

`gh ruleset check` beantwortet die Frage, die im Alltag zählt — «welche Regeln
greifen auf *diesem* Branch» — und ist der schnellste Weg, einen abgelehnten
Push zu erklären, ohne Admin-Rechte zu brauchen.

In Web- und Remote-Sessions existiert `gh` nicht (Backend B). Dort gilt die
Regel aus `SKILL.md`: **als offenen Punkt in `.github/repo-meta.yml` vermerken**
und beim nächsten Durchlauf mit `gh` nachziehen — nicht stillschweigend
übergehen.

---

## Was nicht zentralisiert wird

Die D-Regeln aus `references/review-rules.md` gelten hier unverändert und
werden durch einen zentralen Regelsatz nicht besser. Ein Ruleset, das
Commit-Message- oder Branch-Namensmuster erzwingt, ist ein Formatzwang über
Repos hinweg, die aus verschiedenen Gründen verschieden sind. Vor dem
Scharfschalten dieselbe Frage wie bei jedem Sammel-Lauf: **verhindert die Regel
einen realen Fehler, oder vereinheitlicht sie nur?**

Der Weg, der ohne Reue bleibt: `evaluate` einschalten, eine Woche lesen, was
gebrochen wäre, und erst dann entscheiden — je Regel einzeln.
