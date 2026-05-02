# Changelog - FusionMCP

All notable changes to this project are documented in this file.

## [9.4.0] - 2026-05-02
### Added
- **Expanded sketch authoring API:** `edit_sketch` now supports additional create actions such as `draw_text`, more rectangle/polygon/slot variants, `import_svg`, and `create_spun_profile`.
- **Sketch projection and include workflows:** `edit_sketch` now supports `project_geometry`, `project_cut_edges`, `include_geometry`, `project_to_surface`, `redefine`, and `find_connected_curves`.
- **New compact 3D actions:** `apply_3d_features` now supports `create_hole`, `draft`, `circular_pattern`, `rectangular_pattern`, `path_pattern`, `create_loft`, `create_sweep`, `create_revolve`, plus additional corrective/helper actions such as `delete_body`, `rename_body`, `move_body`, `move_body_absolute`, `pattern_feature`, `rectangular_pattern_feature`, `mirror_feature`, `create_construction_plane`, `create_construction_axis`, `create_thread`, `create_coil`, `select_by_property`, `align_to_normal`, `apply_taper_to_extrude`, `edit_feature`, and `delete_feature`.
- **Assembly extensions:** `edit_assembly` now supports `create_as_built_joint` and `set_contact_sets`.
- **Analysis and developer checks:** `analyze_design` now supports `get_feature_history`, `interference_check`, `capture_view`, and `capture_side`; developer-tool tests and broader API-guide coverage were also added.
- **Direct expert scripting:** New public tool `execute_python_script` for targeted Python API workflows inside Fusion 360.

### Changed
- **Tool action guides:** The public compact documentation now describes sketch and projection actions much more precisely, including units, selectors, and aliases.
- **Sketch batch behavior:** `edit_sketch` now handles constraints, dimensions, slots, offsets, and projection paths more robustly and closer to the official Fusion API.
- **Advanced geometry:** Loft centerlines and sweep/revolve/loft batch paths were aligned with documented Fusion API patterns.
- **Public tool guidance:** `create_sketch`, `edit_assembly`, `edit_surfaces`, and `edit_forms` now include clearer usage rules and naming guidance for semantic object names.
- **README release notes:** The project overview now reflects the expanded compact-profile capabilities.

### Fixed
- **Slot creation:** `draw_slot` no longer uses an invalid `sketchSlots` path and is more robust across API and fallback paths.
- **Sketch validation:** `add_constraint`, `add_dimension`, `clear_sketch`, and other batch actions now produce more consistent results and clearer error responses.
- **Public MCP surface:** Alias/guide/tool-profile coverage and accompanying tests are now more consistent with the current compact API.

## [9.3.0] - 2026-04-30
### Added
- **Corrective compact actions:** `edit_sketch` now supports `move_entities`, `copy_entities`, and `mirror_entities`.
- **Feature inspection in the compact profile:** `analyze_design(action="get_feature_history")` now returns timeline data for later feature corrections.
- **Assembly correction:** `edit_assembly` now supports `move_component`.
- **Direct modeling in the compact profile:** `apply_3d_features` now supports `shell`, `split_body`, `delete_face`, `offset_face`, and `move_face`.
- **Feature correction in the compact profile:** `apply_3d_features` now supports `edit_feature` and `delete_feature`.

### Changed
- **AI guidance:** The public documentation and action guides were expanded to cover the new compact corrective workflows.
- **Batch referencing:** Sketch, feature, body, and component corrections now follow a more consistent analyze-first workflow.

### Fixed
- **Sketch mirroring:** The AI can now mirror sketch geometry around a referenced axis instead of rebuilding geometry manually.

## [9.2.0] - 2026-04-29
### Added
- **Unified export:** New MCP tool `export_model` for `stl`, `f3d`, and `step`.
- **Reactivated MCP modules:** `advanced_geometry`, `export`, `mechanical`, and `threads` are registered in the MCP server again.
- **Regression tests:** Added coverage for export consolidation, batch alias fields, and more robust bolt/restart paths.

