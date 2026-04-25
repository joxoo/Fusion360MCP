# Testplan: FusionMCP fuer KI-gestuetzte End-to-End-Tests

## Ziel
Dieser Testplan ist fuer einen KI-Agenten gedacht, der den laufenden FusionMCP ueber MCP-Tools prueft.  
Der Plan ist so aufgebaut, dass jeder Schritt mit einem klaren Toolaufruf, einer erwarteten Textantwort und einem erwarteten sichtbaren Ergebnis in Fusion 360 verifiziert werden kann.

## Testprinzip
- Jeder Test startet von einem bekannten Zustand.
- Vor jedem groesseren Block soll der Agent `design_bereinigen()` oder `cleanup_design()` aufrufen.
- Wenn ein Test eine vorhandene Skizze oder einen vorhandenen Koerper benoetigt, muss diese Voraussetzung vorher explizit erzeugt werden.
- Ein Test gilt nur dann als bestanden, wenn
  - die MCP-Antwort plausibel ist und
  - das erwartete Objekt oder die erwartete Aenderung in Fusion 360 sichtbar ist.

## Transport und Voraussetzungen

### Fusion-Seite
- Fusion 360 muss laufen.
- Das Add-In `FusionMCP` muss aktiv sein.
- Die lokale Bridge muss erreichbar sein:

```bash
curl -s http://localhost:8082
```

Erwartet:
- JSON mit Status wie `online`

### MCP-Seite
- Der MCP-Server muss laufen.
- Der MCP-Status-Endpunkt ist:

```bash
curl -s http://localhost:8081/mcp
```

Erwartet:
- JSON mit
  - `status: "mcp_server_online"`
  - `transport`
  - `sse_endpoint`
  - `messages_endpoint`

Hinweis:
- Fuer echte MCP-Clients ist nicht `/mcp` selbst der Tool-Transport, sondern der dort ausgewiesene SSE- und Messages-Pfad, typischerweise `/mcp/sse` und `/mcp/messages`.

## Ausfuehrungsreihenfolge
Der Agent soll die Tests in genau dieser Reihenfolge ausfuehren:
1. Konnektivitaet
2. Dokumentzustand
3. Basis-Geometrie
4. Basis-Skizzen
5. Erweiterte Skizzen
6. Skizzen-Modifikatoren
7. 3D-Operationen
8. Analyse und Export
9. Sprach- und I18n-Checks
10. Gewinde- und Bolzen-Checks

## 1. Konnektivitaet

### 1.1 Bridge erreichbar
- Aktion: `curl -s http://localhost:8082`
- Erwartet:
  - gueltiges JSON
  - Bridge meldet sich als online

### 1.2 MCP erreichbar
- Aktion: `curl -s http://localhost:8081/mcp`
- Erwartet:
  - gueltiges JSON
  - MCP meldet Transportinformationen

## 2. Dokumentzustand

### 2.1 Neuer Entwurf
- Tool: `neue_konstruktion()` oder `create_new_design()`
- Erwartete Antwort:
  - DE: `Dokument erstellt.`
  - EN: `Design created.`

### 2.2 Bereinigung
- Tool: `design_bereinigen()` oder `cleanup_design()`
- Erwartete Antwort:
  - DE: `Entwurf bereinigt.`
  - EN: `Design cleaned up.`
- Erwartetes Fusion-Ergebnis:
  - keine Bodies
  - keine Occurrences

## 3. Basis-Geometrie

### 3.1 Box erzeugen
- Tool DE:

```text
box_erstellen(l=10, w=10, h=5, name="Box", x=0, y=0, z=0)
```

- Tool EN:

```text
create_box(l=10, w=10, h=5, name="Box", x=0, y=0, z=0)
```

- Erwartete Antwort:
  - DE: `Box 'Box' erstellt.`
  - EN: `Box 'Box' created.`
- Erwartetes Fusion-Ergebnis:
  - ein Body namens `Box`

### 3.2 Koerper spiegeln
- Tool DE:

```text
spiegeln(body="Box", plane_name="YZ")
```

- Tool EN:

```text
mirror_body(body="Box", plane_name="YZ")
```

- Erwartete Antwort:
  - DE: `Spiegelung erstellt.`
  - EN: `Mirror created.`

Hinweis:
- Dieser Test prueft nur, dass der Toolpfad sauber durchlaeuft. Er setzt keinen stabilen Namen fuer den gespiegelten Koerper voraus.

