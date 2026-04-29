# Changelog - FusionMCP

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [9.2.0] - 2026-04-29
### Hinzugefügt
- **Einheitlicher Export:** Neues MCP-Tool `export_model` fuer `stl`, `f3d` und `step`.
- **Reaktivierte MCP-Module:** `advanced_geometry`, `export`, `mechanical` und `threads` werden wieder im MCP-Server registriert.
- **Regressionstests:** Zusätzliche Abdeckung fuer Export-Konsolidierung, Batch-Alias-Felder und robustere Bolt-/Restart-Pfade.

### Geaendert
- **Export-API:** Die bisherigen Einzel-Export-Tools wurden auf ein gemeinsames `export_model`-Interface konsolidiert.
- **Batch-Geometrie:** `apply_3d_features` akzeptiert nun `height` fuer `Box` und `Cylinder` sowie `center` fuer `Cylinder`.
- **MCP-Neustart:** `manage_design(action="restart_mcp")` beendet den bekannten MCP-Kindprozess jetzt wirklich und startet ihn frisch neu.
- **Plugin-Stopp:** Beim Stoppen des Fusion-Add-ins wird der MCP-Prozess nun immer mit beendet, statt auf ein fehleranfälliges Reuse-Verhalten zu setzen.
- **Bolt-Erzeugung:** `create_bolt` extrudiert explizit als `NewBody` und waehlt die groesste zylindrische Flaeche fuer das Gewinde.
- **Testdokumentation:** Testplan und Smoke-Test wurden auf `export_model`, den echten Restart-Pfad und die aktuellen Batch-Parameter aktualisiert.

### Behoben
- **Batch-Boxen:** `apply_3d_features` wirft bei `Box`-Payloads mit `height` statt `h` keinen `ERR:'h'`-Fehler mehr.
- **Batch-Zylinder:** `apply_3d_features` verarbeitet `height`/`center`-Aliasfelder fuer `Cylinder` konsistent.
- **MCP-Code-Reload:** Aenderungen am MCP-Server werden nach `restart_mcp` wieder zuverlaessig geladen.
- **Bolt-Threading:** Das automatische Finden der Gewindeflaeche bei `create_bolt` ist robuster.

## [9.1.0] - 2026-04-27
### Hinzugefügt
- **Text-Extrusion:** `extrude_sketch` unterstützt nun die Extrusion von `SketchText`-Objekten. Text wird automatisch in die Profilsammlung aufgenommen.
- **Skizzen auf Flächen:** `create_sketch` ermöglicht das Erstellen von Skizzen direkt auf Körperflächen (`body_name`, `face_index`).
- **Erweiterte Extrusions-Operationen:** Unterstützung für `Join`, `Cut`, `Intersect`, `NewBody` und `NewComponent` in `extrude_sketch`.
- **Extrusions-Offset:** Neuer Parameter `offset` für `extrude_sketch`, um Extrusionen mit einem Versatz zur Skizzen-Ebene zu starten.
- **Zielkörper-Selektion:** `extrude_sketch` erlaubt die gezielte Auswahl von `participantBodies` für boolesche Operationen.
- **Auto-Targeting:** Bei `Cut` und `Join` ohne expliziten Zielkörper werden automatisch alle Körper der aktiven Komponente als Ziele einbezogen (behebt "Kein Zielkörper gefunden").

### Geaendert
- **Profil-Sammlung:** `extrude_sketch` sammelt nun standardmäßig alle Profile einer Skizze (statt nur das erste).

## [9.0.3] - 2026-04-25
### Hinzugefügt
- **KI-Testartefakte:** Ausfuehrlicher KI-Testplan, kompakter Smoke-Test und maschinenlesbare YAML-Smoketest-Datei hinzugefuegt.
- **Alias-Testabdeckung:** Unit-Tests fuer lokalisierte MCP-Toolsignaturen und Parametermappings erweitert.
- **MCP-Kompatibilitäts-Wrapper:** Bekannte Tool-/Parameter-Aliase und harmlose Client-Metadaten wie `wait_for_previous` werden bei der Tool-Registrierung wieder toleriert.

### Geaendert
- **Dynamische Tool-Registrierung:** Sprach- und Parameter-Aliase werden zentral aus `i18n.json` geladen.
- **Skizzen-Tools:** Registrierung vereinfacht und auf die zentrale Alias-Logik zurueckgefuehrt.

## [9.0.2] - 2026-04-25
### Hinzugefügt
- **Erweiterte UI-Einstellungen:** Dialog um Konfiguration für den Bridge-Server (Fusion Interface) erweitert.
- **Auto-Restart:** Der Bridge-Server startet nun automatisch neu, wenn Host oder Port im Dialog geändert werden.
- **Gruppierte Ansicht:** Einstellungen im Dialog sind nun in logische Gruppen unterteilt (Bridge, MCP, Historie).

## [9.0.1] - 2026-04-25
### Hinzugefügt
- **Befehlshistorie:** Ein Log-Fenster im Fusion 360 Dialog zeigt nun die letzten 20 ausgeführten Befehle mit Zeitstempel an.
- **Status-Feedback:** Live-Anzeige des Server-Status (RUNNING/STOPPED) im UI.
- **Refresh-Funktion:** Manuelle Aktualisierung der Dialogansicht ermöglicht.

### Behoben
- **API-Fix:** `addSectionCommandInput` durch die korrekte Methode `addGroupCommandInput` ersetzt.

## [9.0.0] - 2026-04-25
### Hinzugefügt
- **Fusion 360 UI Tool:** Integration eines Buttons in den Reiter "Werkzeuge" (Tools) / Panel "Zusatzmodule".
- **MCP Server Steuerung:** Möglichkeit zum Starten/Stoppen des MCP-Servers direkt aus Fusion 360.
- **Konfiguration:** Felder für MCP Host und Port (Slider) implementiert.
- **Add-in Integration:** Automatisches Kopieren und Setup im Fusion 360 API Verzeichnis.

## [8.9.0] - Initialer Build
### Hinzugefügt
- Basis-Infrastruktur für die HTTP-Bridge zwischen Gemini CLI und Fusion 360.
- `FastMCP` Server mit Modul-Registrierung (Design, Geometry, Mechanical, etc.).
- `uv` Integration für isolierte Python-Ausführung innerhalb von Fusion 360.
