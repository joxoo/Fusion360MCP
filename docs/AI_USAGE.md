# FusionMCP AI Usage

<!-- Generated from modules/tool_action_guides.json by scripts/generate_ai_usage.py -->

This file defines the preferred usage pattern for AI clients working against the compact public FusionMCP API.

## Public API First

Prefer the compact public tools:

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
- `execute_python_script`

Do not assume internal or specialist tools are available unless the server explicitly runs with `--api-profile full`.

## Recommended Workflow

1. Inspect before editing. Use `analyze_design(action="get_assembly_tree")` for assemblies and `analyze_design(action="scene_map")` or `validate` before major modeling changes.
2. Create sketches before sketch-based solids. Use `create_sketch`, then `edit_sketch`, then `apply_3d_features`.
3. Prefer batch actions over imaginary specialist tools. Use `apply_3d_features` instead of assuming separate public tools like `extrude_sketch` or `combine_bodies`. Use `edit_assembly` instead of assuming separate public tools like `create_component` or `create_joint`.
4. Export only at the end. Use `export_model` once the design is already in the desired final state.

## Component Scope Rules

- Prefer `component_path` over `component_name`.
- Use full nested paths like `Root/Frame/Arm`.
- For joint creation, prefer `component1_path` and `component2_path`.
- Use `component_name` only as a fallback when the component is unambiguous.

## Tool Selection Hints

### `manage_design`

Use for design-level lifecycle tasks, not geometry editing.

Actions:
- `cleanup`: required none
- `create_new`: required none
- `restart_mcp`: required none

### `analyze_design`

Use before editing when you need assembly structure, validation, or scene context.

Rules:
- Use returned component_path and body_ref fields from analysis results to target existing components and bodies in later edit calls.
- Prefer body_ref.component_path plus body_ref.body over guessing names from the viewport.
- For sketch corrections, reuse sketch_ref, curve_ref, constraint_ref, and dimension_ref from get_assembly_tree or validate instead of inventing indices.
- Use get_feature_history before editing or deleting a feature so later apply_3d_features actions can target an existing feature by name.

Actions:
- `get_assembly_tree`: required `action`
- `get_feature_history`: required `action`
- `validate`: required `action`
- `scene_map`: required `action`
- `physical_data`: required `action`
- `bounding_box`: required `action`
- `interference_check`: required `action` (Detects collisions between components)
- `capture_view`: required `action`, optional `width`, `height`
- `capture_side`: required `action` (Captures orthographic right side view)

### `list_parameters`

Use before editing parameters when you need current parameter names or values.

### `edit_parameters`

Use to create, update, or delete user parameters in one call.

Actions:
- `set`: required `name`, `expr`
- `delete`: required `name`

### `create_sketch`

Use to create a new sketch on a plane or on a body face before sketch editing or extrusion.

Rules:
- Prefer component_path for nested assemblies.
- Use body_name plus face_index when the sketch must be attached to an existing face.
- The resolved target component is activated before sketch creation so the sketch lands in the intended assembly context.
- If component_path is omitted for nested assemblies, Fusion may use the currently active component and place the sketch in the wrong location.
- Always give new sketches semantic names that describe intent or role. Avoid placeholders like Sketch1, Sketch2, or NewSketch.

### `edit_sketch`

Use to modify one existing sketch with multiple 2D operations in a single call.

Rules:
- You can target the sketch with sketch_name or reuse sketch_ref from analyze_design.
- For curve edits such as delete_curve, set_construction, or trim, prefer curve_ref from analyze_design and only fall back to raw curve_index when needed.
- For constraint and dimension edits, prefer constraint_ref and dimension_ref from analyze_design or validate.
- When creating a sketch earlier in the workflow, keep its name semantic and stable so later edit_sketch calls can target it reliably.
- Sketch coordinates and distances are passed through in Fusion Design internal units. For lengths, that means centimeters unless you explicitly convert before calling.