## 4. Basis-Skizzen

### 4.1 Skizze anlegen
- Tool DE:

```text
skizze_erstellen(name="S1", ebene="XY")
```

- Tool EN:

```text
create_sketch(name="S1", plane="XY")
```

- Erwartete Antwort:
  - DE: `Skizze 'S1' erstellt.`
  - EN: `Sketch 'S1' created.`

### 4.2 Linie zeichnen

```text
linie_zeichnen(skizzen_name="S1", x1=0, y1=0, x2=5, y2=0)
```

Erwartet:
- `Linie gezeichnet.`

### 4.3 Kreis zeichnen

```text
kreis_zeichnen(skizzen_name="S1", center_x=10, center_y=10, radius=3)
```

Erwartet:
- `Kreis gezeichnet.`

### 4.4 Rechteck zeichnen

```text
rechteck_zeichnen(skizzen_name="S1", x1=15, y1=0, x2=20, y2=5)
```

Erwartet:
- `Rechteck gezeichnet.`

## 5. Erweiterte Skizzen

### 5.1 Polygon

```text
polygon_zeichnen(skizzen_name="S1", center_x=25, center_y=10, radius=3, seiten=6)
```

Erwartet:
- `Polygon (6 Seiten) gezeichnet.`
- in Fusion sichtbar: geschlossenes Sechseck

### 5.2 Bogen

```text
bogen_zeichnen(skizzen_name="S1", mittelpunkt_x=0, mittelpunkt_y=10, start_x=5, start_y=10, winkel=90)
```

Erwartet:
- `Bogen gezeichnet.`

### 5.3 Spline

```text
spline_zeichnen(skizzen_name="S1", punkte_liste=[[0,0], [2,5], [5,2]])
```

Erwartet:
- `Spline gezeichnet.`

### 5.4 Langloch

```text
langloch_zeichnen(skizzen_name="S1", x1=30, y1=0, x2=40, y2=0, breite=2)
```

Erwartet:
- `Langloch gezeichnet.`

## 6. Skizzen-Modifikatoren

Wichtig:
- Diese Tests muessen auf einer bereits gefuellten Skizze wie `S1` ausgefuehrt werden.

### 6.1 Kreismuster in Skizze

```text
skizze_kreismuster(skizzen_name="S1", center_x=0, center_y=0, anzahl=6)
```

Erwartet:
- `Muster in Skizze erstellt.`

### 6.2 Rechteckmuster in Skizze

```text
skizze_rechteckmuster(skizzen_name="S1", anzahl_x=3, distanz_x=5, anzahl_y=2, distanz_y=5)
```

Erwartet:
- `Muster in Skizze erstellt.`

### 6.3 Skizzen-Versatz

```text
skizze_versatz(skizzen_name="S1", abstand=1.0)
```

Erwartet:
- `Versatz in Skizze erstellt.`

## 7. 3D-Operationen

### 7.1 Skizze extrudieren
- Voraussetzung:
  - Die Skizze `S1` enthaelt mindestens ein geschlossenes Profil.

```text
extrudieren(sketch_name="S1", distance=2)
```

oder auf Englisch:

```text
extrude_sketch(sketch_name="S1", distance=2)
```

Erwartet:
- Extrusionsantwort fuer `S1`
- neuer Body in Fusion

### 7.2 Abrunden

```text
abrunden_erstellen(body_name="Box", radius=0.5)
```

Erwartet:
- `Abrundung erstellt.`

### 7.3 Fase

```text
fase_erstellen(body="Box", distance=0.25)
```

Erwartet:
- `Fase erstellt.`

### 7.4 Schale

```text
schale_erstellen(body="Box", thickness=0.2)
```

Erwartet:
- `Schale erstellt.`

### 7.5 Koerper-Kreismuster

```text
kreismuster_erstellen(body_name="Box", count=4, axis="Z")
```

Erwartet:
- `Muster erstellt.`

### 7.6 Koerper-Rechteckmuster

```text
rechteckmuster_erstellen(body_name="Box", count_x=2, dist_x=10, count_y=2, dist_y=10)
```

Erwartet:
- `Muster erstellt.`

## 8. Analyse und Export

### 8.1 Koerper analysieren

```text
koerper_analysieren()
```

oder

```text
analyze_bodies()
```

Erwartet:
- JSON oder strukturierte Daten mit Koerperinformationen

### 8.2 Viewport-Aufnahme

```text
ansicht_fotografieren()
```

