# MCP-Server auf Protokollstand `2026-07-28`

Lies diese Datei, sobald ein `*-mcp`-Repo angelegt, migriert oder released
wird. **Zielstand für jeden MCP-Server im Portfolio ist die Spezifikation
[`2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28).**
Ein Server auf `2025-11-25` oder älter ist ein offener Migrationspunkt, kein
gleichwertiger Zustand.

Gelesen aus dem
[Changelog der Spezifikation](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
am **2026-09-26**. Wer diese Datei ändert, liest dort nach und setzt das Datum
neu — nicht aus dieser Datei, nicht aus einer Zusammenfassung.

**Warum diese Vorgabe so steht:** Im `mcp-continuous-auditor` wurde die
Spec-Probe zuerst gegen eine *Zusammenfassung* der Spezifikation geschrieben.
Drei der drei Regeln, die sie nannte, waren falsch, dazu eine vierte im
Test-Profil — zwei davon hätten einen vollständig migrierten Server als
Altlast gemeldet. Die Regeln unten stammen aus dem Dokument selbst.

---

## S1 — Was `2026-07-28` am Server verlangt

| Thema | Regel | Quelle (Changelog) |
|---|---|---|
| Handshake | `initialize` / `notifications/initialized` **entfernt**. Jede Anfrage trägt Version, Client-Capabilities und Client-Info in `params._meta` | Major 2 |
| `_meta`-Schlüssel | namespaced: `io.modelcontextprotocol/protocolVersion`, `…/clientCapabilities`, `…/clientInfo`; der Server identifiziert sich in jedem Result mit `…/serverInfo` | Major 2 |
| Sessions | `Mcp-Session-Id` **entfernt**, nicht abgekündigt. Zustand über Aufrufe hinweg nur über vom Server ausgegebene Handles als normale Tool-Argumente | Major 1 |
| Discovery | `server/discover` **MUSS** der Server implementieren; der Client *darf* es aufrufen | Major 3 |
| Benachrichtigungen | HTTP-GET-Endpunkt und `resources/subscribe` ersetzt durch `subscriptions/listen` | Major 4 |
| Entfernt | `ping`, `logging/setLevel`, `notifications/roots/list_changed`; Log-Level pro Anfrage über `io.modelcontextprotocol/logLevel` | Major 5 |
| Results | jedes Result trägt `resultType` (`"complete"` oder `"input_required"`) | Major 8 |
| Listen-Results | `ttlMs` und `cacheScope` (`"public"` \| `"private"`) **Pflicht** auf `tools/list`, `prompts/list`, `resources/list`, `resources/read`, `resources/templates/list`; `tools/list` in deterministischer Reihenfolge | Minor 3, 5 |
| HTTP-Header | `Mcp-Method` und `Mcp-Name` auf Streamable-HTTP-POSTs; `MCP-Protocol-Version` muss dem `_meta`-Wert entsprechen, sonst `400` mit `-32020 HeaderMismatch` | Minor 4, 12 |
| Fehlercodes | Resource not found `-32002` → `-32602`; `-32020`…`-32099` sind der Spezifikation vorbehalten | Minor 6, 12 |
| Resumability | `Last-Event-ID` und SSE-Event-IDs entfernt; abgerissener Stream = Anfrage neu stellen | Major 9 |

**Zwei Details, an denen die erste Spec-Probe gescheitert ist:** `_meta` steht in
`params`, nicht an der Wurzel der JSON-RPC-Nachricht. Und `Mcp-Name` spiegelt
`params.name` bzw. `params.uri` und gehört nur zu `tools/call`,
`resources/read` und `prompts/get` — ein leerer Header ist kein neutraler,
sondern ein `HeaderMismatch`.

## S2 — Was neu nicht mehr gebaut wird

Abgekündigt, aber noch funktionsfähig. **Neue Server übernehmen sie nicht:**

| Feature | Stattdessen |
|---|---|
| Roots | Verzeichnisse oder Dateien als Tool-Parameter, Resource-URIs oder Server-Konfiguration |
| Sampling | direkt gegen die API des LLM-Anbieters |
| Logging | `stderr` (stdio) oder OpenTelemetry |
| HTTP+SSE-Transport (`/sse`) | Streamable HTTP |
| Dynamic Client Registration | Client ID Metadata Documents |

«Frühestmögliche Entfernung» ist eine Berechtigung, **keine Frist**. Für den
`/sse`-Transport gibt die Spezifikation kein Datum an — keines erfinden. Ein
errechnetes Datum in einem Bericht wird verplant, und genau das ist im Auditor
passiert (`2027-07-28` für ein `/sse`-Endpoint, eine Zahl, die in der
Spezifikation nirgends steht).

## S3 — Die Protokollversion gehört dem SDK

Die Version steht in aller Regel nicht im Servercode, sondern kommt aus dem
installierten SDK. Daraus folgen drei Regeln:

1. **Untergrenze des SDK auf die erste Version legen, die `2026-07-28`
   spricht**, und eine Obergrenze auf den nächsten Major (`>=A.B,<A+1`). Welche
   Version das ist, steht im Changelog des SDK — hier bewusst **keine Zahl**,
   aus demselben Grund wie beim ruff-Pin (Schritt 8.1): eine Nummer in der
   Dokumentation veraltet still und wird trotzdem kopiert.
2. **Lockfile nachziehen.** Eine Untergrenze in `pyproject.toml` neben einem
   `uv.lock`, das noch die alte Version fixiert, ändert am installierten Stand
   nichts.
3. **Den Stand am Draht belegen, nicht im Quelltext.** Während der Migration
   ändert sich der Servercode oft gar nicht — nur das SDK. Eine Prüfung, die nur
   die Quellen liest, sieht ein sauberes Repo und einen falschen Draht.

## S4 — Nachweis vor dem Release

```bash
# stdio-Server: server/discover ohne Handshake — die Anfrage exakt wie in
# https://modelcontextprotocol.io/specification/2026-07-28/server/discover
printf '%s\n' '{"jsonrpc":"2.0","id":"discover-1","method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"release-check","version":"1.0.0"},"io.modelcontextprotocol/clientCapabilities":{}}}}' \
  | uvx --from . <server-command> 2>/dev/null | head -1
```

Erwartet: ein `result` mit `"resultType": "complete"` und `supportedVersions`,
das `"2026-07-28"` enthält. Kommt ein JSON-RPC-Fehler (typisch `-32601`,
*method not found*), spricht der Server noch das alte Protokoll. Kommt gar
nichts, ist das **kein Ergebnis** — nicht als «bestanden» buchen.

Für laufende HTTP-Server misst der
[`mcp-continuous-auditor`](https://github.com/malkreide/mcp-continuous-auditor)
dasselbe mit `scripts/spec_probe.py --url …` und unterscheidet dabei einen
Server, der die Header-Pflicht *durchsetzt*, von einem, der sie nur duldet.

## S5 — Festhalten

- `.github/repo-meta.yml`: `mcp_spec_version: 2026-07-28` (Schritt 0). Der
  Validator meldet ein fehlendes Feld als WARN und einen anderen Wert als ERROR
  (Regel A5).
- README: im Abschnitt zur Installation oder Konfiguration einen Satz, welcher
  Protokollstand gilt — Clients auf älterem Stand scheitern sonst ohne
  Hinweis am fehlenden Handshake.
- CHANGELOG: die Migration ist eine **Breaking Change** für Clients, die noch
  `initialize` senden → Major-Version.

**Nicht verwechseln:** Das Datum im `$schema` von `server.json`
(`references/mcp-publishing.md`) ist die Version des *Registry-Schemas*, nicht
die Protokollversion. Die beiden haben nichts miteinander zu tun.
