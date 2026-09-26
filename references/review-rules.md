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

### E7 — Emoji ist nicht «Zeichen über U+2000»

E4 warnt davor, dass eine zu breite Emoji-Regel Umlaute frisst. Dieselbe Regel
war auch in die andere Richtung zu breit: sie nahm ganze Unicode-Blöcke pauschal
und meldete `The UID join — Zefix ↔ Amtsblatt` (register-mcp) als Emoji.

Unicode unterscheidet zwei Klassen, und genau daran verläuft die Grenze:

| Klasse | Beispiele | zählt als Emoji |
|---|---|---|
| Emoji-Standarddarstellung | `⚡` `✨` `⭐` `✅` | für sich allein |
| Text-Standarddarstellung | `⚖` `❄` `✈` `↔` `✓` | erst mit VS16 (U+FE0F) |

`↔` ist Typografie, `↔️` ist ein Emoji — derselbe Codepoint, ein unsichtbares
Zeichen Unterschied. Im Portfolio gegengeprüft: die vorkommenden
Textdarstellungs-Emoji (`⚖ ⚙ ⛰ ✈ ❄`) tragen **ausnahmslos** VS16, die
Default-Emoji (`⚡ ✨`) stehen **ausnahmslos** nackt.

Zwei Bereiche der alten Regel waren besonders grob:

- `U+2190–U+21FF` — der komplette Pfeilblock, also `←` `→` `↔` inklusive.
- `U+24C2–U+1F251` — ein einzelner Bereich, der nebenbei **den gesamten
  CJK-Block** verschluckte: `漢` galt als Emoji.

Beim Ändern der Erkennung zusätzlich beachten: `normalise()` benutzt dieselbe
Regex zum Strippen. Wird der Variantenselektor nicht mitgenommen, bleibt er als
unsichtbarer Rest im Titel stehen und der exakte Vergleich (E3) scheitert an
einem Zeichen, das man nicht sieht. `scripts/test_emoji.py` hält alle drei
Seiten fest — Fehlalarm, Übersehen und Strip-Hygiene.

### E8 — Links auf fremde Inhalte zeigen auf einen Tag, nicht auf `main`

Ein Link, der etwas über den Inhalt eines anderen Repos **behauptet** («seine
Regel 5», «Schritt 1.4»), kann auf `main` aufhören zu stimmen, ohne dass sich
im eigenen Repo ein Byte ändert — und ohne dass es jemand merkt. Auf einen Tag
gepinnt kann er nur veralten, und das ist sichtbar.

Gemessen im `mcp-continuous-auditor`: Drei Skill-Repos wurden in
`mcp-audit-skill` zusammengeführt und archiviert. Die Links im README lösten
weiter auf und sahen intakt aus — sie zeigten auf einen Stand, den niemand
mehr pflegt. Das ist die schlimmere Hälfte eines toten Links: ein 404 ist
wenigstens lesbar.

Umgekehrt gilt: Ein Pin auf einen Tag braucht jemanden, der ihn hebt. Wer auf
Tags pinnt, lässt einen wöchentlichen Lauf prüfen, ob der Tag noch der neueste
Release ist (Muster: `audit-pin-drift.yml` im Auditor) — sonst ist der Pin
korrekt und trotzdem zwei Versionen alt.

---

## F2 — 403 beim Push in ein archiviertes Repo

Lesen funktioniert, Schreiben nicht, deterministisch. **Bevor Berechtigungen
debuggt werden: Archiv-Status prüfen.**

```bash
gh repo view <owner>/<repo> --json isArchived,defaultBranchRef
```

Entarchivieren: `gh repo unarchive <owner>/<repo>`

---

## F3 — Ein abgebrochener Sweep ist kein Teilergebnis

Ein Durchlauf über das Portfolio reisst das Rate-Limit: viele Repos mal mehrere
API-Aufrufe. Real beobachtet in **Backend B**, mitten in einer Verifikation —
ein Listen-Aufruf brach ab mit «API rate limit already exceeded for user ID …»,
während andere Endpunkte noch antworteten. Von aussen sah der Lauf aus, als
liefe er weiter.