Actions:
- `draw_line`: required `x1`, `y1`, `x2`, `y2`
- `draw_circle`: required `x`, `y`, `r`
- `draw_rectangle`: required `x1`, `y1`, `x2`, `y2`
- `draw_center_rectangle`: required `cx`, `cy`, `x`, `y`
- `draw_three_point_rectangle`: required `x1`, `y1`, `x2`, `y2`, `x3`, `y3`
- `draw_polygon`: required `cx`, `cy`, `r`, `sides`
- `draw_inscribed_polygon`: required `cx`, `cy`, `r`, `sides`
- `draw_circumscribed_polygon`: required `cx`, `cy`, `r`, `sides` where `r` is the apothem radius to the sides
- `draw_edge_polygon`: required `x1`, `y1`, `x2`, `y2`, `sides`; optional `flip`
- `draw_arc`: required `cx`, `cy`, `sx`, `sy`, `angle`
- `draw_spline`: required `pts`
- `draw_slot`: required `x1`, `y1`, `x2`, `y2`, `width` for a center-to-center slot; `x1,y1` and `x2,y2` are the end-arc centers
- `draw_overall_slot`: required `x1`, `y1`, `x2`, `y2`, `width` for an overall slot; `x1,y1` and `x2,y2` are the outer endpoints
- `draw_center_point_slot`: required `cx`, `cy`, `x`, `y`, `width` for a center-point slot
- `draw_ellipse`: required `cx`, `cy`, `mx`, `my`, `ox`, `oy`
- `draw_text`: required `text`, `x`, `y`; optional `height`, `font`
- `import_svg`: required `path`; optional `x`, `y`, `scale`
- `create_spun_profile`: required `body`; uses Fusion `Sketch.createSpunProfileInput`; optional `face_index` or `face_indices`, `bodies`, `axis`, `axis_curve_index`, `axis_curve_ref`, `axis_body` plus `axis_edge_index`, `flip_result`, `is_axis_projected`, `is_centerline_added`, `tolerance`
- `project_geometry`: projects selected sketch curves or model geometry into the sketch; supports `curve_index`/`curve_indices`/`curve_ref`/`curve_refs`, or `body` plus optional `face_index`/`face_indices`, `edge_index`/`edge_indices`, `vertex_index`/`vertex_indices`; optional `is_linked`
- `project_cut_edges`: required `body`
- `include_geometry`: includes selected geometry without planar projection; selectors match `project_geometry`
- `project_to_surface`: project selected sketch curves onto `body` target faces using `face_index` or `face_indices`; `projection_type` accepts `closest_point` or `along_vector`; along-vector projection also needs `direction_axis`, `direction_curve_index`, or `direction_curve_ref`
- `redefine`: changes the sketch plane; use `plane_name` with `XY`, `XZ`, or `YZ`, or use `body` plus `face_index`
- `find_connected_curves`: required `curve_index` or `curve_ref`
- `offset`: required `dist`; optional `seed_curve_index` or `seed_curve_ref` to auto-expand a connected chain via Fusion `findConnectedCurves`
- `circular_pattern`: required `cx`, `cy`, `count`
- `rectangular_pattern`: required `count_x`, `dist_x`
- `delete_curve`: required `curve_index`
- `move_entities`: required `curve_indices`, `dx`, `dy`
- `copy_entities`: required `curve_indices`, `dx`, `dy`
- `mirror_entities`: required `curve_indices`, `mirror_curve_index`
- `set_construction`: required `curve_index`
- `trim`: required `curve_index`, `x`, `y`
- `clear_sketch`: required none
- `add_constraint`: required `type` and curve selection via `curve_index`/`curve_ref`, or for pair constraints via `curve_indices`/`curve_refs`; accepted type aliases include `HorizontalConstraint`, `VerticalConstraint`, `ParallelConstraint`, `PerpendicularConstraint`, `CollinearConstraint`, `TangentConstraint`, `ConcentricConstraint`
- `remove_constraint`: required `constraint_index`
- `add_dimension`: required `type` and curve selection via `curve_index`/`curve_ref`, or for pair dimensions via `curve_indices`/`curve_refs`; accepted type aliases include `Distance`, `DistanceDimension`, `RadialDimension`, `DiameterDimension`, `AngularDimension`
- `set_dimension`: required `dimension_index`, `value`
- `delete_dimension`: required `dimension_index`

### `apply_3d_features`

Use for most solid modeling changes after a sketch exists.