### Changed
- **Export API:** The previous individual export tools were consolidated into a shared `export_model` interface.
- **Batch geometry:** `apply_3d_features` now accepts `height` aliases for `Box` and `Cylinder`, and `center` for `Cylinder`.
- **MCP restart:** `manage_design(action="restart_mcp")` now fully terminates the known MCP child process and starts it fresh.
- **Plugin stop behavior:** Stopping the Fusion add-in now always stops the MCP process as well, instead of relying on fragile reuse behavior.
- **Bolt creation:** `create_bolt` now extrudes explicitly as `NewBody` and chooses the largest cylindrical face for threading.
- **Test documentation:** The test plan and smoke test were updated for `export_model`, the real restart path, and the current batch parameters.

### Fixed
- **Batch boxes:** `apply_3d_features` no longer throws `ERR:'h'` for `Box` payloads that use `height` instead of `h`.
- **Batch cylinders:** `apply_3d_features` now handles `height` and `center` alias fields for `Cylinder` consistently.
- **MCP code reload:** MCP server changes are now reloaded reliably after `restart_mcp`.
- **Bolt threading:** Automatic thread-face detection in `create_bolt` is now more robust.

## [9.1.0] - 2026-04-27
### Added
- **Text extrusion:** `extrude_sketch` now supports extruding `SketchText` objects. Text is collected into the profile set automatically.
- **Sketches on faces:** `create_sketch` now supports creating sketches directly on body faces (`body_name`, `face_index`).
- **Expanded extrusion operations:** Added support for `Join`, `Cut`, `Intersect`, `NewBody`, and `NewComponent` in `extrude_sketch`.
- **Extrusion offset:** New `offset` parameter for `extrude_sketch` to start extrusions with an offset from the sketch plane.
- **Target-body selection:** `extrude_sketch` now supports explicit `participantBodies` selection for boolean operations.
- **Auto-targeting:** For `Cut` and `Join` without an explicit target body, all bodies in the active component are now included automatically as targets, fixing "no target body found" cases.

### Changed
- **Profile collection:** `extrude_sketch` now collects all sketch profiles by default instead of only the first one.

## [9.0.3] - 2026-04-25
### Added
- **AI test artifacts:** Added a detailed AI test plan, compact smoke test, and machine-readable YAML smoke-test file.
- **Alias test coverage:** Expanded unit tests for localized MCP tool signatures and parameter mappings.
- **MCP compatibility wrapper:** Known tool/parameter aliases and harmless client metadata such as `wait_for_previous` are accepted again during tool registration.

### Changed
- **Dynamic tool registration:** Language and parameter aliases are now loaded centrally from `i18n.json`.
- **Sketch tools:** Registration was simplified and moved back onto the shared alias logic.

## [9.0.2] - 2026-04-25
### Added
- **Expanded UI settings:** The dialog now includes configuration for the bridge server (Fusion interface).
- **Auto-restart:** The bridge server now restarts automatically when host or port is changed in the dialog.
- **Grouped view:** Settings in the dialog are now split into logical sections (Bridge, MCP, History).

## [9.0.1] - 2026-04-25
### Added
- **Command history:** A log panel in the Fusion 360 dialog now shows the last 20 executed commands with timestamps.
- **Status feedback:** Live display of server status (`RUNNING`/`STOPPED`) in the UI.
- **Refresh action:** Added manual refresh for the dialog view.

### Fixed
- **API fix:** Replaced `addSectionCommandInput` with the correct `addGroupCommandInput` method.

## [9.0.0] - 2026-04-25
### Added
- **Fusion 360 UI tool:** Added a button in the "Tools" tab / "Add-Ins" panel.
- **MCP server control:** Added the ability to start and stop the MCP server directly from Fusion 360.
- **Configuration:** Added fields for MCP host and port (slider-based configuration).
- **Add-in integration:** Added automatic copy/setup into the Fusion 360 API directory.

## [8.9.0] - Initial Build
### Added
- Base infrastructure for the HTTP bridge between Gemini CLI and Fusion 360.
- `FastMCP` server with module registration (Design, Geometry, Mechanical, etc.).
- `uv` integration for isolated Python execution inside Fusion 360.