oder

```text
capture_view()
```

Erwartet:
- Base64-String oder plausibler Bildinhalt als Rueckgabe
- wenn stattdessen ein Fehlertext kommt, muss der Agent den exakten Rueckgabewert protokollieren

### 8.3 STL-Export

```text
stl_exportieren()
```

oder

```text
export_stl()
```

Erwartet:
- erfolgreiche Rueckmeldung
- Export darf nur dann als bestanden gelten, wenn der Zielpfad oder die erzeugte Datei nachvollziehbar ist

## 9. Sprach- und I18n-Checks

### 9.1 Deutscher und englischer Toolname fuer denselben Pfad
Der Agent soll fuer mindestens diese Paare pruefen, dass beide funktionieren:
- `skizze_erstellen` / `create_sketch`
- `polygon_zeichnen` / `draw_polygon`
- `kreis_zeichnen` / `draw_circle`
- `skizze_versatz` / `sketch_offset`

### 9.2 Sprachspezifische Parameternamen
Der Agent soll gezielt verifizieren:
- Deutsch:

```text
skizze_erstellen(name="AliasDE", ebene="XY")
polygon_zeichnen(skizzen_name="AliasDE", center_x=5, center_y=5, radius=2, seiten=5)
bogen_zeichnen(skizzen_name="AliasDE", mittelpunkt_x=0, mittelpunkt_y=0, start_x=3, start_y=0, winkel=45)
skizze_versatz(skizzen_name="AliasDE", abstand=0.5)
```

- Englisch:

```text
create_sketch(name="AliasEN", plane="XY")
draw_polygon(sketch_name="AliasEN", center_x=5, center_y=5, radius=2, sides=5)
draw_arc(sketch_name="AliasEN", center_x=0, center_y=0, start_x=3, start_y=0, angle=45)
sketch_offset(sketch_name="AliasEN", distance=0.5)
```

Erwartet:
- keine Parameterfehler
- jeweils plausible sprachspezifische Erfolgsmeldungen

## 10. Gewinde- und Bolzen-Checks

Wichtig:
- Dieser Block ist ein Risikoblock.
- Er soll separat ausgefuehrt und separat bewertet werden.
- Ein Fehlschlag hier soll nicht die Aussage ueber die restliche MCP-Funktionalitaet verfaelschen.

### 10.1 Bolzen erzeugen

```text
bolzen_erstellen(diameter_mm=3, length_cm=1)
```

oder

```text
create_bolt(diameter_mm=3, length_cm=1)
```

Erwartet:
- kein `ERR_API`
- Rueckmeldung in Richtung `Bolzen M3... erstellt.`

### 10.2 Gewinde auf Zylinder anwenden

Vorbereitung:
- Einen Zylinderkoerper in Fusion erzeugen oder einen passenden Body vorbereiten.

Test:

```text
gewinde_anwenden(body_name="Zylinder", thread_type="ISO Metric profile", size="8", designation="M8x1.25")
```

oder

```text
apply_custom_thread(body_name="Zylinder", thread_type="ISO Metric profile", size="8", designation="M8x1.25")
```

Erwartet:
- erfolgreiche Thread-Antwort
- sichtbares Gewinde auf dem Zylinder

Wenn fehlgeschlagen:
- exakte MCP-Antwort protokollieren
- exakten Toolaufruf protokollieren
- den Testblock als `known failing path` markieren, falls die restlichen Tests gruen sind

## Ergebnisformat fuer KI-Agenten

Der Agent soll am Ende jeden Testblocks in diesem Format berichten:

```text
[PASS|FAIL] <Blockname>
- Toolaufruf:
- MCP-Antwort:
- Sichtpruefung in Fusion:
- Bemerkungen:
```

## Minimaler Smoke-Test
Wenn nur ein sehr kurzer KI-Testlauf moeglich ist, sollen mindestens diese Schritte ausgefuehrt werden:
1. `neue_konstruktion()`
2. `design_bereinigen()`
3. `box_erstellen(l=10, w=10, h=5, name="Box")`
4. `skizze_erstellen(name="S1", ebene="XY")`
5. `polygon_zeichnen(skizzen_name="S1", center_x=10, center_y=10, radius=3, seiten=6)`
6. `koerper_analysieren()`
7. `cleanup_design()`

Wenn diese Schritte gruen sind, funktionieren Bridge, MCP, I18n-Basics, Sketch-Aliase und Basis-Geometrie.
