import unittest,tempfile,pathlib
from worldloom.session import WorldSession
class Session(unittest.TestCase):
 def test_player_effect_persists_without_founder_impersonation(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'world.db';w=WorldSession(p);s=w.open_player();headers={'actor':s['actor'],'capability':s['token'],'session':s['session']}
   q={**headers,'operation':'journey.append','event_id':'walk-1','payload':{'kind':'walk','position':[1,0,2]}}
   a=w.invoke(q);self.assertEqual(a['status'],'ok');self.assertIsNotNone(a['commit_id']);self.assertEqual(w.invoke(q)['commit_id'],a['commit_id'])
   self.assertEqual(w.invoke({**q,'actor':'dark','event_id':'forged'})['status'],'refused')
   check=w.store.checkpoint();w.close();w=WorldSession(p)
   self.assertEqual(w.store.checkpoint(),check);self.assertEqual(len(w.store.state()['sessions'][s['session']]),1);w.close()
 def test_read_and_prepare_do_not_commit(self):
  with tempfile.TemporaryDirectory() as t:
   w=WorldSession(pathlib.Path(t)/'db');before=w.store.verify()['count'];w.invoke({'operation':'billboard.inspect','payload':{}});w.invoke({'operation':'gate.plan','payload':{'position':[0,0,0],'velocity':[1,0,0]}})
   self.assertEqual(w.store.verify()['count'],before);w.close()
 def test_invalid_operation_returns_typed_error(self):
  with tempfile.TemporaryDirectory() as t:
   w=WorldSession(pathlib.Path(t)/'db');self.assertEqual(w.invoke({'operation':[],'payload':{}})['status'],'error');w.close()
 def test_shell_query_sees_current_frozen_world_without_deadlock(self):
  import json
  with tempfile.TemporaryDirectory() as t:
   w=WorldSession(pathlib.Path(t)/'db');w.world.tick(1)
   r=w.invoke({'operation':'shell.run','payload':{'source':'darkctl query'},'actor':'dark','capability':w.store.operator_token})
   self.assertEqual(r['data']['exit_code'],0)
   output=json.loads(r['data']['stdout'])['data']['data']
   self.assertEqual(output['world']['tick'],w.world.tick_count);self.assertEqual(len(output['world']['actors']),24);w.close()
if __name__=='__main__':unittest.main()
