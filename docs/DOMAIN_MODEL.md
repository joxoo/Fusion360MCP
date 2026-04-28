# FusionMCP Domain Model

## Purpose

This document defines the target domain model for `fusionmcp` so component-aware modeling operations behave predictably across root and nested Fusion 360 components.

The current codebase mixes:

- global lookup across the full design
- local feature creation on `activeComponent`
- direct `rootComponent` access for sketches and features

That combination causes unstable behavior when tools operate on components, especially around `body_not_found` and `sketch_not_found`.

## Core Concepts

### Design

The top-level Fusion document.

Responsibilities:

- owns the `rootComponent`
- exposes the current `activeComponent`
- is the global boundary for cross-component lookup

### Component

A modeling scope that owns:

- sketches
- bodies
- construction geometry
- features
- child occurrences

Rules:

- every created sketch belongs to exactly one component
- every created feature belongs to exactly one component
- every body has exactly one owner component

### Occurrence

An instantiated component inside another component.

Responsibilities:

- provides placement/path context inside the assembly tree
- connects parent and child component scopes

Rules:

- component names are not stable identifiers
- occurrence path is more reliable than plain component name

### Sketch

2D construction geometry owned by a component.

Attributes:

- `name`
- `owner_component`
- `construction_plane_or_face`
- `profiles`
- `curves`

Rules:

- a sketch is always created in the component that owns its reference geometry
- sketch lookup must return both the sketch and its owner component
- profile-based tools must distinguish between `sketch exists` and `sketch has no usable profile`

### Body

A B-Rep solid or surface body owned by a component.

Attributes:

- `name`
- `owner_component`
- `entity_token`
- `body_type`

Rules:

- body lookup must return both the body and its owner component
- feature operations on a body must run in the body owner context unless Fusion explicitly allows otherwise

### T-Spline Body

A form body with the same ownership expectations as a regular body, but different feature APIs.

Rules:

- form operations must resolve the owning component first
- form editing commands must not assume root ownership

### Feature

A modeling operation executed within one component context.

Examples:

- extrude
- revolve
- sweep
- loft
- hole
- pattern
- split
- combine

Rules:

- every feature has exactly one execution context component
- that context must be derived from the input entities, not guessed from `activeComponent`

## Domain Services

### Entity Resolver

Central service for finding model entities.

Required outputs:

- resolved object
- owner component
- occurrence path if available
- resolution status

Suggested responsibilities:

- resolve body by stable match strategy
- resolve sketch by stable match strategy
- resolve component by name/path/token
- resolve body or sketch owner component
- resolve compatible feature execution component

### Context Resolver

Determines where a new object or feature must be created.

Examples:

- sketch on plane -> target component is explicit root/active/selected component
- sketch on body face -> target component is the body owner component
- extrude sketch -> target component is the sketch owner component
- cut/join against body -> participant body must be in same compatible feature scope

### Error Mapper

Maps Fusion/API failures into explicit MCP errors.

This layer must avoid flattening unrelated failures into the same not-found response.

## Stable Invariants

These rules should hold after the refactor:

1. Entity lookup and feature execution are separate steps.
2. Lookup returns owner context, not only the raw Fusion object.
3. Feature builders never choose `root` or `activeComponent` implicitly when owner context is known.
4. Tools that create geometry on existing entities run in the owner component of those entities.
5. Not-found errors are only used when lookup actually fails.
6. Owner mismatch is reported as a context error, not as not-found.

## Scope Model

Every tool should operate with one explicit scope mode.

### Global Resolution Scope

Used for finding referenced entities anywhere in the design tree.

Examples:

- find sketch by name
- find body by name
- find component by path

### Execution Scope

Used for creating or modifying geometry.

Possible execution scopes:

- root component
- active component
- resolved owner component
- explicit component argument from the tool call

Default rule:

- if a tool references an existing sketch/body/face, execute in the resolved owner component
- if a tool creates standalone geometry without references, execute in the explicit target component or active component

## Tool Input Model

Current tool signatures often rely on implicit context. The target model should support optional explicit scoping.

Suggested common fields:

- `component_name`
- `component_path`
- `body_name`
- `sketch_name`
- `target_body`
- `face_index`

Guideline:

- only one of `component_name` or `component_path` should be needed
- `component_path` is preferred for unambiguous nested component targeting

## Error Taxonomy

The current implementation overuses generic not-found messages. The target domain should distinguish:

- `component_not_found`
- `body_not_found`
- `sketch_not_found`
- `profile_not_found`
- `face_not_found`
- `owner_context_not_resolved`
- `entity_owner_mismatch`
- `cross_component_operation_not_supported`
- `ambiguous_entity_name`
- `fusion_api_error`

Mapping guidance:

- use `*_not_found` only when lookup truly fails
- use `profile_not_found` when a sketch exists but has no valid profile
- use `entity_owner_mismatch` when lookup succeeds but execution scope is incompatible

## Canonical Resolution Result

All resolvers should conceptually return a structure like:

```text
ResolvedEntity
  kind: body | sketch | component | tspline_body
  name: string
  object: Fusion API object
  owner_component: Fusion component
  owner_component_name: string
  occurrence_path: string | null
  entity_token: string | null
```

This can be implemented either:

- in Python host logic, or
- inside shared Fusion script fragments

The important point is that builders consume a structured result instead of repeating ad-hoc lookup code.

## High-Risk Tool Families

These tool families should be migrated first because they are most sensitive to owner-context errors:

1. `create_sketch`
2. `extrude_sketch`
3. `create_sweep`
4. `create_loft`
5. `combine_bodies`
6. `split_body`
7. form tools in `forms_scripts.py`

## Migration Strategy

### Phase 1

Introduce shared resolution and context helpers without changing every tool at once.

### Phase 2

Refactor sketch and core geometry flows to consume resolved owner context.

### Phase 3

Refactor form, surface, mechanical, and analysis modules to the same model.

### Phase 4

Replace generic error flattening with explicit error taxonomy and integration tests.

## Definition of Done

The domain model is correctly implemented when:

- a sketch created on a body face is always created in the body owner component
- sketch-based features succeed on nested components without relying on root-only lookup
- owner mismatch produces a specific error instead of `body_not_found` or `sketch_not_found`
- tests cover root and nested component flows explicitly
