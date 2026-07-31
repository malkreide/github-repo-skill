# MCP-Server auf PyPI und in die MCP-Registry publizieren

Lies diese Datei, sobald ein `*-mcp`-Repo publiziert oder für einen Release
vorbereitet wird. Jeder Punkt entspricht einem real aufgetretenen Fehler aus
einem Durchlauf über 43 Repos — keiner davon ist vorsorglich.

**Die Reihenfolge ist entscheidend.** Drei der vier Blocker fallen erst beim
Publish auf, also nachdem der PyPI-Upload bereits erfolgreich war. PyPI-Releases
sind unveränderlich: was dort steht, lässt sich nicht korrigieren, sondern nur
durch eine neue Version ersetzen.

---

## Vor dem ersten Release: Reihenfolge

1. `mcp-name`-Marker ins README (A1)
2. `server.json` mit `description` ≤ 100 Zeichen (A2)
3. **Pending Publisher auf PyPI anlegen** (A3) — vor dem ersten Workflow-Lauf
4. Tag setzen, Workflow läuft, Release-Gate prüft das gebaute Artefakt (A4)

---

## A1 — `mcp-name`-Marker vor dem ersten Release

Die MCP-Registry prüft die PyPI-Paket-Ownership über einen Marker im
**publizierten** README:

```markdown
<!-- mcp-name: io.github.<github-user>/<server> -->
```

Er muss in genau der Datei stehen, die `pyproject.toml` als `readme` deklariert
— in der Regel `README.md`. **Ein Marker nur in `README.de.md` zählt nicht**,
weil diese Datei nicht in die Wheel-METADATA wandert.

Fehlt der Marker beim Release, kostet das Nachrüsten einen Versionssprung. Das
ist in zwei Repos passiert.

**Beim Bearbeiten von READMEs:** Marker-Anzahl vor und nach jeder Änderung
vergleichen. Ein Blockverschieben am Dateiende hat den Marker einmal
stillschweigend mitgerissen.

```bash
grep -c 'mcp-name:' README.md          # vor der Änderung
# ... Änderung ...
grep -c 'mcp-name:' README.md          # muss identisch sein
```

Der Validator gibt die Anzahl bei jedem Lauf aus:
`python3 scripts/validate_repo.py .`

## A2 — `server.json` `description` ≤ 100 Zeichen

Die Registry lehnt längere Beschreibungen ab:
`422 expected length <= 100`. Der Fehler erscheint **erst beim Publish, nach
erfolgreichem PyPI-Upload**.

```bash
python3 -c "import json;d=json.load(open('server.json'))['description'];print(len(d))"
```

Im CI verifiziert `scripts/check_release_artifacts.py`.

## A3 — Pending Publisher vor dem Erst-Release

Trusted Publishing über OIDC braucht auf PyPI einen Eintrag. Für ein noch nicht
existierendes Projekt geht das nur als *Pending Publisher*, angelegt **bevor**
der Workflow das erste Mal läuft. Sonst:

```
invalid-publisher: valid token, but no corresponding publisher
```

Felder exakt (PyPI → Account settings → Publishing → Add a pending publisher):

| Feld | Wert |
|---|---|
| PyPI Project Name | `<paketname>` |
| Owner | `<github-user>` |
| Repository name | `<repo>` |
| Workflow name | **Dateiname**, z. B. `publish.yml` — nicht der Anzeigename aus `name:` |
| Environment name | Wert aus `environment: name:` im Workflow, z. B. `pypi` |

**Environment leer lassen ist der häufigste Fehler**, wenn der Workflow eines
deklariert. Die mitgelieferte `assets/workflows/publish.yml` deklariert `pypi`.

## A4 — Tags zeigen auf den Stand, der publiziert wird

Ein Re-Run eines alten, fehlgeschlagenen Tag-Laufs checkt den **alten** Commit
aus und reproduziert denselben Fehler — der Fix im Default-Branch ist dabei
unsichtbar.

Nach einem Fix entweder:

- `workflow_dispatch` auf dem Default-Branch auslösen, oder
- einen neuen Tag setzen (`v1.0.1`).

`skip-existing: true` im PyPI-Step verhindert Doppel-Uploads, wenn ein Teil des
Laufs schon durchgelaufen war.

---

## Nach dem Publish: F1 — PyPI-JSON-API liefert gecachte Antworten

Ein Publish kann erfolgreich sein, während `/pypi/<paket>/json` noch die alte
Version zeigt. **Nicht** anhand der JSON-API debuggen. Gegenprüfen gegen:

```bash
curl -s https://pypi.org/simple/<paket>/ | grep -o '<paket>-[0-9.]*'
```

---

## `server.json` — Minimalgerüst

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-07-09/server.schema.json",
  "name": "io.github.<github-user>/<server>",
  "description": "≤ 100 Zeichen, Englisch, ohne Punkt am Ende",
  "version": "1.0.0",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "<paketname>",
      "version": "1.0.0",
      "transport": { "type": "stdio" }
    }
  ]
}
```

`version` muss mit `pyproject.toml` und dem Git-Tag übereinstimmen — der
Validator und das Release-Gate prüfen das beide.
