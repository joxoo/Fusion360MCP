# Ultimate Testplan: FusionMCP (Standard-konforme Profi-Tests)

## Ziel
Dieser Testplan dient der vollständigen Verifizierung aller Fusion 360 MCP-Module. Er nutzt ausschließlich die **kanonischen englischen Werkzeugnamen** und deckt den gesamten Workflow vom Concept-Design bis zur Fertigungsprüfung ab.

---

## 1. Konnektivität & Basis
- **Status-Check:** `curl -s http://localhost:8081/mcp` -> `mcp_server_online`
- **Cleanup:** `cleanup_design()` -> Konstruktion leer.
- **New Doc:** `create_new_design()` -> Frisches Dokument.
- **Parameter:** `manage_parameter(name="Breite", expression="50mm")` -> Erstellt.
- **List Params:** `list_parameters()` -> JSON mit "Breite" enthalten.

---

## 2. Solid Modeling (Das "Create" Menü)
- **Primitives:**
  - `create_box(l=10, w=10, h=10, name="Base")`
  - `create_cylinder(r=5, h=20, name="Pillar")`
  - `create_sphere(r=5, name="Ball")`
  - `create_coil(dia=10, h=30, p=5, sec_t=2, name="Spring")`
- **Sketch-based:**
  - `create_sketch(name="Profile", plane_name="XY")` + `draw_circle(...)`
  - `create_revolve(sketch_name="Profile", axis="Z", angle=360)` -> Toroidaler Körper.
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
- **Solid-Weg:** `stitch_surfaces(body_names=["S1", "S2"])` -> Solid.

---

## 4. Mesh Tools (3D-Druck & Scans)
- **Import:** `import_mesh(path="/pfad/zu/modell.stl")` -> Mesh geladen.
- **Prepare:**
  - `generate_face_groups(body="Mesh1")` -> Gruppen erkannt.
  - `repair_mesh(body="Mesh1")` -> Wasserdicht.
- **Convert:** `convert_mesh(body="Mesh1", conv_type="infoPrismatic")` -> B-Rep Solid erstellt.

---

## 5. Form Design (Organische T-Splines)
- **Creation:** `create_form_box(l=10, w=10, h=10, name="Organic")`
- **Modification:**
  - `subdivide_form_face(body="Organic")` -> Mehr Details.
  - `create_form_crease(body="Organic")` -> Scharfe Kante.
- **Symmetry:** `create_form_mirror_internal(body="Organic")` -> Grüne Symmetrie-Linie sichtbar.

---

## 6. Professional Modification (Direct Modeling)
- **Combine:** `combine_bodies(target="Base", tool_bodies=["Pillar"], operation="Cut")` -> Loch in Base.
- **Direct Edit:**
  - `delete_face(body="Base", face_index=0)` -> Feature entfernt.
  - `offset_face(body="Base", dist=2.0)` -> Maß geändert.
- **Transform:** `move_body(body="Base", x=5, y=0, z=0, angle=45)` -> Verschoben & rotiert.

---

## 7. Assembly & Baugruppen (Hierarchie & Kontext)
- **Component Creation:** `create_component(name="Sub_Assembly")` -> Baugruppe erstellt UND automatisch aktiviert.
- **Hierarchical Placement:** 
  - `create_component(name="Baugruppe_A")`
  - `create_cylinder(r=10, h=40, name="Körper_in_A")`
  - **Check:** Körper liegt physisch in `Baugruppe_A` (nicht im Root).
- **Nested Components:**
  - `create_component(name="Parent")`
  - `create_component(name="Child")`
  - **Check:** `Child` ist eine Unter-Komponente von `Parent`.
- **Joints:** `create_joint(comp1="Parent", comp2="Child", joint_type="Rigid")` -> Verbindung zwischen Ebenen.
- **Hierarchy Split:** `split_body(body="Körper_in_A", tool="XY")` -> Nutzt Konstruktionsebene der aktiven Komponente.

---

## 8. Analyse & Export
- **Physics:** `get_volumetric_properties(body="Base")` -> Masse, Volumen, Trägheit.
- **Dimensions:** `get_bounding_box(body="Base")` -> Länge, Breite, Höhe.
- **Visuals:** `capture_view()` -> Screenshot.
- **Export:** `export_step(filename="final_model")` -> STEP-Datei erzeugt.

---

## Ergebnis-Matrix
| Task | Modul | Status | Bemerkung |
| :--- | :--- | :--- | :--- |
| 1 | Core/Bridge | [ ] | Multi-line & Stdout |
| 2 | Registration | [ ] | Canonical Names |
| 3-6 | Solid/Surface/Mesh/Form | [ ] | Komplett |
| 7 | Analysis/Assembly | [ ] | Interferenz & Physik |

Tests sind mit `[PASS]` oder `[FAIL]` zu kennzeichnen.
