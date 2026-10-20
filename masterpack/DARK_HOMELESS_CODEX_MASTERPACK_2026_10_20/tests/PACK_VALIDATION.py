"""Validate the handoff documents and signatures without source code dependencies."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
required=['README.md','CODEX_ONE_SHOT_INSTALL.md','specs/MASTER_PRD.md','specs/UNREAL_ASSETS_AND_STREAMING.md',
'specs/NPC_GAME_THEORY_AND_DARK.md','specs/WORLD_DATA_AND_GEOLOGIC_GRAPH.md',
'specs/ANDROID_WEB_AND_ONE_TAP_DELIVERY.md',
'research/PURL_SEURL_ACSP_CONTINUITY.md','research/GRAMMAR_GENERATOR_AND_RUNTIME_SHELL.md',
'research/OCTAVE_MATHEMATICAL_AUTHORITY.md','research/ASTROMETRIC_CONSTELLATABLES.md',
'research/SOUND_WEATHER_AND_CAMERA.md','interfaces/PROTOCOL_CONTRACTS.md',
'harness/SUBSTRATE_AGENT_HARNESS.md','tests/ACCEPTANCE_MATRIX.md']
for name in required:
    p=root/name
    assert p.exists() and p.stat().st_size>900,(name,'absent or too short')
alltxt='\n'.join((root/x).read_text() for x in required)
for token in ['Unreal Engine 5.8','PURL','SEURL','ACSP','Octave','Tampa','Android', 'Pixel Streaming', 'shell', 'sky', 'sound', 'WAMR', 'WebRTC']:
    assert token.lower() in alltxt.lower(),('missing scope',token)
assert len(re.findall(r'\b(?:F\d\d|G\d\d|V\d\d|S\d\d|D\d\d|N\d\d)\b',(root/'tests/ACCEPTANCE_MATRIX.md').read_text()))>=35
print('PASS: required documents',len(required),'with complete scope')
