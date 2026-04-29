# Consolidated Testplan: FusionMCP (Batch-Architecture)

## Ziel
Dieser Testplan dient der Verifizierung der konsolidierten Batch-Architektur von FusionMCP. Er nutzt die neuen "Core Tools", die mehrere Operationen in einem Aufruf bündeln, um Token-Bloat zu reduzieren und die Effizienz zu steigern.

---

## 1. Core & Design Management
- **Status Check:** `curl http://localhost:8081/mcp` (Sollte `mcp_server_online` zurückgeben)
- **Basic Management:** 
  - `manage_design(action="cleanup")` -> Bereinigt das Design.
  - `manage_design(action="create_new")` -> Erstellt ein leeres Design.
- **Export/Import:**
  - `manage_design(action="export_step", filename="test_model")`
  - `import_mesh(path="path/to/mesh.obj")`

---

## 2. Sketch Operations (Batch)
- **Create Sketch:** `create_sketch(plane_name="XY", name="Base")` (Entry point)
- **Edit Sketch:** `edit_sketch(sketch_name="Base", operations=[...])`
  - `{"action": "draw_circle", "x": 0, "y": 0, "radius": 5}`
  - `{"action": "draw_line", "x1": 0, "y1": 0, "x2": 10, "y2": 10}`
  - `{"action": "draw_rectangle", "x1": -5, "y1": -5, "x2": 5, "y2": 5}`
  - `{"action": "draw_polygon", "cx": 10, "cy": 10, "radius": 3, "sides": 6}`
  - `{"action": "add_constraint", "type": "Horizontal", "entity1_id": 0}`

---

## 3. 3D Geometry & Features (Batch)
- **Apply Features:** `apply_3d_features(operations=[...])`
  - `{"action": "create_box", "l": 10, "w": 10, "h": 5, "name": "Box1"}`
  - `{"action": "create_cylinder", "r": 5, "h": 10, "name": "Cyl1"}`
  - `{"action": "extrude", "sketch": "Base", "dist": 10 }`
  - `{"action": "fillet", "body": "Box1", "radius": 2}`
  - `{"action": "chamfer", "body": "Box1", "distance": 1}`

---

## 4. Assembly & Parameters (Batch)
- **Assembly:** `edit_assembly(operations=[...])`
  - `{"action": "create_component", "name": "SubAssembly"}`
  - `{"action": "move_component", "component": "SubAssembly", "x": 10, "y": 0, "z": 0}`
- **Parameters:**
  - `list_parameters()` -> Listet existierende Parameter.
  - `edit_parameters(operations=[{"action": "set", "name": "length", "expression": "100mm"}])`

---

## 5. Specialty Domains (Batch)
- **Mesh:** `edit_mesh(operations=[{"action": "remesh", "body": "Mesh1", "density": 0.5}])`
- **Surfaces:** `edit_surfaces(operations=[{"action": "patch", "sketch": "Profile"}])`
- **Forms (T-Splines):** `edit_forms(operations=[{"action": "extrude", "sketch": "FormProfile", "distance": 10}])`

---

## 6. Analysis & Visuals
- **Validate:** `analyze_design(action="validate")`
- **Assembly Tree:** `analyze_design(action="get_assembly_tree")`
- **Scene Map:** `analyze_design(action="scene_map")` -> Räumliche Karte aller Körper (Schwerpunkte + Bboxes).
- **Physical Data:** `analyze_design(action="physical_data", body="Box1")` -> Masse, Volumen, Trägheit.
- **Bounding Box:** `analyze_design(action="bounding_box", body="Box1")` -> Außenabmessungen.
- **Visual Evidence:** `capture_view()` (Erstellt Screenshot)

---

## 7. Feature Manipulation
- **History:** `get_feature_history()` -> Listet die Timeline-Features auf.
- **Edit Feature:** `edit_feature(feature_name="Extrude1", new_name="BaseExtrude", suppress=False, value="15mm")`
- **Delete Feature:** `delete_feature(feature_name="Fillet1")`

---

## Ergebnis-Matrix
| Task | Modul | Tool | Status |
| :--- | :--- | :--- | :--- |
| 1 | core | manage_design | [x] Verified |
| 2 | sketch | create_sketch / edit_sketch | [x] Verified |
| 3 | geometry | apply_3d_features | [x] Verified |
| 4 | assembly | edit_assembly | [x] Verified |
| 5 | parameters| list_parameters / edit_parameters | [x] Verified |
| 6 | mesh | edit_mesh | [x] Verified |
| 7 | surfaces | edit_surfaces | [x] Verified |
| 8 | forms | edit_forms | [x] Verified |
| 9 | analysis | analyze_design (Consolidated) | [x] Verified |
| 10| features | get_feature_history / edit_feature | [x] Verified |
| 11| visual | capture_view | [x] Verified |
