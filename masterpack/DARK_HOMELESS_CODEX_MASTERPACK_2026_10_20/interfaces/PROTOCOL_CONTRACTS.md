# EXECUTABLE INTERFACE CONTRACTS — PROPOSED SCHEMAS & TEST VECTORS

The schemas below are **new proposals** to be reconciled with actual PURL/SEURL/ACSP repository implementations. Their names are not asserted to be already deployed. Preserve backwards-compatible adapters when source repositories disagree; don't mutate unrelated repos. Every interface supplies `describe`, `validate`, `invoke`, `witness`, `replay`.

## Main model object

```
{
  "version": 1,
  "model_id": "grammar:world.walk.v1",
  "kind": "grammar_generator",
  "alphabet": {"symbols": ["S", "L", "R", "U"], "index": "retial"},
  "grammar": {"parser": "DFA", "constraints": ["must_follow_connected_edges"]},
  "ingrammar": {"model": "weighted-finite-state", "revision": "sha256:<real>"},
  "context": {"geo_chart": "overture@<revision>", "time": "<UTC>", "actor": "<id>"},
  "semantics": {"denotation": "typed-walk", "effects": ["read-world"]},
  "verification": {"validators": ["walkable", "source-provenance", "replay"]},
  "budgets": {"max_steps": 3000, "max_ms": 50}
}
```

## Runtime messages

```
{
  "protocol": "seurl.world.v1", "request_id": "<uuid>",
  "actor": "<authorized_actor>",
  "operation": "query|compile|simulate|propose|commit",
  "program": "purl://dark/journey/<id>/program",
  "context_hash": "<sha256>", "capability": "<scoped-id>",
  "clock": {"tick": 451234, "wall_utc": "<ISO8601>", "world_epoch": "<ISO8601>"},
  "payload": {}, "budget": {"fuel": 100000, "ms": 35}
}
```

Result:

```
{
 "request_id": "<uuid>", "status": "ok|refused|infeasible|unsupported|timeout|error",
 "data": {}, "trace_digest": "<sha256>", "commit_id": "<id-or-null>",
 "numerical": {"method": "<method>", "residual": 0.0, "tolerance": 0.0001},
 "effects": [], "source_versions": [], "warnings": []
}
```

## Actor decision

`{actor_id,world_tick,world_state_revision,available_actions[],constraints[],objective,selected_action,policy_id,utility_estimates,solver,seed,witness,refusal_reason?}`.

## Sky certificate

`{source_catalog,source_release,epoch,observer_coords,star_ids[],angular_edges[],pattern_signature,null_model,score,p_value?,quality_mask,known_template_compared_after_discovery?,display_projection_hash}`.

## Geographic certificate

`{source_graph_1,source_graph_2,chart_rev_1,chart_rev_2,route_nodes_1,route_nodes_2,feature_map,transform,score,calibration,confidence,content_hash,fictional_portal_effect?}`.

## Asset manifest

`{asset_id,source_url,source_revision,file_hash,asset_family,format,LOD,material_traits,triangles,texture_dim,rig_ref,animated?,geo_style,tile_id,stream_priority,import_test,frame_test,delivery_status}`.

## Transient environmental field

`{field:'wind|wetness|sound|sky-overlay',coords,epoch,source_kind:'observed|estimated|constructed',solver,mesh_resolution,seed,boundary_conditions,update_budget,values_ref,checksums,visual_material_effects}`.

## Shell-work request

`{shell_profile:'sandbox/ash',script_hash,script_path,working_directory:'/work/<job>',max_output_bytes,wall_time_ms,cpu_budget_ms,memory_budget_mb,allowed_commands[],input_bindings[],effect_policy:'propose-only',capability_ref}`. Response includes `exit_code`, `stdout_ref`, `stderr_ref`, `typed_effects_proposed[]`, `trace_digest`, `clock_snapshot`.

## Candidate test vectors

1. Two short street paths with bearings rotated by 100° share the same turn alphabet but differing absolute coordinates. This is *structural* match, not a real Earth match.
2. One vector field with zero source has zero vorticity under seeded smooth initial condition; a compact swirl input creates a bounded localized vorticity. Numerical residual bounded.
3. One star graph 3-node triangle remains congruent under 3D rigid rotation; measured RA/Dec timestamps differ under observer frame change as expected.
4. One user script proposes a fictional billboard text change, rejected without actor permission and admitted after explicit authorization; no process-level host effect.
5. One ACSP handoff sends twice under disconnect; exactly one durable append occurs.
6. One player walk produces legitimate witnessed `walk.program`, then billboard shows its actual normalized parse rather than random code.
7. One soundtrack prospective cue ignored by player triggers no escalating repetitive nudging; event still proceeds independently.
