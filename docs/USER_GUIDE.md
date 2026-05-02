# Fusion 360 MCP Server - Benutzerhandbuch

## 1. Überblick
Der Fusion 360 MCP-Server ermöglicht die vollständige Fernsteuerung von Autodesk Fusion 360 durch KI-Agenten oder externe Skripte. Er deckt den gesamten Workflow der modernen Produktentwicklung ab – von der ersten Skizze bis zur finalen Fertigungsprüfung.

---

## 2. Verfügbare Module & Werkzeuge

### 2.0 Öffentliche API-Profile

Standardmäßig läuft FusionMCP mit dem Profil `compact`. Dieses Profil ist absichtlich klein gehalten, damit KI-Clients nicht zwischen zu vielen Spezialwerkzeugen wählen müssen.

**`compact` (Standard)**
- `manage_design`
- `describe_tool_actions`
- `analyze_design`
- `list_parameters`
- `edit_parameters`
- `create_sketch`
- `edit_sketch`
- `apply_3d_features`
- `edit_assembly`
- `edit_surfaces`
- `edit_forms`
- `import_mesh`
- `edit_mesh`
- `export_model`

**`full`**
- Enthält zusätzlich interne und spezialisierte Werkzeuge wie `direct_api_access`, `list_mcp_tools`, Mess-/Appearance-Tools, Gewinde- und Mechanical-Helfer.

Startbeispiele:

```bash
python fusion_mcp_server.py --api-profile compact
python fusion_mcp_server.py --api-profile full
```

### 2.1 Solid Modeling (Festkörper)
Basiskonstruktion mit mathematisch präzisen Volumenkörpern.
*   **Öffentlich im Profil `compact`:** `create_sketch`, `edit_sketch`, `apply_3d_features`.
*   **Wichtige Regel:** Spezialoperationen wie Extrude, Fillet, Chamfer oder Combine werden bevorzugt als Actions innerhalb von `apply_3d_features` angesprochen.

### 2.2 Surface Design (Flächen)
Erstellung hochkomplexer Freiform-Flächen für aerodynamische Hüllen.
*   **Öffentlich im Profil `compact`:** `edit_surfaces`
*   **Hinweis:** Einzelfunktionen werden nach außen bewusst gebündelt.

### 2.3 Form Design (Organische T-Splines)
Der "Sculpting"-Modus für ergonomische und fließende Designs.
*   **Öffentlich im Profil `compact`:** `edit_forms`
*   **Hinweis:** Form-Operationen werden gesammelt als Actions innerhalb dieses Werkzeugs ausgeführt.

### 2.4 Mesh Modeling (Netzkörper)
Umgang mit STL, OBJ und 3D-Scan-Daten.
*   **Öffentlich im Profil `compact`:** `import_mesh`, `edit_mesh`, `export_model`
*   **Hinweis:** `export_model` ist das einheitliche Export-Werkzeug für `stl`, `f3d` und `step`.

### 2.5 Professional Modification (Direct Modeling)
Bearbeitung von Geometrie direkt auf Flächenebene, ideal für historienlose Modelle.
*   **Öffentlich im Profil `compact`:** über `apply_3d_features`
*   **Typische Actions:** Combine, Fillet, Chamfer, Shell, direkte Modellieroperationen.

### 2.6 Assembly & Baugruppen
Strukturierung von komplexen Projekten aus mehreren Teilen.
*   **Öffentlich im Profil `compact`:** `edit_assembly`
*   **Typische Actions:** `create_component`, `create_joint`

### 2.7 Analyse & Engineering
Technische Validierung des Modells.
*   **Öffentlich im Profil `compact`:** `analyze_design`
*   **Typische Actions:** `get_assembly_tree`, `validate`, `scene_map`, `physical_data`, `bounding_box`

---

## 3. Besonderheiten des Servers

### 3.1 Mehrzeilige Skripte & Standardausgabe
Der Server unterstützt komplexe, mehrzeilige Python-Skripte via `direct_api_access`. Sämtliche `print()`-Ausgaben innerhalb dieser Skripte werden automatisch abgefangen und als Teil der MCP-Antwort an den Nutzer zurückgegeben.

### 3.2 Kanonische Schnittstelle
Alle Werkzeuge und Parameter sind nach internationalem Standard auf **Englisch** benannt (z.B. `create_sketch` statt `skizze_erstellen`). Dies ist die bevorzugte und vollständig dokumentierte Schnittstelle für moderne KI-Clients.

Für KI-Clients ist die **kompakte Außen-API** die kanonische Schnittstelle. Das Profil `full` ist für Debugging, Migration und Spezialfälle gedacht.

### 3.2.1 Kompatibilitäts-Aliase
Für ältere Prompts und einfache Smoke-Tests akzeptiert der Server zusätzlich einige bekannte Tool- und Parameter-Aliase, z.B.:
- `skizze_erstellen(..., ebene="XY")` -> `create_sketch(..., plane_name="XY")`
- `polygon_zeichnen(..., skizzen_name=..., center_x=..., center_y=..., seiten=...)` -> `sketch_polygon(..., sketch_name=..., cx=..., cy=..., sides=...)`
- `kreis_zeichnen(..., skizzen_name=..., center_x=..., center_y=...)` -> `draw_circle(..., sketch_name=..., x=..., y=...)`

Zusätzliche Client-Metadaten wie `wait_for_previous` werden toleriert und serverseitig ignoriert, solange sie keine fachlichen Parameter sind.

### 3.3 Lokalisierte Rückmeldungen
Obwohl die Befehle Englisch sind, antwortet der Server basierend auf der Nutzersprache (aktuell Deutsch und Englisch) mit lokalisierten Erfolgsmeldungen und Fehlermeldungen.

---

## 4. Einrichtung & Neustart

### 4.1 Installation
Das Plugin muss im Fusion 360 Add-In Verzeichnis liegen:
`~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FusionMCP`

Für Windows liegt das Zielverzeichnis standardmäßig unter:
`%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FusionMCP`

Für Endnutzer ohne Script-Ausführung gibt es jetzt zusätzlich einen normalen Windows-Installer auf Basis von Inno Setup:

`installer/windows/FusionMCP.iss`

Daraus kann eine klassische `Setup.exe` gebaut und verteilt werden.

Zusätzlich gibt es weiterhin eine Script-basierte Installationsroutine im Repo:

```powershell
.\scripts\install_windows.cmd
```

oder direkt:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1
```

Die Routine kopiert das Add-In nach `%APPDATA%` und lässt Entwicklungsartefakte wie `.git`, `.venv`, `tests` und `__pycache__` aus.

### 4.2 Neustart
Nach Code-Änderungen oder bei Session-Problemen muss das Add-In in Fusion 360:
1.  Über das Menü "Utilities" -> "Add-Ins" gestoppt werden.
2.  An gleicher Stelle wieder gestartet werden.

---

## 5. Troubleshooting
*   **-32602 (Invalid Parameters):** Verwende bevorzugt die englischen Parameternamen aus dem Schema. Wenn ein älterer Prompt Aliase nutzt, prüfe, ob der Alias vom Server unterstützt wird.
*   **404 (Not Found):** Die Session-ID ist abgelaufen. Starte die Gemini-Session neu.
*   **Timeout:** Fusion 360 blockiert den UI-Thread (z.B. durch ein offenes Dialogfenster). Schließe alle Dialoge in Fusion.
