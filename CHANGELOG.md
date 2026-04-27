# Changelog - FusionMCP

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

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
