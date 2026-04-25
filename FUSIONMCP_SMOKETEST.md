# FusionMCP Smoke-Test fuer KI-Agenten

## Ziel
Dieser Smoke-Test prueft in wenigen Minuten, ob die wichtigsten Pfade von FusionMCP funktionieren:
- Bridge erreichbar
- MCP erreichbar
- neuer Entwurf
- Bereinigung
- Basis-Geometrie
- lokalisierte Skizzen-Tools
- einfache Analyse-Rueckgabe

Der Smoke-Test ist bewusst klein. Er soll schnell zeigen, ob das System grundsaetzlich lauffaehig ist.

## Voraussetzungen
- Fusion 360 laeuft.
- Das Add-In `FusionMCP` ist aktiv.
- Der MCP-Server laeuft.

## Erfolgskriterium
Der Smoke-Test ist bestanden, wenn:
- alle Schritte ohne Parameterfehler durchlaufen
- mindestens ein Body in Fusion erzeugt wurde
- mindestens eine Skizze mit Polygon erfolgreich erstellt wurde
- die Analyse-Rueckgabe plausibles JSON oder strukturierte Koerperdaten liefert

## Schritt 1: Bridge pruefen

```bash
curl -s http://localhost:8082
```

Erwartet:
- JSON mit Online-Status

## Schritt 2: MCP pruefen

```bash
curl -s http://localhost:8081/mcp
```

Erwartet:
- JSON mit `status: "mcp_server_online"`

## Schritt 3: Neuer Entwurf

```text
neue_konstruktion()
```

Erwartet:
- `Dokument erstellt.`

## Schritt 4: Bereinigen

```text
design_bereinigen()
```

Erwartet:
- `Entwurf bereinigt.`

## Schritt 5: Box erzeugen

```text
box_erstellen(l=10, w=10, h=5, name="SmokeBox", x=0, y=0, z=0)
```

Erwartet:
- `Box 'SmokeBox' erstellt.`
- in Fusion sichtbar: Body `SmokeBox`

## Schritt 6: Skizze erzeugen

```text
skizze_erstellen(name="SmokeSketch", ebene="XY")
```

Erwartet:
- `Skizze 'SmokeSketch' erstellt.`

## Schritt 7: Polygon zeichnen

```text
polygon_zeichnen(skizzen_name="SmokeSketch", center_x=10, center_y=10, radius=3, seiten=6)
```

Erwartet:
- `Polygon (6 Seiten) gezeichnet.`
- in Fusion sichtbar: geschlossenes Sechseck in `SmokeSketch`

## Schritt 8: Kreis zeichnen

```text
kreis_zeichnen(skizzen_name="SmokeSketch", center_x=20, center_y=10, radius=2)
```

Erwartet:
- `Kreis gezeichnet.`

## Schritt 9: Koerper analysieren

```text
koerper_analysieren()
```

Erwartet:
- JSON oder strukturierte Daten mit mindestens einem Body
- `SmokeBox` sollte enthalten sein

## Schritt 10: Optionaler EN-Alias-Check

```text
create_sketch(name="SmokeSketchEN", plane="XY")
draw_polygon(sketch_name="SmokeSketchEN", center_x=5, center_y=5, radius=2, sides=5)
```

Erwartet:
- `Sketch 'SmokeSketchEN' created.`
- `Polygon (5 sides) drawn.`

## Schritt 11: Aufraeumen

```text
cleanup_design()
```

Erwartet:
- `Design cleaned up.`

## Ergebnisformat
Der Agent soll so berichten:

```text
[PASS|FAIL] FusionMCP Smoke-Test
- Bridge:
- MCP:
- Erzeugte Bodies:
- Erzeugte Skizzen:
- Analyseantwort:
- Auffaelligkeiten:
```

## Abbruchregeln
- Wenn schon Schritt 1 oder 2 fehlschlaegt, Test sofort abbrechen.
- Wenn `box_erstellen` fehlschlaegt, keine spaeteren Geometrieaussagen treffen.
- Wenn `skizze_erstellen` funktioniert, aber `polygon_zeichnen` fehlschlaegt, Fehler als Skizzen-/Alias-Pfad markieren.
