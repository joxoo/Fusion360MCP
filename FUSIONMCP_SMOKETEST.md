# FusionMCP Smoke-Test fuer KI-Agenten (Batch-Architektur)

## Ziel
Dieser Smoke-Test prueft in wenigen Minuten, ob die wichtigsten Pfade der konsolidierten FusionMCP Batch-Architektur funktionieren:
- Bridge erreichbar
- MCP erreichbar
- Design Management (Cleanup)
- Geometrie-Batching (apply_3d_features)
- Skizzen-Batching (edit_sketch)
- Parameter-Batching (edit_parameters)
- Analyse-Rueckgabe

## Voraussetzungen
- Fusion 360 laeuft.
- Das Add-In `FusionMCP` ist aktiv.
- Der MCP-Server laeuft.

## Erfolgskriterium
Der Smoke-Test ist bestanden, wenn:
- alle Batch-Schritte ohne Parameterfehler durchlaufen
- die Box via `apply_3d_features` erzeugt wurde
- die Skizze mit mehreren Primitiven via `edit_sketch` aktualisiert wurde
- die Analyse-Rueckgabe plausible Daten liefert

## Schritt 1: Bridge pruefen
`curl -s http://localhost:8082`
Erwartet: JSON mit Online-Status

## Schritt 2: MCP pruefen
`curl -s http://localhost:8081/mcp`
Erwartet: JSON mit `status: "mcp_server_online"`

## Schritt 3: Bereinigen & Management
`manage_design(action="cleanup")`
Erwartet: `Design cleaned up.`

## Schritt 4: Geometrie erzeugen (Batch)
`apply_3d_features(operations=[{"action": "create_box", "l": 10, "w": 10, "h": 5, "name": "SmokeBox"}])`
Erwartet: `geometry_updated`

## Schritt 5: Skizze erzeugen & bearbeiten (Batch)
1. `create_sketch(name="SmokeSketch", plane_name="XY")`
2. `edit_sketch(sketch_name="SmokeSketch", operations=[{"action": "draw_polygon", "cx": 10, "cy": 10, "radius": 3, "sides": 6}, {"action": "draw_circle", "x": 20, "y": 10, "radius": 2}])`
Erwartet: `sketch_created` und `sketch_updated`

## Schritt 6: Parameter setzen (Batch)
`edit_parameters(operations=[{"action": "set", "name": "smoke_param", "expression": "10mm"}])`
Erwartet: `parameters_updated`

## Schritt 7: Analyse
`analyze_design(action="validate")`
Erwartet: Plausible Design-Daten (JSON)

## Schritt 8: Aufraeumen
`manage_design(action="cleanup")`
Erwartet: `Design cleaned up.`

## Ergebnisformat
Der Agent soll so berichten:
```text
[PASS|FAIL] FusionMCP Smoke-Test (Batch)
- Bridge:
- MCP:
- Erzeugte Bodies (Batch):
- Skizzen-Operationen (Batch):
- Parameter-Status:
- Analyseantwort:
```