Rules:
- Prefer component_path on each operation when working in nested components.
- Use target_body for Join/Cut when the target body is known.
- Use get_feature_history from analyze_design before edit_feature or delete_feature so the feature name comes from the actual timeline.
- Component-aware creation actions activate the resolved target component before creating bodies.
- If component_path is omitted for nested assemblies, primitive creation may fall back to the wrong active component.
- Always provide semantic body names for new bodies. Avoid placeholders like Body1, Body2, or NewBody.
- Length values are passed through in Fusion Design internal units. For distances, that means centimeters unless you convert before calling.
- Angle values passed as plain numbers use Fusion internal angle units, which means radians.

Actions:
- `extrude`: required `sketch`, `dist`
- `create_hole`: required `body`, `dia`, `depth` unless `through_all`; optional `face_index`, `x`, `y`, `hole_type`, `cb_dia`, `cb_depth`, `cs_dia`, `cs_angle`
- `draft`: required `body`, `face_index`, `angle`; optional `pull_plane`, `is_tangent_chain`, `is_symmetric`, `flip_direction`
- `create_loft`: required `sketch_names`, optional `centerline_sketch` (single connected curve/path)
- `create_sweep`: required `profile_sketch`, `path_sketch`, optional `taper`, `twist` (angles in radians when sent as numbers)
- `create_revolve`: required `profile_sketch`, optional `axis`, `axis_sketch`, `angle` (angle in radians when sent as a number)
- `circular_pattern`: required `body`, `count`; optional `axis`, `total_angle` (radians)
- `rectangular_pattern`: required `body`, `count_x`, `dist_x`; optional `count_y`, `dist_y`, `axis_one`, `axis_two`
- `path_pattern`: required `body`, `path_sketch`, `count`, `dist`; optional `is_symmetric`
- `fillet`: required `body`, `radius`
- `chamfer`: required `body`, `dist`
- `combine`: required `target`, `tools`, `op`
- `create_box`: required `l`, `w`, `h`, `name`
- `create_cylinder`: required `r`, `h`, `name`
- `delete_body`: required `body`
- `rename_body`: required `body`, `new_name`
- `move_body`: required `body`; optional `x`, `y`, `z` (translation), `rx`, `ry`, `rz` (rotation in radians around center of mass)
- `move_body_absolute`: required `body`, `x`, `y`, `z`; optional `rx`, `ry`, `rz` (rotation in radians after translation)
- `execute_python`: required `script`; expert tool to run Python code within a batch; access to `adsk`, `app`, `design`, `root`, `active_comp`, `params`, `returnValue`
- `pattern_feature`: required `feature_name`, `count`; optional `axis`, `total_angle` (radians); patterns a named feature instead of a body
- `rectangular_pattern_feature`: required `feature_name`, `count_x`, `dist_x`; optional `count_y`, `dist_y`, `axis_one`, `axis_two`
- `mirror_feature`: required `feature_name`; optional `plane` (XY, XZ, YZ)
- `create_construction_plane`: optional `plane_type` (offset or angle), `base_plane`, `offset`, `axis`, `angle`
- `create_construction_axis`: optional `axis_type` (two_point or cylinder), `x1`, `y1`, `z1`, `x2`, `y2`, `z2`, `body`, `face_index`
- `create_thread`: required `body`; optional `face_index`, `thread_type`, `size`, `designation`, `thread_class`, `is_modeled`
- `create_coil`: required `dia`, `height`, `pitch`; optional `center`, `op`
- `select_by_property`: required `body`, `property` (area or length); optional `min_val`, `max_val`; returns indices of faces/edges matching criteria
- `align_to_normal`: required `body`, `target_body`; optional `face_index`, `align_axis` (X, Y, or Z); aligns body axis to target face normal
- `apply_taper_to_extrude`: required `feature_name`, `taper` (angle in radians)
- `scale_body`: required `body`, `factor`
- `shell`: required `body`, `thick`
- `split_body`: required `body`, `tool`
- `delete_face`: required `body`, `face_index`
- `offset_face`: required `body`, `face_index`, `dist`
- `move_face`: required `body`, `face_index`
- `edit_feature`: required `feature_name`
- `delete_feature`: required `feature_name`

