# Bestehende Repos bearbeiten: was nicht angefasst wird und wie geprüft wird

Lies diese Datei, **bevor** du Änderungen an einem bestehenden Repo vornimmst —
besonders bei Durchläufen über mehrere Repos. Sie enthält die Regeln, die im
Durchlauf über 43 Repos jeweils eine falsche Änderung oder einen Fehlalarm
verhindert haben.

**Grundhaltung:** Ein Skript, das «aufräumt», richtet mehr Schaden an, als es
behebt. Der Validator (`scripts/validate_repo.py`) meldet deshalb nur und ändert
nichts. Jede Änderung wird einzeln entschieden.

---

## D — Was NICHT vereinheitlicht werden darf

Diese Abweichungen sind bewusste Entscheidungen.

### D1 — Selbstbezeichnungen

Im Portfolio existieren `Autor`, `Autorin`, `Autor·in` und `Autorin / Autor`.
**Wie sich jemand bezeichnet, ist keine Formatabweichung. Niemals umschreiben** —
auch nicht «zur Konsistenz».

### D2 — Präzisere Titel behalten

`Software Licence` + `Data Licence` statt eines generischen `License` ist
genauer, nicht falsch. Ebenso `Security & Compliance`, wenn die Sektion
zusätzlich ISDS und revDSG abdeckt. Diese Titel bleiben.

### D3 — Deutsche Synonyme

`Mitwirken`, `Mitmachen`, `Beitragen` sind alle legitim. **Nur eine englische
Überschrift in einer deutschen Datei ist ein Fehler** (C6) — nicht die Wahl
zwischen deutschen Synonymen.

---

## E — Prüfregeln für Agenten

### E1 — Tool-Namen gegen den REGISTRIERTEN Namen prüfen

Nutzt ein Server `@mcp.tool(name="gazette_get_publication")`, heisst die
Funktion trotzdem `get_publication`. Eine Prüfung auf `def <name>(` lässt einen
falschen Tool-Namen im README durch.

**Erst feststellen, ob explizite Namen vergeben werden**, dann vergleichen. Der
Validator gibt die registrierten Namen unter `[E1]` aus.

### E2 — Bilder in beiden Syntaxformen suchen

Markdown `![](...)` **und** `<img src="...">`. Badges (`shields.io` und
Verwandte) herausfiltern, sonst gilt jedes Repo als bebildert.

Ein Repo galt fälschlich als demo-los, weil es ein `<img>`-Tag nutzte.

### E3 — Überschriften exakt vergleichen, nicht per Teilstring

`## Sicherheit & Grenzen` ist eine Inhaltssektion, nicht die Dokumentsektion
`## Sicherheit`. Eine Teilstring-Regel hätte die falsche Sektion verschoben.

Der Validator vergleicht gegen eine Allowlist bekannter Varianten (inkl. D2) —
nicht per `in`-Operator.

### E4 — Vor dem Entfernen von Emoji aus Überschriften die Anker prüfen

GitHub generiert Anker aus dem Überschriftstext. Ein entferntes Emoji ändert den
Anker und bricht `](#...)`-Links **stillschweigend**.

```bash
grep -o '](#[^)]*)' README.md          # welche Anker existieren?
```

Ebenso: Emoji-Entfernung auf explizite Unicode-Bereiche beschränken. Eine zu
breite Regel frisst Umlaute — aus `## Verfügbare Tools` wird `## Verfgbare Tools`.

### E5 — Der Default-Branch ist nicht immer `main`

Drei Repos nutzen `master`. Vor jedem Push und in jedem Workflow prüfen:

```bash
git symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's|.*/||'
```

### E6 — C1 meldet die Reihenfolge, zeigt aber nicht immer auf die Ursache

Ein C1-Reihenfolgefehler bedeutet **nicht**, dass der Schlussblock falsch
sortiert ist. In allen drei Fällen, die im Portfolio auftraten, war er korrekt —
gemeldet wurde eine gleich klassifizierte Sektion weiter oben:

| Repo | Auslöser | Zeile vs. Schlussblock |
|---|---|---|
| `swisstopo-mcp` | `## Security & Compliance` (Inhaltssektion) | 324 vs. 618–640 |
| `register-mcp` | `### Security` unter `## Safety & Limits` | 468 vs. 529–548 |
| `seco-labor-mcp` | `## Data License` (Datenlizenz-Sektion) | 216 vs. 237–256 |

Der Titel allein ist nie die Ursache: `news-monitor-mcp` führt
`## Security & Compliance` *als* Schluss-Sektion und ist damit sauber (D2). Der
Fehler entsteht durch **Doppelbelegung** desselben Klassifikationsschlüssels —
einmal als Inhalt, einmal als Dokumentsektion.

Der Validator filtert deshalb vor der Reihenfolgeprüfung zweifach:

1. **Ebene** — nur die flachste Ebene, auf der Schluss-Sektionen stehen. Ein
   `###` unter einer Inhaltssektion ist keine Dokumentsektion. Nicht hart `##`,
   sonst gilt ein durchgehend tiefer gegliedertes README als blockfrei.
2. **Mehrfachnennung** — die *letzte* Nennung gewinnt.

Über die 99 READMEs des Portfolios räumt **Last-Wins allein bereits alle drei
Fälle ab** — auch `register-mcp`, weil das spätere `## Security` den Unterpunkt
ohnehin verdrängt. Der Ebenenfilter trägt erst, wenn *keine* spätere
Dokumentsektion folgt: dann hält der Unterpunkt die Klassifikation allein und
würde ungefiltert einen Reihenfolgefehler erfinden. Genau dieser Fall steht als
eigenes Fixture in `scripts/test_c1.py` — ohne ihn war der Ebenenfilter
entfernbar, ohne dass ein Test rot wurde.

Die Existenzprüfung (`Sektion '…' fehlt`) bleibt bewusst ebenenblind: eine
vorhandene Sektion fälschlich als fehlend zu melden wäre schlimmer.

**Vor dem Umsortieren also erst prüfen, wo die gemeldete Sektion steht:**

```bash
grep -n "^#\{1,4\} " README.md | grep -iE "contribut|security|licen|author"
```

Steht der Schlussblock bereits richtig, ist Umsortieren der falsche Fix — er
zerstört die korrekte Reihenfolge. Zu klären ist dann die Doppelbelegung.

---

## F2 — 403 beim Push in ein archiviertes Repo

Lesen funktioniert, Schreiben nicht, deterministisch. **Bevor Berechtigungen
debuggt werden: Archiv-Status prüfen.**

```bash
gh repo view <owner>/<repo> --json isArchived,defaultBranchRef
```

Entarchivieren: `gh repo unarchive <owner>/<repo>`

---

## Ablauf für einen Durchlauf über mehrere Repos

1. `python3 scripts/validate_repo.py <repo>` je Repo, Ausgaben sammeln
2. ERROR-Findings sichten — **nicht blind fixen**, gegen D1–D3 gegenprüfen
3. Änderungen einzeln vornehmen, pro Repo committen
4. Bei README-Änderungen: Marker-Anzahl vorher/nachher vergleichen (A1)
5. Vor dem Push: Default-Branch (E5) und Archiv-Status (F2) prüfen
