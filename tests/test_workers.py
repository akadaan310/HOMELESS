import unittest
from worldloom.workers import shell, javascript, wasm
class Workers(unittest.TestCase):
 def test_real_shell_pipes_proposals_and_clock(self):
  r=shell("printf 'golden\\n' | tr a-z A-Z; darkctl time; darkctl propose sign.rename cafe 'Golden Haven'")
  self.assertEqual(r['exit_code'],0);self.assertIn('GOLDEN',r['stdout']);self.assertIn('world_epoch',r['stdout']);self.assertEqual(r['typed_effects_proposed'][0]['kind'],'sign.rename');self.assertEqual(r['effects_committed'],[])
 def test_shell_host_isolation_and_output_and_timeout(self):
  r=shell('cat /etc/passwd');self.assertNotEqual(r['exit_code'],0)
  r=shell('while true; do echo aaaaaaaaaaaaaaaaaaaaaaaaaaaaa; done',wall_time_ms=150,max_output_bytes=1000)
  self.assertLessEqual(len(r['stdout'].encode()),1000);self.assertTrue(r['timed_out'] or r['output_limited'])
 def test_actual_javascript_budgets_and_no_system(self):
  r=javascript("JSON.stringify({kind:'sky.overlay',intensity:0.2})");self.assertEqual(r['event']['kind'],'sky.overlay')
  self.assertEqual(javascript('while(true){}',wall_time_ms=50)['status'],'timeout')
  self.assertNotEqual(javascript("require('fs').readFileSync('/etc/passwd')")['status'],'ok')
 def test_actual_wasm_and_import_rejection(self):
  r=wasm('(module (func (export "event") (result i32) i32.const 7))');self.assertEqual(r['event']['value'],7)
  self.assertNotEqual(wasm('(module (import "host" "erase" (func)) (func (export "event") (result i32) i32.const 0))')['status'],'ok')
  self.assertEqual(wasm('(module (func (export "event") (result i32) (loop $l br $l) i32.const 0))',fuel=1000)['status'],'timeout')
if __name__=='__main__':unittest.main()