### `edit_assembly`

Use for assembly structure and joints.

Rules:
- Prefer component_path over component_name for nested assemblies.
- For joints, prefer component1_path and component2_path.
- Create components first, then use their component paths in later sketch or body creation so activation can target the correct assembly context.
- After create_component, use the returned or expected component path in later calls instead of relying on the currently active component.
- Always give components semantic names that describe function or placement. Avoid placeholders like Component1, Component2, or New Component.

Actions:
- `create_component`: required `action`, `name`
- `rename_component`: required `action`, `new_name`
- `delete_component`: required `action`
- `move_component`: required `action`
- `create_joint`: required `action`, `type`
- `create_as_built_joint`: required `action`, `type`, `component1_path`, `component2_path`
- `set_contact_sets`: required `action`, `enable`

### `edit_surfaces`

Use for grouped surface operations instead of direct solid modeling tools.

Rules:
- Prefer component_path when the action references a sketch in a nested component.
- Use body_names for stitch and body for offset or thicken.
- Provide semantic names for newly created surface bodies whenever possible.

Actions:
- `patch`: required `sketch`
- `offset`: required `body`, `dist`
- `stitch`: required `body_names`
- `thicken`: required `body`, `thick`

### `edit_forms`

Use for grouped T-Spline form operations.

Rules:
- Use sketch plus dist for form extrusion.
- Use body for display mode, symmetry, or conversion actions on existing T-Spline bodies.
- Provide semantic names for newly created form bodies whenever possible.

Actions:
- `extrude`: required `sketch`, `dist`
- `set_display_mode`: required `body`
- `clear_symmetry`: required `body`
- `convert`: required `body`

### `import_mesh`

Use to bring STL or OBJ geometry into the active Fusion design.

### `edit_mesh`

Use for grouped mesh repair, smoothing, remesh, or conversion actions.

### `execute_python_script`

Expert: Use to execute complex modeling logic directly in Fusion 360 using the Python API. Best for loops, mathematical patterns (e.g. Fibonacci spirals), or operations not exposed via standard tools.

Rules:
- The script has access to `adsk`, `app`, `design`, `root`, `active_comp`, and `params`.
- Store results to be returned in the `returnValue` list (e.g. `returnValue.append('Success')`).
- Use this tool sparingly and prefer standard tools when possible for better traceability.

### `export_model`

Use only after the design is in the desired final state.

## Error Interpretation

- `component_not_found`: the requested component or path could not be resolved.
- `entity_owner_mismatch`: referenced geometry belongs to incompatible component contexts.
- `cross_component_operation_not_supported`: the operation is not valid across components.
- `sketch_not_found`: the sketch does not exist in the expected scope.
- `body_not_found`: the body does not exist in the expected scope.

## Minimal Examples

Create Sketch:

```json
{
  "plane_name": "XY",
  "name": "BaseSketch",
  "component_path": "Root/Bracket"
}
```

Edit Sketch:

```json
{
  "sketch_name": "BaseSketch",
  "operations": [
    { "action": "draw_rectangle", "x1": 0, "y1": 0, "x2": 4, "y2": 2 },
    { "action": "draw_circle", "x": 2, "y": 1, "r": 0.3 },
    { "action": "delete_curve", "curve_index": 0 }
  ]
}
```

Apply 3D Features (Advanced):

```json
{
  "operations": [
    { "action": "extrude", "sketch": "BaseSketch", "dist": 2.0, "name": "MainBody" },
    { "action": "create_revolve", "profile_sketch": "HalfCircle", "axis": "z", "angle": 6.28 }
  ]
}
```

Analyze Design (Interference):

```json
{
  "action": "interference_check"
}
```

Edit Assembly (As-Built Joint):

```json
{
  "operations": [
    { 
      "action": "create_as_built_joint", 
      "component1_path": "Root/Fuselage", 
      "component2_path": "Root/Cockpit", 
      "type": "Rigid" 
    }
  ]
}
```

Execute Python Script (Expert):

```json
{
  "script": "import math\nfor i in range(10):\n  # complex logic here\n  pass\nreturnValue.append('Finished loop')",
  "params": {}
}
```
