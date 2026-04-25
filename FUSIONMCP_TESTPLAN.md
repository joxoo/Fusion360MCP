# Testplan: FusionMCP Integration & Funktionalität

## 1. System-Check (Konnektivität)
- **Ziel**: Sicherstellen, dass die Bridge in Fusion 360 erreichbar ist.
- **Test**: `curl -s http://localhost:8082`
- **Erwartetes Ergebnis**: `{"status": "online", "version": "v9", ...}`

## 2. Basistest: Geometrie-Erstellung
- **Ziel**: Verifizierung der wiederhergestellten `create_box_logic`.
- **Test**: Erstellen einer Box (10x10x5 cm) an Position (0,0,0).
- **Tool**: `box_erstellen` (DE) oder `create_box` (EN)
- **Erwartetes Ergebnis**: Ein neuer Körper "Box" erscheint in Fusion 360.

## 3. Kritischer Pfad: Gewinde-Bolzen (Mechanical)
- **Ziel**: Verifizierung der Fixes für die Thread-Signatur und Tuple-Zugriffe.
- **Test**: Erstellen eines M3 Bolzens (Test für robuste Größenauflösung "3" -> "3.0").
- **Tool**: `bolzen_erstellen(diameter_mm=3, length_cm=1)`
- **Erwartetes Ergebnis**: Ein M3 Bolzen wird ohne `ERR_API` erstellt.

## 4. Spezifische Gewinde-Anwendung (Threads)
- **Ziel**: Verifizierung der robusten Größen-Formatierung (z.B. "8" -> "8.0").
- **Test**: Anwendung eines M8-Gewindes auf einen Zylinder.
- **Tool**: `gewinde_anwenden(koerper_name="Zylinder", gewinde_typ="ISO Metric profile", groesse="8", bezeichnung="M8x1.25")`
- **Erwartetes Ergebnis**: Rückmeldung "Gewinde M8x1.25 angewendet".

## 5. Erweiterte Skizzen-Funktionen
- **Ziel**: Verifizierung aller neuen Skizzen-Zeichenwerkzeuge.
- **Tests**:
  - **Bogen**: `bogen_zeichnen(skizzen_name="S1", mittelpunkt_x=0, mittelpunkt_y=0, start_x=5, start_y=0, winkel=90)`
  - **Polygon**: `polygon_zeichnen(skizzen_name="S1", center_x=10, center_y=10, radius=3, seiten=6)`
  - **Spline**: `spline_zeichnen(skizzen_name="S1", punkte_liste=[[0,0], [2,5], [5,2]])`
  - **Langloch (Slot)**: `langloch_zeichnen(skizzen_name="S1", x1=0, y1=0, x2=10, y2=0, breite=2)`
- **Erwartetes Ergebnis**: Die entsprechenden Kurven erscheinen in der Skizze "S1".

## 6. Skizzen-Modifikatoren (Patterns & Offset)
- **Ziel**: Verifizierung von Anordnungen und Versatz innerhalb von Skizzen.
- **Tests**:
  - **Kreismuster**: `skizze_kreismuster(skizzen_name="S1", center_x=0, center_y=0, anzahl=6)`
  - **Rechteckmuster**: `skizze_rechteckmuster(skizzen_name="S1", anzahl_x=3, distanz_x=5, anzahl_y=2, distanz_y=5)`
  - **Versatz (Offset)**: `skizze_versatz(skizzen_name="S1", abstand=1.0)`
- **Erwartetes Ergebnis**: Bestehende Kurven werden vervielfältigt oder versetzt.

## 7. Körper-Operationen (Fillet, Shell, Patterns)
- **Ziel**: Verifizierung mechanischer Bearbeitungen an 3D-Körpern.
- **Tests**:
  - **Abrunden**: `abrunden_erstellen(koerper_name="Box", radius_cm=0.5)`
  - **Schale**: `schale_erstellen(koerper_name="Box", wandstaerke_cm=0.2)`
  - **Körper-Kreismuster**: `kreismuster_erstellen(koerper_name="Box", anzahl=4, achse="Z")`
  - **Körper-Rechteckmuster**: `rechteckmuster_erstellen(koerper_name="Box", anzahl_x=2, distanz_x=10)`
- **Erwartetes Ergebnis**: Der Körper wird modifiziert oder als Muster angeordnet.

## 8. Dokumenten-Management & I18n
- **Ziel**: Sicherstellen der Bereinigung und Mehrsprachigkeit.
- **Tests**:
  - **Bereinigen**: `design_bereinigen()`
  - **I18n**: Wechsel zwischen DE und EN Tool-Aufrufen.
- **Erwartetes Ergebnis**: Leerer Entwurf; korrekte Sprachausgabe in den Antworten.
