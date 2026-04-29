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

Actions:
- `get_assembly_tree`: required `action`
- `validate`: required `action`
- `scene_map`: required `action`
- `physical_data`: required `action`
- `bounding_box`: required `action`

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

Examples:
```json
{
  "plane_name": "XY",
  "name": "BaseSketch",
  "component_path": "Root/Bracket"
}
```
```json
{
  "name": "FaceSketch",
  "body_name": "BracketBody",
  "face_index": 0
}
```

### `edit_sketch`

Use to modify one existing sketch with multiple 2D operations in a single call.

Actions:
- `draw_line`: required `x1`, `y1`, `x2`, `y2`
- `draw_circle`: required `x`, `y`, `r`
- `draw_rectangle`: required `x1`, `y1`, `x2`, `y2`
- `draw_polygon`: required `cx`, `cy`, `r`, `sides`
- `add_constraint`: required `type`

Examples:
```json
{
  "sketch_name": "BaseSketch",
  "operations": [
    {
      "action": "draw_rectangle",
      "x1": 0,
      "y1": 0,
      "x2": 4,
      "y2": 2
    },
    {
      "action": "draw_circle",
      "x": 2,
      "y": 1,
      "r": 0.3
    }
  ]
}
```

### `apply_3d_features`

Use for most solid modeling changes after a sketch exists.

Rules:
- Prefer component_path on each operation when working in nested components.
- Use target_body for Join/Cut when the target body is known.
- Component-aware creation actions activate the resolved target component before creating bodies.
- If component_path is omitted for nested assemblies, primitive creation may fall back to the wrong active component.

Actions:
- `extrude`: required `sketch`, `dist`
- `fillet`: required `body`, `radius`
- `chamfer`: required `body`, `dist`
- `combine`: required `target`, `tools`, `op`
- `create_box`: required `l`, `w`, `h`, `name`
- `create_cylinder`: required `r`, `h`, `name`

### `edit_assembly`

Use for assembly structure and joints.

Rules:
- Prefer component_path over component_name for nested assemblies.
- For joints, prefer component1_path and component2_path.
- Create components first, then use their component paths in later sketch or body creation so activation can target the correct assembly context.
- After create_component, use the returned or expected component path in later calls instead of relying on the currently active component.

Actions:
- `create_component`: required `action`, `name`
- `create_joint`: required `action`, `type`

### `edit_surfaces`

Use for grouped surface operations instead of direct solid modeling tools.

Rules:
- Prefer component_path when the action references a sketch in a nested component.
- Use body_names for stitch and body for offset or thicken.

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

Actions:
- `extrude`: required `sketch`, `dist`
- `set_display_mode`: required `body`
- `clear_symmetry`: required `body`
- `convert`: required `body`

### `import_mesh`

Use to bring STL or OBJ geometry into the active Fusion design.

Examples:
```json
{
  "path": "/absolute/path/model.stl"
}
```

### `edit_mesh`

Use for grouped mesh repair, smoothing, remesh, or conversion actions.

Rules:
- Each action requires body and the target must already be a mesh body.
- Use density for remesh, smoothing for smooth, repair_type for repair, and conv_type for convert.

Actions:
- `remesh`: required `body`
- `smooth`: required `body`
- `repair`: required `body`
- `convert`: required `body`

### `export_model`

Use only after the design is in the desired final state.

Examples:
```json
{
  "format": "step",
  "filename": "assembly_export"
}
```

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
```json
{
  "name": "FaceSketch",
  "body_name": "BracketBody",
  "face_index": 0
}
```

Edit Sketch:

```json
{
  "sketch_name": "BaseSketch",
  "operations": [
    {
      "action": "draw_rectangle",
      "x1": 0,
      "y1": 0,
      "x2": 4,
      "y2": 2
    },
    {
      "action": "draw_circle",
      "x": 2,
      "y": 1,
      "r": 0.3
    }
  ]
}
```

Apply 3D Features:

```json
{
  "action": "extrude",
  "sketch": "BaseSketch",
  "dist": 2.0,
  "op": "NewBody",
  "component_path": "Root/Bracket"
}
```

Edit Assembly:

```json
{
  "action": "create_component",
  "name": "Arm",
  "component_path": "Root/Frame"
}
```
