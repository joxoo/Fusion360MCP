#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = ROOT / "modules" / "tool_action_guides.json"
OUTPUT_PATH = ROOT / "docs" / "AI_USAGE.md"

PUBLIC_TOOLS = [
    "manage_design",
    "describe_tool_actions",
    "analyze_design",
    "list_parameters",
    "edit_parameters",
    "create_sketch",
    "edit_sketch",
    "apply_3d_features",
    "edit_assembly",
    "edit_surfaces",
    "edit_forms",
    "import_mesh",
    "edit_mesh",
    "export_model",
]

WORKFLOW = [
    'Inspect before editing. Use `analyze_design(action="get_assembly_tree")` for assemblies and `analyze_design(action="scene_map")` or `validate` before major modeling changes.',
    "Create sketches before sketch-based solids. Use `create_sketch`, then `edit_sketch`, then `apply_3d_features`.",
    "Prefer batch actions over imaginary specialist tools. Use `apply_3d_features` instead of assuming separate public tools like `extrude_sketch` or `combine_bodies`. Use `edit_assembly` instead of assuming separate public tools like `create_component` or `create_joint`.",
    "Export only at the end. Use `export_model` once the design is already in the desired final state.",
]

SCOPE_RULES = [
    "Prefer `component_path` over `component_name`.",
    "Use full nested paths like `Root/Frame/Arm`.",
    "For joint creation, prefer `component1_path` and `component2_path`.",
    "Use `component_name` only as a fallback when the component is unambiguous.",
]

ERRORS = [
    "`component_not_found`: the requested component or path could not be resolved.",
    "`entity_owner_mismatch`: referenced geometry belongs to incompatible component contexts.",
    "`cross_component_operation_not_supported`: the operation is not valid across components.",
    "`sketch_not_found`: the sketch does not exist in the expected scope.",
    "`body_not_found`: the body does not exist in the expected scope.",
]

EXAMPLE_ORDER = ["create_sketch", "edit_sketch", "apply_3d_features", "edit_assembly"]


def fenced_json(value: object) -> str:
    return "```json\n" + json.dumps(value, indent=2) + "\n```"


def load_guides() -> dict:
    with GUIDE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_tool_section(tool_name: str, guide: dict) -> list[str]:
    lines = [f"### `{tool_name}`", ""]
    when = guide.get("when_to_use")
    if when:
        lines.append(when)
        lines.append("")

    rules = guide.get("rules", [])
    if rules:
        lines.append("Rules:")
        for rule in rules:
            lines.append(f"- {rule}")
        lines.append("")

    actions = guide.get("actions", {})
    if actions:
        lines.append("Actions:")
        for action_name, action_guide in actions.items():
            required = ", ".join(f"`{item}`" for item in action_guide.get("required", [])) or "none"
            lines.append(f"- `{action_name}`: required {required}")
        lines.append("")

    examples = []
    if "example" in guide:
        examples.append(guide["example"])
    examples.extend(guide.get("examples", []))
    if examples:
        lines.append("Examples:")
        for example in examples:
            lines.append(fenced_json(example))
        lines.append("")

    return lines


def render_example_section(guides: dict) -> list[str]:
    lines = ["## Minimal Examples", ""]
    for tool_name in EXAMPLE_ORDER:
        guide = guides.get(tool_name, {})
        title = tool_name.replace("_", " ").title()
        lines.append(title + ":")
        lines.append("")

        if "example" in guide:
            lines.append(fenced_json(guide["example"]))
        else:
            for example in guide.get("examples", []):
                lines.append(fenced_json(example))

        action_examples = []
        for action in guide.get("actions", {}).values():
            example = action.get("example")
            if example:
                action_examples.append(example)
        for example in action_examples[:1]:
            lines.append(fenced_json(example))
        lines.append("")
    return lines


def build_markdown(guides: dict) -> str:
    lines = [
        "# FusionMCP AI Usage",
        "",
        "<!-- Generated from modules/tool_action_guides.json by scripts/generate_ai_usage.py -->",
        "",
        "This file defines the preferred usage pattern for AI clients working against the compact public FusionMCP API.",
        "",
        "## Public API First",
        "",
        "Prefer the compact public tools:",
        "",
    ]
    for tool in PUBLIC_TOOLS:
        lines.append(f"- `{tool}`")
    lines.extend([
        "",
        "Do not assume internal or specialist tools are available unless the server explicitly runs with `--api-profile full`.",
        "",
        "## Recommended Workflow",
        "",
    ])
    for index, item in enumerate(WORKFLOW, start=1):
        lines.append(f"{index}. {item}")
    lines.extend([
        "",
        "## Component Scope Rules",
        "",
    ])
    for rule in SCOPE_RULES:
        lines.append(f"- {rule}")
    lines.extend([
        "",
        "## Tool Selection Hints",
        "",
    ])
    for tool in PUBLIC_TOOLS:
        guide = guides.get(tool)
        if guide:
            lines.extend(render_tool_section(tool, guide))
    lines.extend([
        "## Error Interpretation",
        "",
    ])
    for item in ERRORS:
        lines.append(f"- {item}")
    lines.extend([""])
    lines.extend(render_example_section(guides))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    guides = load_guides()
    OUTPUT_PATH.write_text(build_markdown(guides), encoding="utf-8")


if __name__ == "__main__":
    main()
