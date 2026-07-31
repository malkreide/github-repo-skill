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
