import importlib.util,json,pathlib,struct,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('asset_pipeline',ROOT/'tools/assets.py');assets=importlib.util.module_from_spec(spec);spec.loader.exec_module(assets)

class AssetTests(unittest.TestCase):
 def test_shipped_derivative_hashes(self):
  catalog=json.loads((ROOT/'assets/catalog.json').read_text())
  self.assertGreaterEqual(len(catalog['assets']),4)
  for asset in catalog['assets']:
   for variant in asset.get('variants',{}).values():
    if variant.get('sha256') and variant.get('path','').startswith('assets/runtime/'):
     self.assertEqual(assets.sha(ROOT/variant['path']),variant['sha256'])
   for variants_key in ('surface_variants','surface_low_variants'):
    for variant in asset.get(variants_key,{}).values():self.assertEqual(assets.sha(ROOT/variant['path']),variant['sha256'])
  for path in (ROOT/'assets/runtime').iterdir():
   if path.is_file():self.assertLessEqual(path.stat().st_size,25*1024*1024,'Static/mobile artifact exceeds25MiB: '+path.name)
 def test_actual_archived_source_hashes(self):
  catalog=json.loads((ROOT/'assets/catalog.json').read_text())
  files={f['path']:f for a in catalog['assets'] for f in a.get('files',[])}
  missing=[p for p in files if not (ROOT/p).exists()]
  if missing:self.skipTest('Archival source masters absent. Restore exact sources with python tools/assets_restore.py; reacquire/conversion: python tools/assets.py acquire and python tools/assets_rocketbox_fetch.py')
  for f in files.values():self.assertEqual(assets.sha(ROOT/f['path']),f['sha256'])
 def test_source_fidelity_and_rig_survive_packing(self):
  catalog=json.loads((ROOT/'assets/catalog.json').read_text())
  for item in catalog['assets']:
   source=item.get('source_metrics');variant=item.get('variants',{}).get('rendezvous-medium',{});runtime=variant.get('metrics')
   if not source or not runtime:continue
   if 'simplifier' in variant:
    self.assertLessEqual(runtime['triangles'],source['triangles']);self.assertGreater(runtime['triangles'],0)
    self.assertLessEqual(variant['simplifier']['mesh_radius_error_limit'],.01)
   else:self.assertEqual(source['triangles'],runtime['triangles'])
   self.assertEqual(source['bones'],runtime['bones']);self.assertEqual(source['animations'],runtime['animations'])
   self.assertTrue(runtime['passed']);self.assertGreater(runtime['triangles'],0)
 def test_glb_rejects_truncated_payload(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'bad.glb';p.write_bytes(struct.pack('<4sII',b'glTF',2,999))
   with self.assertRaises(ValueError):assets.load_gltf(p)
 def test_catalog_does_not_invent_cinematic_acceptance(self):
  data=json.loads((ROOT/'assets/catalog.json').read_text())
  self.assertIn('FAIL',data['quality_acceptance']['hero_scene'])
  for item in data['assets']:
   self.assertNotEqual(item.get('import_status'),'cooked');self.assertNotEqual(item.get('scene_test'),'rendered')
 def test_unreal_preflight_exposes_exact_blockers(self):
  spec=importlib.util.spec_from_file_location('ue_preflight',ROOT/'tools/unreal_preflight.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  result=module.detect()
  self.assertTrue(result['source_project_present'])
  if result['ue_root'] is None:self.assertIn('UE_SDK_MISSING',[x['code'] for x in result['blockers']])

if __name__=='__main__':unittest.main()
