# Testplan: FusionMCP (Standard-konforme KI-Tests)

## Ziel
Dieser Testplan dient der Verifizierung des FusionMCP Servers durch einen KI-Agenten. Er nutzt ausschließlich die **kanonischen englischen Werkzeugnamen**, um universelle Kompatibilität mit allen MCP-Clients (Gemini, Claude, Cursor etc.) sicherzustellen.

## Testprinzip
- Jeder Test startet von einem bekannten Zustand.
- Vor jedem Block soll `cleanup_design()` aufgerufen werden.
- Ein Test gilt als bestanden, wenn die MCP-Antwort plausibel ist und das Ergebnis in Fusion 360 korrekt erzeugt wurde.

## Transport und Voraussetzungen

### Fusion-Seite
- Fusion 360 aktiv.
- Add-In `FusionMCP` läuft.
- Bridge erreichbar unter `http://localhost:8082`.

### MCP-Seite
- MCP-Server erreichbar unter `http://localhost:8081/mcp/sse`.

## Ausführungsreihenfolge

### 1. Konnektivität
- Aktion: `curl -s http://localhost:8081/mcp`
- Erwartet: `status: "mcp_server_online"`

### 2. Dokumentsteuerung
- **Cleanup:** `cleanup_design()` -> Erwartet: `Design cleaned up.`
- **New Design:** `create_new_design()` -> Erwartet: `Design created.`

### 3. Basis-Skizzen
- **Create Sketch:** `create_sketch(plane_name="XY", name="S1")` -> Erwartet: `Sketch 'S1' created.`
- **Line:** `draw_line(sketch_name="S1", x1=0, y1=0, x2=5, y2=0)` -> Erwartet: `Line drawn.`
- **Circle:** `draw_circle(sketch_name="S1", x=10, y=10, radius=3)` -> Erwartet: `Circle drawn.`
- **Rectangle:** `draw_rectangle(sketch_name="S1", x1=15, y1=0, x2=20, y2=5)` -> Erwartet: `Rectangle drawn.`

### 4. Skizzen-Modifikatoren
- **Circular Pattern:** `sketch_circular_pattern(sketch_name="S1", center_x=0, center_y=0, count: 6)` -> Erwartet: `Sketch pattern created.`
- **Offset (Frische Skizze):** 
  - `create_sketch(name="OffsetTest", plane_name="XY")`
  - `draw_circle(sketch_name="OffsetTest", x=0, y=0, radius=5)`
  - `sketch_offset(sketch_name="OffsetTest", distance=1.0)`
  - Erwartet: `Sketch offset created.`

### 5. 3D-Operationen
- **Extrude:** `extrude_sketch(sketch_name="S1", distance=2.0)` -> Erwartet: Body in Fusion sichtbar.
- **Fillet:** `create_fillet(body_name="Body1", radius=0.5)` -> Erwartet: `Fillet created.`
- **Shell:** `create_shell(body="Body1", thickness=0.2)` -> Erwartet: `Shell created.`
- **Mirror:** `mirror_body(body="Body1", plane_name="YZ")` -> Erwartet: `Mirror created.`

### 6. Mechanische Komponenten
- **Bolt:** `create_bolt(diameter_mm=8, length_cm=5, modeled=True)` -> Erwartet: `Bolt M8... created.`
- **Gear:** `create_gear(num_teeth=20, module=2.0, thickness=1.0)` -> Erwartet: `Gear created.`

### 7. Fortgeschrittene Geometrie (NEU)
- **Loft:** 
  - Erzeuge `S1` bei Z=0 und `S2` (Offset) bei Z=10.
  - Aufruf: `create_loft(sketch_names=["S1", "S2"])`
  - Erwartet: Verbindungskörper zwischen beiden Skizzen.
- **Appearance:** `apply_appearance(body="Body1", appearance="Red")` -> Erwartet: Körper in Fusion wird rot.

### 8. Analyse & Messen (NEU)
- **Mass Center:** `get_center_of_mass(body="Body1")` -> Erwartet: X,Y,Z Koordinaten.
- **Distance:** `measure_distance(body1="Body1", body2="Body2")` -> Erwartet: Distanz in cm.

### 9. Analyse & Export
- **Screenshot:** `capture_view()` -> Erwartet: Base64-Daten.
- **STL Export:** `export_stl(filename="test_model")` -> Erwartet: Pfad zur Datei.
- **STEP Export (NEU):** `export_step(filename="test_model")` -> Erwartet: Erfolgreicher Export.

## Ergebnisformat
Tests sind mit `[PASS]` oder `[FAIL]` zu kennzeichnen.
