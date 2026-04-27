# Ultimate Testplan: FusionMCP (Standard-konforme Profi-Tests)

## Ziel
Dieser Testplan dient der vollständigen Verifizierung aller Fusion 360 MCP-Module. Er nutzt ausschließlich die **kanonischen englischen Werkzeugnamen** und deckt den gesamten Workflow vom Concept-Design bis zur Fertigungsprüfung ab.

---

## 1. Konnektivität & Basis
- **Status-Check:** `curl -s http://localhost:8081/mcp` -> `mcp_server_online`
- **Cleanup:** `cleanup_design()` -> Konstruktion leer.
- **New Doc:** `create_new_design()` -> Frisches Dokument.
- **Self-Inspection:** `list_mcp_tools()` -> Liefert vollständige Liste aller registrierten Tools.
- **Parameter:** `manage_parameter(name="Breite", expression="50mm")` -> Erstellt.
- **List Params:** `list_parameters()` -> JSON mit "Breite" enthalten.

---

## 2. Solid Modeling (Das "Create" Menü)
- **Primitives:**
  - `create_box(l=10, w=10, h=10, name="Base")`
  - `create_cylinder(r=5, h=20, name="Pillar")`
  - `create_sphere(r=5, name="Ball")`
- **Bekannte Einschränkungen:**
  - `create_coil(...)` -> [EXPECTED: ERR_UNSUPPORTED] (Kommando im API-Kontext nicht ausführbar).
- **Sketch-based:**
  - `create_sketch(name="Profile", plane_name="XY")` + `draw_circle(...)`
  - `create_revolve(sketch_name="Profile", axis="Z", angle=360)` -> Toroidaler Körper.
  - `create_sweep_advanced(profile_sketch="S1", path_sketch="P1", twist=15)` -> Verdrehter Flügel.
  - `create_loft(sketch_names=["S1", "S2"])` -> Übergangskörper.
- **Holes & Threads:**
  - `create_hole_advanced(body="Base", dia=8, depth=20, hole_type="Counterbore", cb_dia=12, cb_depth=5)` -> Profi-Bohrung.
  - `apply_custom_thread(body_name="Pillar", thread_type="ISO Metric profile", size="10")` -> Gewinde.

---

## 3. Surface Design (Freiform-Flächen)
- **Creation:** `create_surface_cylinder(r=10, h=50, name="Hull")`
- **Modification:** 
  - `extend_surface(body="Hull", distance=5)` -> Verlängert.
  - `trim_surface(body="Hull", tool_sketch="TrimLine")` -> Beschnitten.
- **Solid-Weg:** `stitch_surfaces(body_names=["S1", "S2"])` -> Solid (automatisches Zusammenfügen).

---

## 4. Mesh Tools (3D-Druck & Scans)
- **Import:** `import_mesh(path="/pfad/zu/modell.stl")` -> Mesh geladen.
- **Prepare:**
  - `generate_face_groups(body="Mesh1")` -> Gruppen erkannt.
  - `repair_mesh(body="Mesh1")` -> Wasserdicht.
- **Convert:** `convert_mesh(body="Mesh1", conv_type="infoPrismatic")` -> B-Rep Solid erstellt.

---

## 5. Form Design (Organische T-Splines)
- **Primitives (Eingeschränkt):**
  - `create_form_box`, `create_form_sphere`, etc. -> [EXPECTED: ERR_UNSUPPORTED] (Runtime-Exponierung fehlt).
- **Modification (Edit):**
  - `insert_form_edge(body="Organic")` -> Kante eingefügt.
  - `subdivide_form_face(body="Organic")` -> Mehr Details.
  - `create_form_crease(body="Organic")` -> Scharfe Kante.
- **Symmetry:** `create_form_mirror_internal(body="Organic")` -> Grüne Symmetrie-Linie sichtbar.

---

## 6. Professional Modification (Inkrementelles Editing)
- **Boolean & Patterns:**
  - `combine_bodies(target="Base", tool_bodies=["Pillar"], operation="Cut")` -> Schnitt.
  - `create_feature_pattern(feature_name="Extrude1", count=3)` -> [NEW] Muster von Operationen (Join garantiert).
- **Direct Edit:**
  - `delete_body(body="TempBody")` -> [NEW] Gezieltes Löschen.
  - `rename_body(old_name="Body1", new_name="FinalPart")` -> [NEW] Umbenennung.
  - `delete_face(body="Base", face_index=0)` -> Fläche entfernt.
- **Precise Transform:**
  - `move_body(body="Base", x=5, y=0, z=0)` -> Relativ.
  - `move_body_absolute(body="Base", x=10, y=0, z=0)` -> [NEW] Absolut (Schwerpunkt-basiert).

---

## 7. Assembly & Timeline (Struktur & Historie)
- **Component Management:** `create_component(name="Sub_Assembly")` -> Baugruppe erstellt.
- **Joints:** `create_joint(comp1="Parent", comp2="Child", joint_type="Rigid")` -> Verbindung.
- **Timeline Manipulation:**
  - `get_feature_history()` -> [NEW] Listet alle Arbeitsschritte.
  - `delete_feature(feature_name="Fillet1")` -> [NEW] Löscht Operation aus Timeline.
  - `edit_feature(feature_name="Extrude1", value="20mm")` -> [NEW] Ändert Parameter.

---

## 8. Analyse & Validierung
- **Spatial Awareness:** `get_scene_map()` -> [NEW] Karte aller Schwerpunkte & Bounding Boxen.
- **Construction Integrity:** `validate_model()` -> [NEW] Prüft Manifold, Body Count & Interferenz.
- **Visuals:** `capture_standard_views()` -> [NEW] Top, Front, Right, ISO Screenshots.
- **Export:** `export_f3d(filename="archive")` -> [NEW] Gesamtes Projekt exportieren.

---

## Ergebnis-Matrix
| Task | Modul | Status | Bemerkung |
| :--- | :--- | :--- | :--- |
| 1 | Core/Status | [ ] | SSE & list_mcp_tools |
| 2 | Inkrementelles Edit | [ ] | move_absolute & rename |
| 3-6 | Solid/Timeline | [ ] | Feature Patterns & History |
| 7 | Validierung | [ ] | Manifold & Standard Views |

Tests sind mit `[PASS]` oder `[FAIL]` zu kennzeichnen.