**Gefährlich ist nicht der Fehler, sondern der Bericht danach.** Ein Sweep, der
bei Repo 19 von 32 abbricht, liefert eine Tabelle mit 18 Zeilen, und nichts
darin sagt, dass 13 fehlen. Wer sie liest, liest sie als vollständig.

**Regel:** Jeder Lauf über mehrere Repos führt mit, welche Repos er **nicht**
erreicht hat, und der Bericht nennt sie ausdrücklich und zuerst. Nicht erreicht
ist nicht bestanden — dieselbe Unterscheidung wie zwischen «geprüft und nichts
gefunden» und «gar nicht geprüft».

Stand messen, bevor der Lauf beginnt:

| Backend | Vorgehen |
|---|---|
| A (`gh`) | `gh api rate_limit` — Rest-Kontingent vor dem Sweep festhalten |
| B (MCP) | Kein Kontingent-Tool. Stattdessen Aufrufe je Repo zählen und den Lauf so takten, dass er bei einem Abbruch **wiederaufsetzbar** ist: Zwischenstand nach jedem Repo schreiben, nicht erst am Ende. |
| C (weder noch) | Entfällt — ohne API kein Sweep. |

**Transiente Fehler im Transport wiederholen, nicht im Gate tolerieren.** Ein
Lauf über 47 Repos fand nichts und war trotzdem rot: `api.github.com` hatte
eine einzige Verbindung ohne Antwort geschlossen (`RemoteDisconnected`). Das
Gate hatte recht — ein Repo, das geworfen hat, ist kein sauberes Repo. Falsch
war, dass der Aufruf es nur einmal versuchte. Die Reparatur gehört in den
Transport:

- bis zu **3 Versuche** mit Backoff für Verbindungsabbrüche, `429` und `5xx`;
  ein `Retry-After` in Sekunden geht vor dem eigenen Wert;
- **nie** für `403`/`404` — dreimal beantwortet bleibt es dieselbe Antwort, nur
  langsamer;
- ein **Timeout** auf jedem Aufruf, sonst hängt ein halboffener Socket den Lauf
  bis zum Job-Abbruch, ohne zu sagen, bei welchem Repo;
- was nach allen Versuchen unerreicht bleibt, bleibt **unerreicht** und macht
  den Lauf rot. Die Meldung nennt die Zahl der Versuche, damit ein Pechpaket
  von einem wirklich toten Endpunkt unterscheidbar ist.

Das Gate aufzuweichen («ein unerreichtes Repo ist tolerierbar») kauft grüne
Läufe, indem es «niemand hat hingeschaut» und «nichts gefunden» wieder
ununterscheidbar macht — und erzieht dazu, bei Rot den Re-Run-Knopf zu drücken,
statt hinzuschauen.

Bei 403/429 mitten im Lauf, die auch nach den Wiederholungen bleiben:
abbrechen und melden, nicht auf gut Glück weiterlaufen. Primäres Limit und Secondary-/Abuse-Limit sind getrennt; das
zweite schlägt auf Bursts an, nicht auf Volumen — dort hilft Sequenzieren, beim
primären nur Warten.

Bewusst ohne Zahlenwerte: Die Grenzen hängen an Token-Art und Endpunkt und
ändern sich. Eine hier eingetragene Zahl würde als gemessen gelesen, ohne es zu
sein.

---

## Ablauf für einen Durchlauf über mehrere Repos

0. Rate-Limit-Ausgangsstand festhalten und den Lauf wiederaufsetzbar anlegen (F3)
1. `python3 scripts/validate_repo.py <repo>` je Repo, Ausgaben sammeln
2. ERROR-Findings sichten — **nicht blind fixen**, gegen D1–D3 gegenprüfen
3. Änderungen einzeln vornehmen, pro Repo committen
4. Bei README-Änderungen: Marker-Anzahl vorher/nachher vergleichen (A1)
5. Vor dem Push: Default-Branch (E5) und Archiv-Status (F2) prüfen
6. Im Abschlussbericht **zuerst** die nicht erreichten Repos namentlich nennen,
   dann die Befunde — sonst liest sich ein abgebrochener Lauf wie ein
   vollständiger (F3)
