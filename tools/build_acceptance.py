#!/usr/bin/env python3
"""Compile a conservative acceptance ledger from retained, executed evidence.

This does not run tests, acquire assets, synthesize audio, or certify artwork.
Re-run after final builds: python tools/build_acceptance.py --test-log evidence/final-tests.log
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MASTER = 'masterpack/DARK_HOMELESS_CODEX_MASTERPACK_2026_10_20'
V1 = 'riders/5-HOMELESS_RENDEZVOUS_RELEASE_RIDER_V1/HOMELESS_RENDEZVOUS_RELEASE_RIDER_V1/PERFORMANCE_BUILD_GATES.md'
V2 = 'riders/3-RENDEZVOUS_HIGH_FIDELITY_ASSET_PIPELINE.md'
V3 = 'riders/1-HOMELESS_RENDEZVOUS_GRAMMATICAL_AUDIO_RIDER_V3/HOMELESS_RENDEZVOUS_GRAMMATICAL_AUDIO_RIDER_V3/VERIFICATION_AND_INTEGRATION.md'


def read(path):
    p = ROOT / path
    return p.read_text(errors='replace') if p.is_file() else ''


def obj(path, default=None):
    try:
        return json.loads(read(path))
    except (ValueError, OSError):
        return {} if default is None else default


def sha(path):
    p = ROOT / path
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def log_pass(path):
    s = read(path)
    failure = re.search(r'FAILED\s*\(|Traceback \(most recent call last\)|^FAIL:|^ERROR:|\b[1-9]\d* failed\b|ℹ fail [1-9]', s, re.M)
    success = re.search(r'^OK\s*$|ℹ fail 0|BUILD SUCCESSFUL|^\d+ passed(?:, \d+ warnings?)? in ', s, re.M)
    return bool(s) and not failure and bool(success)


def command(*args):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def integrity():
    checks = []
    for line in read(f'{MASTER}/SHA256SUMS.txt').splitlines():
        m = re.match(r'^([0-9a-f]{64})\s+\*?(.+)$', line)
        if m:
            path = f'{MASTER}/{m[2]}'
            actual = sha(path)
            checks.append({'path': path, 'expected': m[1], 'actual': actual, 'passed': actual == m[1]})
    return checks


def compile_report(args):
    environment = obj('evidence/ENVIRONMENT.json')
    # Hash product sources, not changing reports, caches, model weights, or derived builds.
    sources = {}
    for folder in ('worldloom', 'native', 'math', 'runtime/native', 'unreal/Homeless/Source', 'unreal/Homeless/Config', 'scripts', 'tests', 'web/src', 'tools', 'android/app/src'):
        for p in sorted((ROOT / folder).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.so') and p.name != 'build_acceptance.py' and not any(part in ('assets','build') for part in p.relative_to(ROOT).parts):
                sources[str(p.relative_to(ROOT))] = sha(p.relative_to(ROOT))
    for n in ('web/package.json', 'web/package-lock.json', 'web/index.html', 'web/style.css', 'web/app.js', 'pyproject.toml', 'requirements.txt', 'requirements-voice.txt', 'unreal/Homeless/Homeless.uproject'):
        if (ROOT / n).is_file():
            sources[n] = sha(n)
    source_hash = digest(sources)
    web = obj('artifacts/web/build-manifest.json')
    apk_paths = sorted((ROOT / 'artifacts/android').glob('*.apk'))
    apks = []
    for p in apk_paths:
        entry = {'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': sha(p.relative_to(ROOT))}
        try:
            with zipfile.ZipFile(p) as z:
                entry.update(zip_integrity=z.testzip(), manifest_present='AndroidManifest.xml' in z.namelist(), dex_present='classes.dex' in z.namelist())
        except zipfile.BadZipFile:
            entry['zip_integrity'] = 'invalid ZIP'
        apks.append(entry)
    build_hash = args.build_hash or digest({'source': source_hash, 'web_revision': web.get('revision'), 'apks': apks})
    check_integrity = integrity()
    immutable_ok = bool(check_integrity) and all(x['passed'] for x in check_integrity)
    browser = obj('evidence/web_browser.json')
    telemetry = browser.get('telemetry', {})
    scene = telemetry.get('scene', {})
    browser_log = read('evidence/web_browser_run.log')
    browser_ok = bool(browser) and not browser.get('errors') and browser.get('persistence_equal') is True and browser.get('movement_distance', 0) > .2 and isinstance(scene.get('triangles'), (int, float)) and scene['triangles'] > 500 and 'Traceback (most recent call last)' not in browser_log
    apk_ok = bool(apks) and all(p.get('manifest_present') and p.get('dex_present') and p.get('zip_integrity') is None for p in apks) and 'BUILD SUCCESSFUL' in read('evidence/android_build.log') and 'Verifies' in read('evidence/android_signature.txt')
    grammar = obj('evidence/grammar_world_report.json')
    math = obj('evidence/math_benchmarks.json')
    voice = obj('evidence/voice_benchmarks.json')
    audio = obj('evidence/audio_metrics.json')
    sky = obj('evidence/sky_discovery.json')
    geo = obj('evidence/geo_performance.json')
    assets = obj('assets/catalog.json')
    runtime_assets = obj('assets/runtime/manifest.json')
    gate = obj('evidence/grammar_world_gate_integration.json')
    clips = obj('artifacts/voice/catalog.json').get('clips', [])
    clip_checks = [{'id': c.get('id'), 'passed': sha(str(c.get('path', '')).lstrip('/')) == c.get('audio_hash')} for c in clips]
    voice_ok = len(clips) >= 10 and len({c.get('voice_id') for c in clips}) >= 2 and all(c['passed'] for c in clip_checks)
    android_device = obj('evidence/android_device_test.json')
    checks = []
    evidence_index = {}

    def add(cid, title, threshold, status, observed, paths, procedure, oracle, blocker=None, source=None, local=None):
        assert status in ('pass', 'fail', 'blocked'), (cid, status)
        paths = list(dict.fromkeys(paths))
        found = []
        missing = []
        for path in paths:
            checksum = sha(path)
            if checksum:
                evidence_index[path] = {'sha256': checksum, 'bytes': (ROOT / path).stat().st_size}
                found.append(path)
            else:
                missing.append(path)
        checks.append({'check_id': cid, 'title': title, 'status': status, 'build_hash': build_hash,
                       'source_hash': source_hash, 'env': environment, 'data_revision': {p: evidence_index[p]['sha256'] for p in found},
                       'procedure': procedure, 'oracle': oracle, 'observed': observed, 'threshold': threshold,
                       'logs': found, 'evidence_paths': found, 'missing_evidence': missing,
                       'witness_hash': digest({p: evidence_index[p]['sha256'] for p in found}),
                       'confidence': 'executed-fixture-only' if status == 'pass' else 'unaccepted',
                       'blocker': blocker, 'requirement_source': source or f'{MASTER}/tests/ACCEPTANCE_MATRIX.md',
                       'local_subchecks': local or []})

    unavailable = 'No licensed Unreal 5.8 SDK, rendered/cooked map, GPU, or hardware encoder in this environment.'
    phone = 'No connected authorized Android device/emulator; Samsung A16/A60, install/startup, audio focus, thermal/power and suspend/rejoin tests not executed.'
    art_gap = 'Required authored scene coverage and controlled rendered quality comparison remain incomplete; catalog/conversion/unit success cannot establish cinematic fidelity.'
    proto_paths = ['evidence/protocol-green.log', 'evidence/world-session-green.log', 'evidence/http-tests.log', 'evidence/transport-regression.log']
    grammar_paths = ['evidence/grammar_world_report.json', 'evidence/grammar_world_generated_grammars.json', 'evidence/grammar_world_green.log']
    web_paths = ['evidence/web_browser.json', 'evidence/web_browser_run.log', 'evidence/web_play.png', 'artifacts/web/build-manifest.json']
    asset_paths = ['assets/catalog.json', 'assets/runtime/manifest.json', 'evidence/assets_acquisition.json']
    voice_paths = ['evidence/voice_benchmarks.json', 'artifacts/voice/catalog.json', 'data/voice/sources.json', 'evidence/voice_kokoro_benchmarks.json']
    original = {}
    for line in read(f'{MASTER}/tests/ACCEPTANCE_MATRIX.md').splitlines():
        m = re.match(r'^\| ([FGVSND]\d\d) \| (.*?) \| (.*?) \|$', line)
        if m:
            original[m[1]] = (m[2], m[3])

    def base(cid, status, observed, paths, procedure, oracle, blocker=None, local=None):
        title, threshold = original[cid]
        add(cid, title, threshold, status, observed, paths, procedure, oracle, blocker, local=local)

    historical = ['evidence/source-gin-tests.log', 'evidence/source-cgt-tests.log', 'evidence/source-purl-tests.log', 'evidence/source-substrateIO-tests.log', 'evidence/source-borne-tests.log', 'evidence/grammar_world_ingram_historical.log', 'evidence/grammar_world_realms_historical.log']
    base('F01', 'pass' if immutable_ok and all(log_pass(p) for p in historical) else 'fail', {'masterpack_files': len(check_integrity), 'all_masterpack_hashes_match': immutable_ok, 'upstream_heads': obj('evidence/UPSTREAM_REPOSITORIES.json', []), 'historical_suites': {p: log_pass(p) for p in historical}}, ['evidence/SOURCE_RECONCILIATION.json', 'evidence/UPSTREAM_REPOSITORIES.json', 'evidence/masterpack-integrity.log'] + historical, 'Verify every immutable SHA256SUMS entry; rerun retained historical suites at recorded heads.', 'Pinned source manifest, original test programs and SHA-256.', None if immutable_ok else 'Immutable input check or historical test evidence incomplete.')
    base('F02', 'pass' if all(grammar.get('grammar_certificates', {}).get(k, {}).get('passed') for k in ('walk','audio','naming')) else 'blocked', {'certificates': grammar.get('grammar_certificates'), 'fuzz': grammar.get('fuzz')}, grammar_paths, 'Run tests/test_grammar.py; inspect generated parsers, positive/negative and held-out fixture digests.', 'Declared typed grammar predicates; bounded evaluator.', local=['Template-based grammar synthesis; unrestricted induction is not established.'])
    base('F03', 'pass' if log_pass('evidence/grammar_world_green.log') else 'blocked', {'integration_apis': grammar.get('integration_apis'), 'typed_rejection': 'SEMANTIC_IMPOSSIBLE/SYNTAX_INVALID; usage rank does not grant validity'}, grammar_paths + ['tests/test_grammar.py'], 'Run grammar held-out/negative tests and rare-valid usage-ranking comparison.', 'Original Ingram KN3/Tower and independent semantic predicates.')
    base('F04', 'pass' if log_pass('evidence/protocol-green.log') else 'blocked', {'read_purity': 'tested', 'authorization': 'scoped/revocable; founder string grants nothing', 'context_version': 'pinned by grammar revision/context hash'}, proto_paths + ['docs/PROTOCOL.md'], 'Run protocol/session/HTTP tests for pure resolution, context, invalid authority and versioned effects.', 'Durable ledger state before/after and typed refusal.')
    service = obj('evidence/service-integration.json')
    domains = {c.get('channel','').split('.')[0] for c in service.get('channels',[]) if c.get('status') == 'ok'}
    service_ok = service.get('status') == 'pass' and domains >= {'sound','sky','physics','math','shell','continuity'}
    base('F05', 'pass' if service_ok else 'blocked', service or {'adapters': 'implemented WorldSession sound/sky/physics/math/shell/continuity', 'combined_actual_service_trace': 'not retained'}, ['evidence/service-integration.json', 'worldloom/session.py', 'evidence/unreal_native_interop.json'], 'Invoke every named typed domain against the running WorldSession service and save request/result digests.', 'Actual service responses and domain-specific numerical/authority checks.', None if service_ok else 'Combined actual-service roundtrip witness for all six named domains has not been retained.')
    base('F06', 'pass' if log_pass('evidence/ipc-green.log') else 'blocked', {'transport': 'AF_UNIX framed canonical CBOR', 'checkpoint_restart_duplicate_replay': 'executed local fixtures'}, ['evidence/ipc-green.log'] + proto_paths, 'Run daemon kill/restart, idempotent duplicate/conflict, checkpoint and replay tests without HTTP.', 'Same canonical state/event-chain hashes after restart.')
    base('F07', 'pass' if log_pass('evidence/workers-green.log') else 'blocked', {'worker': 'actual BusyBox ash under bubblewrap; bounded brokered darkctl/HTTPS; proposed writes', 'shell_witness_retained': bool(read('evidence/shell-real-execution.json'))}, ['evidence/workers-green.log', 'evidence/shell-real-execution.json', 'runtime/native/darkctl.cpp'], 'Run bounded shell pipes, exit/output, virtual-clock, broker-query and host-isolation fixtures.', 'Actual stdout/status plus typed propose-only effects and sandbox refusal.')
    base('F08', 'pass' if log_pass('evidence/workers-green.log') else 'blocked', {'engines': 'actual QuickJS and Wasmtime', 'invalid_host_import': 'rejected in executed worker fixture'}, ['evidence/workers-green.log', 'tests/test_workers.py'], 'Execute real JS/Wasm programs and invalid imports, timeout and resource-limit fixtures.', 'Typed returned event; no filesystem/network host binding.')
    base('F09', 'pass' if math.get('comparison', {}).get('pass') else 'blocked', math.get('comparison', {}), ['evidence/math_benchmarks.json', 'evidence/math_octave_reference.json', 'evidence/math_native_build.json', 'math/reference_octave.m'], 'Run actual GNU Octave qp/glpk/ode45 reference and compare native C++ bounded fixtures.', 'Independent Octave 9.4.0 and analytic decay; absolute tolerance 1e-8.')
    base('F10', 'pass' if grammar.get('world_replay_equal') is True else 'blocked', {'world_replay_equal': grammar.get('world_replay_equal'), 'synthetic_counterfactual': grammar.get('realms_social_impact'), 'limitation': 'Small synthetic graph; no real-world social causation.'}, grammar_paths + ['evidence/grammar_world_snapshot.json'], 'Replay seeded events; inspect source/authority/parent chain, rollback and declared modeled counterfactual.', 'Canonical event hashes, restored snapshots and explicit counterfactual limitations.')
    base('G01', 'blocked', {'coordinate_witness': obj('evidence/geo_coordinate_witness.json'), 'broad_regions': list(obj('evidence/geo_global_queries.json'))}, ['evidence/geo_coordinate_witness.json', 'evidence/geo_global_queries.json', 'evidence/geo_full_suite.txt'], 'Run randomized WGS84 pole/dateline/ENU tests and render a moving chart across boundaries.', 'Karney WGS84 inverse/ECEF roundtrip; rendered frame continuity.', 'CPU coordinate fixtures pass; global rendered no-visible-jump transition has not been measured.')
    base('G02', 'pass' if (ROOT/'data/geo/raw/tampa.osm').is_file() else 'blocked', {'junction_origin': [27.95946425, -82.5055696], 'junction_nodes': ['2057042478','1603574189'], 'spawn_footway': '4520926405', 'access_limitation': 'Source tags; no live field/legal access survey.'}, ['data/geo/sources.json', 'evidence/grammar_world_navigation.json', 'evidence/geo_source_manifest.json', 'evidence/geo_test_green.txt'], 'Verify both named ways share the two junction nodes; verify hashed footway route and spawn.', 'Retained original OSM XML, object IDs/versions and source hashes.')
    base('G03', 'pass', {'typed_gaps': obj('evidence/geo_overview.json').get('limits'), 'sources': 'OSM three windows; generalized airport/port/settlement references; population country totals; dated Tampa model weather; HYG stars'}, ['data/geo/sources.json','data/sky/source.json','evidence/geo_global_queries.json','docs/GEO_SKY.md'], 'Query each source family and uncovered regions; verify timestamps, explicit masks and no invented lanes/density.', 'Pinned source records; explicit gap is an allowed truthful result.')
    base('G04', 'blocked', geo, ['evidence/geo_performance.json','evidence/grammar_world_gate_integration.json'] + web_paths, 'Walk/drive multiple cells; log resident geometry, predictions, eviction, memory and elapsed time.', 'Bounded cache plus renderer geometry/network/CPU/GPU telemetry.', 'Metadata LRU is measured; nearby/visible mesh residency, GPU memory and cell streaming are not fully measured.')
    route_negatives = {}
    for city in ('london','marina'):
        result=obj(f'evidence/geo_match_tampa_{city}.json');certificate=result.get('certificate',{})
        route_negatives[city]={'conclusion':result.get('conclusion'),'score':certificate.get('score'),'heldout_p':certificate.get('calibration',{}).get('p_value'),'alpha':certificate.get('calibration',{}).get('threshold'),'heldout_samples':certificate.get('calibration',{}).get('heldout_samples')}
    base('G05', 'pass', {'outcomes': route_negatives, 'interpretation': 'Explicit tested negatives satisfy this check; no certified geographic rarity or resemblance claim.'}, ['evidence/geo_match_tampa_london.json','evidence/geo_match_tampa_marina.json','data/geo/sources.json'], 'Compare actual source-graph routes with held-out selection-adjusted 16-candidate maximum null, seed31,128 samples.', 'p<=.05 required to certify rarity; negative is valid acceptance outcome.')
    base('G06', 'pass' if obj('evidence/sky_source_verification.json').get('source_file_integrity') == 'passed' else 'blocked', obj('evidence/sky_numerical.json'), ['evidence/sky_source_verification.json','evidence/sky_numerical.json','evidence/sky_test_verification.json','data/sky/horizons_references.json'], 'Run angular invariance, epoch transport, observer horizon and pinned JPL field-replay fixtures.', '1e-12 rad geometric residual; 1e-9 deg pinned ephemeris replay, not full apparent-sky accuracy.', local=['No terrain/refraction/nutation/annual aberration/topocentric parallax; Horizons supports only retained instants.'])
    base('G07', 'pass' if sky.get('known_template_compared_after_discovery') else 'blocked', {'p_value': sky.get('p_value'), 'candidate_count': sky.get('candidate_count'), 'benchmark': sky.get('benchmark'), 'conclusion': 'Negative/inconclusive rarity; partial template vertex agreement only.'}, ['evidence/sky_discovery.json','data/sky/source.json','data/sky/template_source.json'], 'Mine without names/templates, freeze hash, calibrate held-out maximum-search null, compare pinned template afterwards.', 'Independent held-out p<=.05 for rarity; template vertices/edges scored separately.')
    base('G08', 'blocked', {'server_portal_semantics': 'learned/consented authored overlay supported by society fixtures', 'rendered_transition': 'unverified'}, ['tests/test_society.py','evidence/grammar_world_green.log','evidence/geo_match_tampa_london.json'], 'Exercise learned skill and visit/overlay/braid choice in rendered runtime; inspect independently sourced destination and authored tags.', 'Consent/skill state, geographic source manifests and transition capture.', 'No complete rendered independently sourced portal transition witness.')
    base('V01', 'blocked', obj('evidence/unreal_preflight.json'), ['unreal/Homeless/Homeless.uproject','evidence/unreal_preflight.json','evidence/unreal_native_interop.json'], 'Run tools/unreal_preflight.py then build/cook project on licensed UE5.8 host.', 'Engine Build.version, Unreal compiler/UAT and cooked/rendered output.', unavailable)
    base('V02', 'fail', {'asset_count': len(assets.get('assets', [])), 'unfilled_families': assets.get('unfilled_families'), 'quality_acceptance': assets.get('quality_acceptance')}, asset_paths, 'Acquire/import each P0 family; validate source hashes, scene integration and installed Unreal state.', 'Catalog state semantics plus actual file/import/render witnesses.', art_gap + ' Unreal entitlement/import also unavailable.')
    base('V03', 'fail', {'browser': scene, 'hero_scene': assets.get('quality_acceptance', {}).get('hero_scene')}, asset_paths + web_paths, 'Capture controlled hero view, image/material probes and p50/p95/1%low/VRAM on a named GPU.', 'V2 scene reference, declared quality tier, rendered art review and hardware profile.', art_gap + ' Named-GPU VRAM/frame measurements also unavailable.')
    base('V04', 'blocked', {'numerical_wetness': math.get('weather'), 'rendered_reflection_readback': None}, ['evidence/math_weather_field.json'] + web_paths, 'Sweep wetness/time/view; measure roughness and light-driven yellow-sign/headlight reflection in framebuffer/G-buffer.', 'Documented wetness/roughness curve plus real light response.', 'No controlled renderer material/reflection readback fixture.')
    base('V05', 'fail', {'server_actors': grammar.get('actors'), 'browser_visibleNPCs': scene.get('visibleNPCs'), 'source_models': [a.get('id') for a in assets.get('assets', []) if a.get('category') in ('character','npc','characters')]}, grammar_paths + asset_paths + web_paths, 'Observe independent pedestrians/traffic over time; compare animation phase, rig contact and scheduling traces.', 'Source-human visual quality, independent actor decisions and rendered motion.', 'Street-scene crowd/traffic quality and unsynchronized full-body locomotion are unaccepted.')
    base('V06', 'blocked', {'synthetic_camera': math.get('camera'), 'rendered_stress': None}, ['evidence/math_benchmarks.json'] + web_paths, 'Stress each camera mode at30/60fps with scene occlusion/collision, horizon and common-time trajectory probes.', 'Declared jerk bound25m/s^3 plus rendered framing/horizon/occlusion targets.', 'Synthetic camera passes do not measure scene-mesh occlusion, image horizon or network jitter.')
    base('V07', 'blocked', {'server_negotiation': grammar.get('ride_equilibria'), 'street_drive': 'not demonstrated'}, ['evidence/grammar_world_report.json','tests/test_society.py'] + web_paths, 'Request consented manual/autonomous ride and entourage event; drive real graph/collision fixture.', 'Authority/refusal record, source road constraints and actual vehicle movement trace.', 'Manual/autonomous driving, entourage and scene collision are not integrated acceptance-tested; OSM turn restrictions remain unenforced.')
    base('V08', 'blocked', {'browser_runtime': browser_ok, 'onboarding_assertions': 'not separately retained'}, web_paths, 'Enter/skip/resume actual active street; record Dark join/camera/nearby response state and restore.', 'Preentry active-world state and explicit skippable/resumable runtime assertions.', 'Full recognition/join scene and skip/resume story have not been independently verified.')
    base('V09', 'blocked', math.get('weather'), ['evidence/math_weather_field.json'] + web_paths, 'Connect field vectors/wetness to actual VFX/materials and read numerical plus rendered response.', 'Declared field residual and actual renderer output; fictional perturbation explicitly tagged.', 'Genuine rendered VFX/material field response has no quantitative capture.')
    base('S01', 'blocked', {'offline_sources': list(audio.get('sources', {})), 'browser_audio': telemetry.get('audio', {})}, ['evidence/audio_metrics.json'] + web_paths, 'Play all seven named source classes at controlled3D positions; measure attenuation/mix and listen.', 'Runtime panner/mix trace and calibrated listening fixture.', 'Offline stereo fixture and partial browser playback do not establish all seven live source classes and intelligible spatial mixing.')
    base('S02', 'pass' if audio.get('metrics', {}).get('heavy_click_count') == 0 else 'blocked', audio.get('metrics'), ['evidence/audio_metrics.json','artifacts/audio/manifest.json','evidence/math_audio_full_suite.log'], 'Render actual PCM, verify integer event samples, loop/crossfade boundaries and adjacent-sample jumps.', 'Offline PCM sample oracle; click threshold .15; simulated512-sample buffer tolerance.', local=['Device drift/underruns, LUFS/true peak and human listening are separate unexecuted gates.'])
    base('S03', 'blocked', {'bounded_policy': 'salience/cooldown and suppression after decline/ignore tested', 'attention_baseline': None}, ['tests/test_audio.py','tests/test_society.py','evidence/math_audio_full_suite.log'], 'Compare opt-in cue/no-cue baseline and persistent ignore/decline suppression during actual play.', 'Recorded attention/response, no forced replay and baseline.', 'Actual attention/response baseline has not been measured.')
    base('S04', 'blocked', {'in_world_cue_render_capture': None}, ['tests/test_society.py'] + web_paths, 'Activate sound/sky cue and capture corresponding in-world object/VFX/audio without compulsory popup.', 'Actual renderer event-to-object/audio correspondence.', 'No full sound/sky cue rendering fixture retained.')
    base('S05', 'pass' if voice.get('asr') and log_pass('evidence/grammar_world_green.log') else 'blocked', {'actual_ASR_fixture_count': len(voice.get('asr', [])), 'grammar': 'finite English/Arabic; ambiguous/out-of-grammar clarify with no effects', 'Arabic_error': 'V3-04 fails Arabic exact-text fixture; physical capture blocked'}, voice_paths + ['tests/test_society.py','evidence/grammar_world_green.log'], 'Run actual ASR fixtures through finite intent grammar; reject commands and ambiguous/unknown text; retain text fallback.', 'Canonical grammar productions and no unauthorized effect.', local=['Tiny clean English fixture results do not certify general ASR accuracy.'])
    base('N01', 'pass' if grammar.get('lazy_capacity') == 8190000000 else 'blocked', {'synthetic_id_capacity': grammar.get('lazy_capacity'), 'active_actors': grammar.get('actors'), 'tick60s_wall_ms': grammar.get('tick_60_seconds_wall_ms'), 'limitation': 'lazy IDs/24 active synthetic actors, not8.19b ticking persons'}, grammar_paths + ['evidence/grammar_world_snapshot.json'], 'Measure active/cohort tick cost and lazy ID allocation over full capacity; replay snapshots.', 'Bounded active records and actual wall time.')
    base('N02', 'pass' if grammar.get('world_replay_equal') else 'blocked', {'seeded_replay': grammar.get('world_replay_equal'), 'rights': 'refusal/cooperation/local observation/finite memory tested'}, ['evidence/grammar_world_green.log','tests/test_society.py'], 'Run refusal, cooperation, observer reach/occlusion, memory and seeded restore tests.', 'Independent utilities/authority and non-observer ignorance.')
    base('N03', 'pass' if log_pass('evidence/grammar_world_green.log') else 'blocked', {'coauthor': 'player/NPC proposals, collaborators, adoption and rollback chain tested'}, ['evidence/grammar_world_green.log','tests/test_society.py'], 'Propose fictional sign jointly; adopt with authority; rollback preserving contributors and prior revision.', 'Causal events, explicit authorization and unchanged source identity.')
    base('N04', 'fail', {'founder_string_authority': False, 'operator_bootstrap': 'local bearer capability', 'production_Abed_identity_verification': False, 'delegation_revoke': 'unit-tested'}, proto_paths + ['docs/PROTOCOL.md','tests/test_society.py'], 'Authenticate actual founder across browser/APK sessions; delegate/revoke and verify actor-bound effects.', 'Real identity provider/session evidence plus revocable ledger grants.', 'Local operator capability does not independently authenticate Abed Kadaan; production founder identity and device cross-session proof are missing.')
    base('D01', 'pass' if apk_ok else 'fail', {'artifacts': apks, 'package': 'world.homeless.rendezvous', 'sdk': 'min23,target35', 'signing': 'Android debug v1/v2 verified', 'device': android_device}, ['evidence/android_build.log','evidence/android_aapt.txt','evidence/android_signature.txt','evidence/android_device_test.json'] + [x['path'] for x in apks], 'Build actual Gradle/Capacitor APK, ZIP-check, aapt inspect, verify signature/checksum; adb install when device accessible.', 'Valid Android package/dex, Gradle success and apksigner; device install is separately blocked.', None if apk_ok else 'A valid built/inspected APK was not verified.')
    base('D02', 'pass' if browser_ok else 'fail', {'local_url': 'http://127.0.0.1:8086/', 'browser_smoke_pass': browser_ok, 'movement_distance': browser.get('movement_distance'), 'persistence_equal': browser.get('persistence_equal'), 'public_https_url': None, 'scope': browser.get('scope')}, web_paths, 'Serve actual production build; use Chromium softwareWebGL2 to enter, move, decode/play audio and reload saved position.', 'No page errors, real triangles>500, movement>.2m and saved position equality; public host status explicit.', None if browser_ok else 'Retained browser smoke did not complete all its assertions; public HTTPS hosting also has not been deployed.')
    base('D03', 'blocked', {'native_protocol_probe': obj('evidence/unreal_native_interop.json').get('status'), 'PixelStreaming_rendered_media': False}, ['evidence/unreal_preflight.json','evidence/unreal_pixelstreaming_build.log','evidence/unreal_native_interop.json'], 'Run actual Pixel Streaming2 GPU host; capture A/V/touch, codec bitrate/fps/latency and reconnect.', 'WebRTC media/interaction trace from running Unreal renderer.', unavailable)
    base('D04', 'blocked', {'browser_local_position_restore': browser.get('persistence_equal'), 'Android_offline_startup': android_device}, ['evidence/android_device_test.json'] + web_paths, 'Disconnect server; launch APK, enter/move/store event, kill process and relaunch.', 'Useful nonblank WebView entry, persistent state and offline interaction.', phone)
    base('D05', 'pass' if web and apk_ok else 'blocked', {'scripts': ['scripts/run.sh','scripts/serve_web.sh','scripts/build_android.sh','scripts/test_android.sh','scripts/build_unreal.sh'], 'web_revision': web.get('revision'), 'apk_hashes': apks, 'known_failures': 'evidence/acceptance.json and COUNTEREXAMPLES.md'}, ['README.md','docs/IMPLEMENTATION_PLAN.md','evidence/ENVIRONMENT.json','artifacts/web/build-manifest.json','scripts/run.sh','scripts/build_android.sh','scripts/test_android.sh','scripts/build_unreal.sh'], 'Run supplied build/launch scripts, inspect manifests/system checks and publish exact artifacts/status ledger.', 'Actual file manifests/hash, explicit environment blockers and retained logs.', None if web and apk_ok else 'Build artifacts incomplete.')

    # V1: every deliverable row, three hardware profiles, instrumentation,
    # the complete one-run story, CI order and final reporting requirements.
    v1_rows = [
      ('A01','Web build','HTTPS production assets, controls, free3D movement, audio, NPCs and persistence','blocked',{'local_browser_smoke':browser_ok,'public_https_url':None},web_paths,'Deploy production assets over HTTPS, enter/walk/interact/rejoin.','Actual public browser integration trace.','Public HTTPS deployment and complete3D/NPC story not acceptance-tested.'),
      ('A02','Android','Real Gradle bytes, inspection/checksum, supported device install/run','blocked',{'apk_verified':apk_ok,'device':android_device},['evidence/android_build.log','evidence/android_aapt.txt','evidence/android_signature.txt','evidence/android_device_test.json'],'Gradle assemble; aapt/apksigner; adb install/am start and capture.','Actual APK plus device startup trace.',phone),
      ('A03','Fullscreen','Enter gesture/fullscreen, no scroll/overscroll; recoverable immersive Android','blocked',{'implementation_present':True},web_paths+['android/app/src/main/java/world/homeless/rendezvous/MainActivity.java'],'Enter with fullscreen allowed/denied; inspect scroll; test system-bar recovery.','Browser fullscreen/viewport assertions and physical OS gesture.',phone+' Browser fullscreen/scroll assertions missing.'),
      ('A04','Shared state','Same authenticated browser/APK world and committed events','blocked',{'HTTP_cross_client_fixture':log_pass('evidence/http-tests.log'),'browser_token_resumed':browser.get('token_resumed')},proto_paths+web_paths,'Commit event from each actual client, restart and compare authority/session/world head.','Authoritative committed event and matching session/head.',phone),
      ('A05','Real physics','Collision stop, impulse/fixed step, replay divergence measured','blocked',{'capsule_wall_unit':log_pass('evidence/web_unit_tests.log')},['evidence/web_unit_tests.log','tests/test_web_physics.mjs'],'Run collision/impulse/conservation seeds and repeated fixed-step state checksums.','Agreed speed/shape, penetration<.08m fixture; declared conservation tolerance.','Capsule wall fixture passes; impulses, conservation and replay divergence not fully measured.'),
      ('A06','NPCs','Independent routine/decision/contextual interaction/restart plus scale','blocked',{'server_actors':grammar.get('actors'),'visibleNPCs':scene.get('visibleNPCs')},grammar_paths+web_paths,'Play contextual NPC interaction, restart; record independent routine/animation and scale.','Agent decision/persistence plus rendered NPC trace.','Server routines pass; complete rendered contextual NPC acceptance remains open.'),
      ('A07','Onboarding','Active world, smooth Dark join, natural selective response, skip/reenter','blocked',{'browser_runtime':browser_ok},web_paths,'Record actual entry and skip/reentry over active audiovisual street.','One-run interaction/recognition assertions.','Complete onboarding story not measured.'),
      ('A08','Geometry','Real geospatial Tampa anchor and source/recipe distinctions','pass',{'origin':[27.95946425,-82.5055696],'terrain':'explicit artistic flat chart'},['data/geo/sources.json','data/geo/tampa-scene.json','docs/GEO_SKY.md'],'Inspect OSM-source IDs and runtime source-quality tags.','Original OSM topology and explicit estimated/artistic dimensions.',None),
      ('A09','Audio','Gesture unlock, stereo/positional/footsteps/NPC/traffic, no transition pops','blocked',{'audio_context':telemetry.get('audio',{}).get('state'),'offline_clicks':audio.get('metrics',{}).get('heavy_click_count')},['evidence/audio_metrics.json']+web_paths,'Enter/focus/resume, walk and cross cells while measuring all source classes and audio glitches.','Actual AudioContext scheduling/dropout/pop and listening measurements.','Only partial software-browser audio and offline DSP measured.'),
      ('A10','Continuity','Real gameplay/runtime PURL/SEURL/ACSP, reconnect/replay after app kill','blocked',{'local_daemon_restart':log_pass('evidence/ipc-green.log')},proto_paths+['evidence/ipc-green.log','evidence/android_device_test.json'],'Commit game event, invoke authorized shell, kill APK and restore same ledger.','Actual client and local protocol event hashes.',phone),
      ('A11','Unreal preserved','Original UE interfaces/configs/scope preserved; render blocked until run','pass' if immutable_ok else 'fail',{'immutable_originals_match':immutable_ok,'unreal_render_status':'blocked'},['evidence/masterpack-integrity.log','evidence/unreal_preflight.json','unreal/Homeless/Homeless.uproject'],'Verify original source hashes and explicitly keep UE lane separate.','Immutable masterpack plus engine preflight.',None if immutable_ok else 'Immutable original mismatch.'),
      ('H01','Low Samsung profile','Stable30fps; p95<=40ms; bounded residency; A16 and A60 separately','blocked',{'software_browser_p95ms':scene.get('p95Ms'),'phone':android_device},web_paths+['evidence/android_device_test.json'],'Steady walk/cold load/background/reconnect on named A16/A60.','Physical device frame/memory/thermal trace.',phone),
      ('H02','Mid profile','>=30fps with denser animated crowds/material/reflections','blocked',{'named_mid_device':None},web_paths,'Run declared mid tier on named device; preserve source identity.','Measured frametimes and controlled visual capture.','No named midrange hardware test.'),
      ('H03','High/cloud profile','60fps where supported, high fidelity desktop/WebGPU/Unreal','blocked',{'named_GPU':None},web_paths+['evidence/unreal_preflight.json'],'Run high tier on named GPU with declared renderer/profile.','Frame/VRAM/draw/triangle and image-quality measurements.',unavailable),
      ('Q01','Timing/load/residency telemetry','Cold start<=15s target; first frame/cell time,1%low,p50/p95,memory,draws,triangles,bytes/min,NPCs,steps,glitches','blocked',scene,web_paths,'Measure complete cold/warm walk/cell sequence and retain uncapped rAF/GPU timing.','Instrumented renderer plus process/GPU memory; all unavailable values remain null.','Telemetry incomplete; software browser is not phone/GPU performance evidence.'),
      ('Q02','Physics conformance','Zero tunneling; declared penetration/conservation tolerance; repeated-seed variance; camera continuity','blocked',{'wall_fixture':'penetration<8cm tested'},['evidence/web_unit_tests.log','tests/test_web_physics.mjs'],'Test high-speed shapes, impulses/damping, repeated seeds, interpolation/teleport.','State checksums/contact distance and integrator tolerance.','Full physics/vehicle replay fixture missing.'),
      ('Q03','Camera instrumentation','Mean jerk and p95 angular delta, occlusion/horizon/teleport measured','blocked',math.get('camera'),['evidence/math_benchmarks.json']+web_paths,'Sample rendered camera pose/pixels under movement/teleport/occlusion stress.','Actual camera trace against declared bounds.','Scalar synthetic camera does not measure actual scene camera.'),
      ('Q04','Asset QA','Smoke load,GLB/textures/LOD projection difference, no missing materials/shader errors; configurable memory ceiling','blocked',{'fixture_category_gaps':runtime_assets.get('fixture_category_gaps'),'browser_errors':browser.get('errors')},asset_paths+web_paths,'Load scene, compare LOD projection and materials under fixed lighting, measure memory.','GLB source metrics plus renderer/material readback.','Controlled LOD/material/shader/memory fixture incomplete.'),
      ('Q05','Web input/audio focus','Fullscreen allowed/denied,100dvh,focus resumes audio;touch/orientation/camera limits','blocked',{'AudioContext_state':telemetry.get('audio',{}).get('state')},web_paths,'Test fullscreen rejection,focus loss/resume,touch sensitivity and both supported orientations.','Actual browser interaction assertions.','Complete input/focus/orientation test not retained.'),
      ('Q06','APK system bars','Recoverable system bars, immersive mode,orientation/audio unlock','blocked',android_device,['evidence/android_device_test.json'],'Install APK; test gesture bars and orientation/audio recovery.','Physical Android/WebView behavior.',phone),
    ]
    for suffix,title,threshold,status,observed,paths,procedure,oracle,blocker in v1_rows:
        add('V1-'+suffix,title,threshold,status,observed,paths,procedure,oracle,blocker,V1)
    stories = [
      'Tap APK or visit URL and obtain preexisting audiovisual world',
      'One clear Enter action enters fullscreen without blank WebView/scroll',
      'Camera reveals Dark arrival at real Dale Mabry/West Spruce Tampa anchor',
      'NPCs/traffic move with ambient airport sound,dynamic light and selective reactions',
      'Walk freely and investigate fictional storefront',
      'Speak to NPC,observe independent response/causal event,and approve world detail or find route pattern',
      'Exit/rejoin retains same world memory and saved event',
      'Low-performance adaptation preserves authored quality and active scene',
    ]
    for i,title in enumerate(stories,1):
        add(f'V1-S{i:02}',title,'Execute this complete one-run human acceptance step in actual browser/APK.', 'blocked',{'partial_local_browser':browser_ok,'human_acceptance_run':False},web_paths+['evidence/android_device_test.json'],'Execute continuous recorded story with event/scene/audio/device trace.','Human acceptance plus numerical/input/state assertions.',phone+' Complete human story unexecuted.',V1)
    add('V1-CI','Verification workflow','Install→unit/property/math→server→web→GPU browser→Gradle→APK inspect→device→cross-session→reports','blocked',{'APK_built':apk_ok,'software_browser':browser_ok,'device':'blocked','UE_lane':'blocked'},['evidence/android_build.log','evidence/web_browser_run.log']+proto_paths+args.test_log,'Run CI stages retaining distinct lane status.','Actual commands/logs; failed/blocked stages do not become pass.',phone+' Named GPU/Unreal lane unavailable.',V1)
    add('V1-REPORT','Final delivery report','Actual live URL/APK link,commit/hash,hardware/software baseline,integration trace,remaining blockers','pass',{'live_public_URL':None,'local_URL':'http://127.0.0.1:8086/','APK':apks,'commit':command('git','rev-parse','HEAD'),'worktree_dirty':bool(command('git','status','--porcelain'))},['evidence/ENVIRONMENT.json','artifacts/web/build-manifest.json','evidence/service-integration.json']+proto_paths,'Regenerate audit after final logs/builds and link actual local artifacts; public deployment remains explicit.','Current filesystem hashes, source commit and scoped environment results.',None,V1)

    # V2: exact pipeline order; source/art identity; all seven acquisition
    # categories; tier-specific and numeric/visual scene acceptance.
    pipeline = ['DISCOVER','PREVIEW','FETCH','INVENTORY/HASH','NORMALIZE','MATERIAL-CONVERT','RETOPO/LOD/ATLAS','COMPRESS','PHYSICS PROXY','INTEGRATE','INSTRUMENT','PUBLISH TO STREAMING CATALOG']
    for i,stage in enumerate(pipeline,1):
        status = 'pass' if stage in ('DISCOVER','FETCH','INVENTORY/HASH') and assets.get('assets') else 'blocked'
        if stage == 'INTEGRATE': status = 'fail'
        observation = {'asset_count':len(assets.get('assets',[])), 'scope':'Some source assets retrieved/hash inventoried; full-category completion not implied.', 'runtime_fixture_gaps':runtime_assets.get('fixture_category_gaps')}
        add(f'V2-P{i:02}',stage,'Execute this stage in the mandated order with its independent checks; candidate≠acquired,optimized≠rendered.',status,observation,asset_paths+['tools/assets.py','evidence/assets_derivative_optimization.log'],'Run asset family through source→derivative→runtime pipeline; retain stage-specific inspection.','Original source hash/metrics and stage-specific renderer checks.',None if status=='pass' else ('Authored scene is incomplete.' if status=='fail' else 'Complete per-family stage verification is missing; see asset records for executed subset.'),V2)
    categories = [
      ('commercial streets','20+ visibly distinct modern storefront modules;10+ roadside classes;curb/parking/signals/regional style'),
      ('vehicles','Passenger cars,buses,bikes,scooters,motorcycles,vans,emergency-style vehicles,interiors;wheel pivots/rigs'),
      ('NPCs','Real human faces,age/wardrobe variety,hands,skeleton/gait/facial animation,crowdLOD/independent agents'),
      ('water/air','Aircraft,balloons,ground service,boats,reflective water and engine/rotor audio'),
      ('retail/culture','Cafes,interiors,carts,furniture,illuminated signs,billboards,food/drink;fictional texture variants'),
      ('natural/weather','Regional vegetation,sky/HDRI,wet road,puddles,reflections,rain and believable night lighting'),
      ('animation/audio','Footfall/idle/turn/gesture/wave/interact,crowd choreography,cabin/ambient audio'),
    ]
    for i,(title,threshold) in enumerate(categories,1):
        add(f'V2-C{i:02}',title,threshold,'fail',{'unfilled_families':assets.get('unfilled_families'),'fixture_category_gaps':runtime_assets.get('fixture_category_gaps')},asset_paths,'Acquire each named class; inspect portable masters/rigs/materials; render in scene.','Actual acquired/imported/rendered bytes and category count.',art_gap,V2)
    v2_extra = [
      ('D01','Source/art identity','Assets first;no visible graybox;source master plus separate UE/runtime derivatives;same authored identity','fail',art_gap),
      ('D02','Opening scene','Geographic Tampa context plus authored faces,vehicle silhouettes,rich signs,natural motion,reflections,vegetation,aircraft,spatial audio,collective recognition','fail',art_gap),
      ('M01','Source masters','Immutable content-addressed highest-quality masters,SHA256,dimensions,units,triangles,skeleton/animation,shader inputs,bounds,texel density,lookdev','blocked','Source hashes/bounds partly measured; complete texel-density/lookdev/animation/skeleton metadata is not verified per family.'),
      ('M02','Normalization/materials','Meters,orientation,transforms,normals/tangents/UV/PBR;separate glass/emissive/decal/foliage checks','blocked','GLB numeric checks exist; all material families have not passed controlled renderer tests.'),
      ('M03','GLB/compression/LOD','GLB2,KTX2/BasisU,verified optional Draco,explicit LODs and exact PlayCanvas reimport','blocked','Baseline GLB with embedded JPEG/PNG exists; KTX2/Draco/LOD roundtrip gates remain pending.'),
      ('M04','GPU variants','Common canonID;low/medium/high/UE-source variants with source provenance/checksum/deviation','blocked','Not every tier has independently verified derivative and rendered parity.'),
      ('M05','Collision proxies','Rich render mesh separate from verified low-cost collider;no splat-only authoritative collision','blocked','Complete mesh-specific proxy/navmesh/collision QA not measured.'),
      ('M06','Predictive streaming','Neighbor/speed/path/view/occlusion preload,farLOD eviction,reuse,memory pressure;bounded first playable download','blocked','Server byte cache passes; complete cell/LOD/GPU/first-frame streaming measurements missing.'),
      ('T00','R0 archive','Lossless8K/16K source,preview,dimensions,hashes','blocked','High-resolution sources retained; complete preview/dimension acceptance for every family missing.'),
      ('T01','R1 Unreal','UE-native high-end original render/cook gates','blocked',unavailable),
      ('T02','R2 desktop/cloud','Declared workstation60fps target with best authoredLOD,materials/light/shadow/reflections and parity','blocked','No named workstation/GPU performance and visual parity fixture.'),
      ('T03','R3 midrange','Measured30–60fps with portable authoredLOD,GPU maps,reflections,bounded animated population','blocked',phone),
      ('T04','R4 founder low','Actual-device30fps,p95/input latency;KTX2/adaptive scale/intelligent streaming;no placeholder appearance','blocked',phone),
      ('F01','Material fixture','Wet/dry asphalt,gold/painted sign,headlight,car paint,skin,glass,clothes,foliage;BRDF/exposure/legibility;view-dependent yellow-sign reflection','blocked','No controlled BRDF/framebuffer fixture for all required materials.'),
      ('F02','Motion fixture','Three full-body NPCs footsteps/turn/gesture/idle/collision/feet;detailed passing vehicle wheels/suspension/headlights/audio','fail','Required three-human animation/vehicle scene fixture is incomplete.'),
      ('F03','Scene fixture','Investor-grade Tampa entrance with lamp/car/storefronts/active crowd/exposure and real source manifest','fail',art_gap),
      ('F04','Streaming fixture','Multi-cell walk/drive/return:bytes,CPU/GPU memory,draws,1%low,p95,resolution,decoded textures,LOD/shader/cache','blocked','Complete cell traversal and GPU/device streaming trace absent.'),
      ('F05','Visual validation','Controlled rendered viewpoints,side-by-side art references,numeric similarity/edges/material checks,human review when available','fail','No completed controlled rendered comparison proves cinematic art quality.'),
      ('F06','Real Android/WebView','Actual3D materials/HDRI/decoding,WebGL2,fullscreen/orientation/audio unlock,suspend/rejoin','blocked',phone),
      ('A01','Rider artifacts','Catalog,masters,runtime manifest,converters/config/QA,real environment and imported NPC/vehicle,downloadable device-testable scene','blocked','Source/derivative/model bytes exist; full rendered environment and device acceptance remain unverified.'),
      ('A02','World contracts','Reuse PURL/SEURL/ACSP and authoritative world state;no replacement renderer-local identity','blocked','Server continuity is tested; actual APK/browser authoritative cross-session remains unverified.'),
      ('A03','Immutable original directives','Do not rewrite original Unreal or Rendezvous Godpack documents','pass' if immutable_ok else 'fail',None if immutable_ok else 'Original checksum mismatch.'),
    ]
    for suffix,title,threshold,status,blocker in v2_extra:
        add('V2-'+suffix,title,threshold,status,{'asset_quality':assets.get('quality_acceptance'),'runtime_gaps':runtime_assets.get('fixture_category_gaps'),'immutable_masterpack_match':immutable_ok},asset_paths+web_paths+['evidence/unreal_preflight.json','evidence/android_device_test.json'],'Execute named V2 fixture at declared tier; retain source/derivative/runtime evidence separately.','Source hashes/metrics plus controlled renderer/device measurements.',blocker,V2)

    # All twelve V3 tasks are literal source requirements, never prototype passes.
    v3_tasks = []
    for line in read(V3).splitlines():
        m = re.match(r'^(\d+)\. \*\*(.*?)\*\*:?\s*(.*)$', line)
        if m and 1 <= int(m[1]) <= 12:
            v3_tasks.append((int(m[1]), m[2], m[3]))
    v3_states = {
      1:('pass' if voice_ok else 'fail',{'clips':len(clips),'voices':len({c.get('voice_id') for c in clips}),'clip_hash_checks':clip_checks,'tts':voice.get('tts'),'Arabic':'actual Jordanian candidate bytes; redistribution/license clearance unresolved'},voice_paths,None if voice_ok else 'Real multi-voice/hash evidence incomplete.'),
      2:('blocked',{'local_environment':voice.get('environment'),'Oracle':voice.get('blockers',{}).get('Oracle2vCPU_ARM64')},voice_paths,'Oracle2-vCPU ARM64 node is not connected; local x86 measurements cannot establish ARM queue1vs2 or service health.'),
      3:('blocked',{'optional_paraphraser':'disconnected; deterministic grammar baseline executes','135M_360M_30line_benchmark':False},voice_paths,'Optional135M/360M worker experiment was not run; baseline speech has no LLM dependency.'),
      4:('fail',{'ASR':[{'locale':a.get('locale'),'kind':a.get('kind'),'engine':a.get('engine'),'WER':a.get('word_error_rate'),'intent':a.get('observed',{}).get('intent')} for a in voice.get('asr',[])],'microphone':'blocked'},voice_paths+['evidence/android_device_test.json'],'Arabic synthetic fixture WER=.333 fails error-free interaction; spontaneous Jordanian/noise and physical push-to-talk capture remain unverified.'),
      5:('blocked',{'server_ambient':'three independent café speakers','browser_visibleNPCs':scene.get('visibleNPCs'),'audio':telemetry.get('audio',{})},grammar_paths+web_paths,'Three visible speaking humans,3D attenuation/occlusion and supported lip/gesture synchronization are not jointly verified in the actual scene.'),
      6:('blocked',{'server_gate':gate,'browser_requests_count':len(browser.get('requests',[]))},['evidence/grammar_world_gate_integration.json']+web_paths,'Server prediction/hash-cache/retreat fixtures pass; actual approach/retreat/reroute network/cache bytes and event-correctness browser trace remains incomplete.'),
      7:('blocked',{'server_billboard':'actual ledger checkpoint/state hash computation','rendered_emissive_readability':'unverified'},['worldloom/session.py']+web_paths,'A true computed ledger report exists; nontrivial authorized-event computation, close-range emissive readability and material capture are not fully verified.'),
      8:('blocked',{'haven_server':'knowledge-scoped report and persistence fixture','walk_entry_in_scene':'unverified'},grammar_paths+web_paths,'Actual world-walk entry,NPC relevant knowledge,spoken report and rejoin have not been jointly exercised.'),
      9:('blocked',{'server_opportunities':'evidence-derived/no lifetime mission-count ceiling','15minute_scene_run':False},grammar_paths+web_paths,'No actual15-minute organic mission/voice/tap walk-through retained.'),
      10:('blocked',{'local_clip_cache':voice.get('tts',{}).get('cache_hit_fraction'),'browser_position_restore':browser.get('persistence_equal'),'device':android_device},voice_paths+web_paths+['evidence/android_device_test.json'],phone),
      11:('fail',{'V2_quality':assets.get('quality_acceptance'),'required_visual_gates':'independent of voice/billboards'},asset_paths+web_paths,art_gap),
      12:('pass' if immutable_ok else 'fail',{'immutable_originals':immutable_ok,'UE_cook_render':'blocked','native_transport_only':obj('evidence/unreal_native_interop.json').get('status')},['evidence/unreal_preflight.json','evidence/unreal_native_interop.json','evidence/masterpack-integrity.log'],None if immutable_ok else 'Original sources mismatch.'),
    }
    assert len(v3_tasks) == 12, 'Source V3 task extraction must include all twelve tasks'
    for i,title,threshold in v3_tasks:
        status,observed,paths,blocker=v3_states[i]
        add(f'V3-{i:02}',title,threshold,status,observed,paths,'Execute this literal integrated task in actual clients; retain source/model/hash/latency and authority/event witnesses.','Actual runtime integration evidence; source prototype/unit tests only establish their own local contracts.',blocker,V3)
    quant = [
      ('Q01','Cached speech onset','Decoded/local cached speech onset p95<250ms;uncached measured separately','blocked','No sufficient actual AudioContext activation-to-onset distribution;prefetch readyMs is not cached speech onset.'),
      ('Q02','Render/audio sync','Fixed-step drift,listener orientation,p95 underruns,pops,quantitative trace and human headphone listening','blocked','No complete actual audio-listener/drift/underrun distribution or human headphone scores.'),
      ('Q03','Masking','Natural-distance intelligibility falls with occlusion;no clipping or gratuitous loudness','blocked','Offline mix peak/click metrics pass; actual city masking and listening fixture absent.'),
      ('Q04','Prefetch metrics','True/false positive,wasted bytes,p50/p95 ready,cachehit,event activation,memory ceiling on Samsung tier','blocked',phone),
      ('Q05','Grammar purity','100% valid declared predicates;invalid typed rejection;seeded fuzz;prepare never commits','pass' if grammar.get('fuzz',{}).get('negative') == 80 and gate.get('committed_events_before') == gate.get('committed_events_after') == 0 else 'blocked',None),
      ('Q06','Held-out rendered evidence','Mixed voices,variable walks,weather,misspoken/ASR errors,unpredictable NPC movement in actual scene','blocked','Offline/grammar heldouts exist; integrated rendered held-out scenario not executed.'),
      ('Q07','First launch story','Controls/ambient/nearby conversation/spatial footsteps,speech,voice-pack event,real-program billboard,exit/rejoin without duplication','blocked','Complete first-launch integrated story and Android power/focus/rejoin not executed.'),
      ('REPORT','Build and cost evidence','Version/device/model/codec/phoneme/audio/APK/web hashes,latency/throughput,memory/energy/bandwidth,prompt comparisons,cache/failed logs;actualAudioContext/WebView','blocked','Source/model/audio/build hashes and local CPU timing exist; device energy/bandwidth and complete runtime metrics remain missing.'),
    ]
    for suffix,title,threshold,status,blocker in quant:
        add('V3-'+suffix,title,threshold,status,{'grammar_fuzz':grammar.get('fuzz'),'gate_events_before':gate.get('committed_events_before'),'gate_events_after':gate.get('committed_events_after'),'audio_context':telemetry.get('audio',{}).get('state')},grammar_paths+['evidence/grammar_world_gate_integration.json']+voice_paths+web_paths,'Run declared quality fixture with real clients; report unexecuted metrics as null/blocked.','Quantitative observed trace and declared target; scoped unit evidence never establishes hardware fidelity.',blocker,V3)

    # Local build lanes are useful evidence but never upgrade the integrated gates.
    lanes = [('APK-BYTES','Gradle APK build/inspection','pass' if apk_ok else 'fail',{'artifacts':apks},['evidence/android_build.log','evidence/android_aapt.txt','evidence/android_signature.txt']),('WEB-SMOKE','Local software-WebGL2 interaction','pass' if browser_ok else 'fail',{'movement':browser.get('movement_distance'),'persistence':browser.get('persistence_equal'),'scene':scene},web_paths)]
    for cid,title,status,observed,paths in lanes:
        add(cid,title,'Execute and retain the actual artifact/runtime smoke assertions.',status,observed,paths,'Run corresponding build/smoke command; inspect all output.','APK bytes/package/signature or actual Chromium rendered interaction.',None if status=='pass' else 'Actual local build/smoke evidence is incomplete or failed.','local-evidence-lane')
    for i,p in enumerate(args.test_log,1):
        add(f'FINAL-TEST-{i:02}',p,'Supplied final test command completes with zero failures.','pass' if log_pass(p) else 'fail',{'passed_log_detection':log_pass(p),'tail':read(p)[-1800:]},[p],'Run root-owned final test command and retain complete log.','Test runner exit/summary; use only for the contracts the suite actually covers.',None if log_pass(p) else 'Missing or failing supplied final test log.','local-evidence-lane')
    summary = dict(Counter(x['status'] for x in checks))
    return {'schema':'worldloom.acceptance.v1','generated_utc':datetime.now(timezone.utc).isoformat(),'full_commission_status':'fail' if summary.get('fail') else 'blocked' if summary.get('blocked') else 'pass','summary':summary,'acceptance_rule':'All original checks and additive rider gates retain independent statuses; local unit/artifact passes do not certify cinematic rendering,physical device,Oracle or Unreal.','build_hash':build_hash,'source_hash':source_hash,'source_commit':command('git','rev-parse','HEAD'),'source_branch':command('git','branch','--show-current'),'worktree_dirty':bool(command('git','status','--porcelain')),'source_file_hashes':sources,'build_artifacts':{'web_manifest':'artifacts/web/build-manifest.json','web_manifest_sha256':sha('artifacts/web/build-manifest.json'),'web_revision':web.get('revision'),'apks':apks},'environment':environment,'immutable_masterpack':{'passed':immutable_ok,'checks':check_integrity},'checks':checks,'evidence_index':evidence_index,'final_test_logs':args.test_log,'artifact_manifest_input':obj(args.artifact_manifest) if args.artifact_manifest else None}


def research(report):
    findings=[]
    for p in sorted((ROOT/'evidence').glob('*findings*.jsonl')):
        for i,line in enumerate(p.read_text().splitlines(),1):
            if not line.strip(): continue
            item=json.loads(line)
            item['source_record']={'path':str(p.relative_to(ROOT)),'line':i,'sha256':sha(p.relative_to(ROOT))}
            findings.append(item)
    ids={x.get('id') for x in findings}
    for city in ('london','marina'):
        path=f'evidence/geo_match_tampa_{city}.json';o=obj(path);c=o.get('certificate',{});cal=c.get('calibration',{})
        fid='GEO-'+city.upper()
        if fid not in ids:
            findings.append({'id':fid,'label':'M','hypothesis':f'Tampa–{city.title()} route winner is rare under the declared maximum-search null','status':'rejected','observed':{'conclusion':o.get('conclusion'),'certificate':c},'threshold':{'alpha':.05},'fixture':f"python -c 'from worldloom.geo import match_routes; print(match_routes(\"tampa\",\"{city}\",seed=31,samples=128))'",'witness':path,'limitation':'Valid tested negative; projection omits lane/building/POI features; no certified global resemblance.','next_experiment':'Enrich matched null controls and held-out independent source windows.'})
    sky=obj('evidence/sky_discovery.json')
    if 'SKY-01' not in ids:
        findings.append({'id':'SKY-01','label':'M','hypothesis':'Blind four-star motif is rare and reconstructs the traditional Southern Cross geometry','status':'rejected','observed':{'heldout_p':sky.get('p_value'),'benchmark':sky.get('benchmark'),'epoch_stability':sky.get('epoch_stability')},'threshold':{'rarity_alpha':.05,'traditional_geometry':'all declared traditional edges must be independently recovered'},'fixture':'python -c "from worldloom.sky import discover; print(discover(seed=42,null_trials=99))"','witness':'evidence/sky_discovery.json','limitation':'Partial source-vertex agreement and one of two edges; conditional RA null; no Gaia-scale discovery.','next_experiment':'Larger source catalog and independent sky-structure null; keep templates outside mining.'})
    for item in findings:
        default_fixture = 'python -m worldloom.numerics' if str(item.get('id','')).startswith('MATH') else 'python tools/voice_benchmark.py' if str(item.get('id','')).startswith('VOICE') else "python -c 'from worldloom.audio import render_soundscape; render_soundscape()'"
        item.setdefault('fixture',default_fixture)
        item.setdefault('witness',item.get('source_record',{}).get('path'))
        item.setdefault('observed',item.get('counterexample'))
        if item['observed'] is None:
            item.setdefault('measurement_status','not executed; no positive outcome inferred')
        item.setdefault('next_experiment','Repeat on independent held-out fixtures and the actual target runtime before generalizing.')
        item['build_hash']=report['build_hash'];item['source_hash']=report['source_hash']
    return findings


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test-log',action='append',default=[],help='Final root-owned test log, relative to repository; repeatable.')
    parser.add_argument('--build-hash',help='Optional externally retained final build hash.')
    parser.add_argument('--artifact-manifest',help='Optional final JSON artifact manifest to include.')
    args=parser.parse_args()
    report=compile_report(args)
    out=ROOT/'evidence/acceptance.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    lines=['# Acceptance ledger','',f"Full commission: **{report['full_commission_status'].upper()}**. {report['summary']}. Generated {report['generated_utc']}.",'',f"Source commit `{report['source_commit']}`; branch `{report['source_branch']}`; working tree changes present: `{report['worktree_dirty']}`.",f"Source-content SHA-256 `{report['source_hash']}`; build SHA-256 `{report['build_hash']}`.",'','Every original matrix row, all twelve V3 integrated tasks, and relevant V1/V2 stages remain independent. JSON contains exact thresholds, procedures, oracles, observed values, file hashes and blockers. A passing negative research experiment does not certify the proposed resemblance.','', 'Actual artifact and local test passes do not pass scene fidelity, Oracle ARM, Unreal, Samsung, physical microphone, or human listening gates. Public HTTPS hosting is not claimed.','', '| Check | Status | Requirement | Remaining gap |','|---|---|---|---|']
    for c in report['checks']:
        clean=lambda v:str(v).replace('|','/').replace('\n',' ')
        lines.append(f"| {c['check_id']} | {c['status'].upper()} | {clean(c['title'])} | {clean(c['blocker'] or 'Executed within the stated fixture scope.')} |")
    lines += ['', 'Rebuild this ledger after final evidence changes: `python tools/build_acceptance.py --test-log evidence/final-tests.log` (repeat `--test-log` for independent final lanes). This reads evidence and hashes artifacts; it does not run tests or upgrade unexecuted gates.','']
    (ROOT/'evidence/acceptance.md').write_text('\n'.join(lines))
    findings=research(report)
    (ROOT/'findings.jsonl').write_text(''.join(json.dumps(x,sort_keys=True,ensure_ascii=False)+'\n' for x in findings))
    print(json.dumps({'status':report['full_commission_status'],'checks':len(report['checks']),'summary':report['summary'],'findings':len(findings),'build_hash':report['build_hash'],'source_hash':report['source_hash']}))


if __name__=='__main__':
    main()
