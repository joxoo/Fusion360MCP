# Fusion 360 MCP Server - Benutzerhandbuch

## 1. Überblick
Der Fusion 360 MCP-Server ermöglicht die vollständige Fernsteuerung von Autodesk Fusion 360 durch KI-Agenten oder externe Skripte. Er deckt den gesamten Workflow der modernen Produktentwicklung ab – von der ersten Skizze bis zur finalen Fertigungsprüfung.

---

## 2. Verfügbare Module & Werkzeuge

### 2.1 Solid Modeling (Festkörper)
Basiskonstruktion mit mathematisch präzisen Volumenkörpern.
*   **Primitives:** `create_box`, `create_cylinder`, `create_sphere`, `create_torus`, `create_coil`.
*   **Skizzen-basiert:** `extrude_sketch`, `create_revolve`, `create_sweep`, `create_loft`.
*   **Features:** `create_hole_advanced` (mit Senkungen), `apply_custom_thread`.

### 2.2 Surface Design (Flächen)
Erstellung hochkomplexer Freiform-Flächen für aerodynamische Hüllen.
*   **Erstellung:** `create_surface_patch`, `create_surface_cylinder`, `create_surface_sphere`.
*   **Modifikation:** `trim_surface`, `extend_surface`, `reverse_surface_normal`.
*   **Konvertierung:** `stitch_surfaces` (Flächen zu Solid nähen), `thicken_surface`.

### 2.3 Form Design (Organische T-Splines)
Der "Sculpting"-Modus für ergonomische und fließende Designs.
*   **Primitives:** `create_form_box`, `create_form_sphere`, `create_form_cylinder`.
*   **Operationen:** `create_form_extrude`, `create_form_revolve`, `create_form_loft`.
*   **Bearbeitung:** `insert_form_edge`, `subdivide_form_face`, `create_form_crease`.
*   **Symmetrie:** `create_form_mirror_internal`, `clear_form_symmetry`.
*   **Utilities:** `set_form_display_mode` (Box/Smooth), `convert_form` (T-Spline zu B-Rep).

### 2.4 Mesh Modeling (Netzkörper)
Umgang mit STL, OBJ und 3D-Scan-Daten.
*   **Import/Export:** `import_mesh`, `export_stl`, `export_step`.
*   **Vorbereitung:** `repair_mesh`, `generate_face_groups`.
*   **Bearbeitung:** `remesh_body`, `smooth_mesh`, `mesh_plane_cut`.
*   **Konvertierung:** `convert_mesh` (Mesh zu Solid via Prismatic Conversion).

### 2.5 Professional Modification (Direct Modeling)
Bearbeitung von Geometrie direkt auf Flächenebene, ideal für historienlose Modelle.
*   **Boolean:** `combine_bodies` (Join, Cut, Intersect).
*   **Manipulation:** `delete_face`, `offset_face`, `move_face`.
*   **Transformation:** `move_body`, `scale_body`, `split_body`.
*   **Detail:** `create_fillet`, `create_chamfer`, `create_shell`.

### 2.6 Assembly & Baugruppen
Strukturierung von komplexen Projekten aus mehreren Teilen.
*   **Struktur:** `create_component` (Neue Unterkomponente).
*   **Verbindung:** `create_joint` (Rigid, Revolute, Slider).
*   **Prüfung:** `check_interference` (Kollisionsprüfung).

### 2.7 Analyse & Engineering
Technische Validierung des Modells.
*   **Physik:** `get_volumetric_properties` (Masse, Volumen, Trägheit), `get_center_of_mass`.
*   **Maße:** `get_bounding_box`, `measure_distance`.
*   **Fertigung:** `create_draft_analysis` (Formschrägen-Prüfung).

---

## 3. Besonderheiten des Servers

### 3.1 Mehrzeilige Skripte & Standardausgabe
Der Server unterstützt komplexe, mehrzeilige Python-Skripte via `direct_api_access`. Sämtliche `print()`-Ausgaben innerhalb dieser Skripte werden automatisch abgefangen und als Teil der MCP-Antwort an den Nutzer zurückgegeben.

### 3.2 Kanonische Schnittstelle
Alle Werkzeuge und Parameter sind nach internationalem Standard auf **Englisch** benannt (z.B. `create_sketch` statt `skizze_erstellen`). Dies garantiert die Kompatibilität mit allen modernen KI-Clients.

### 3.3 Lokalisierte Rückmeldungen
Obwohl die Befehle Englisch sind, antwortet der Server basierend auf der Nutzersprache (aktuell Deutsch und Englisch) mit lokalisierten Erfolgsmeldungen und Fehlermeldungen.

---

## 4. Einrichtung & Neustart

### 4.1 Installation
Das Plugin muss im Fusion 360 Add-In Verzeichnis liegen:
`~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FusionMCP`

### 4.2 Neustart
Nach Code-Änderungen oder bei Session-Problemen muss das Add-In in Fusion 360:
1.  Über das Menü "Utilities" -> "Add-Ins" gestoppt werden.
2.  An gleicher Stelle wieder gestartet werden.

---

## 5. Troubleshooting
*   **-32602 (Invalid Parameters):** Stelle sicher, dass du die englischen Parameternamen aus dem Schema verwendest.
*   **404 (Not Found):** Die Session-ID ist abgelaufen. Starte die Gemini-Session neu.
*   **Timeout:** Fusion 360 blockiert den UI-Thread (z.B. durch ein offenes Dialogfenster). Schließe alle Dialoge in Fusion.
