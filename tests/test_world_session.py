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
if __name__=='__main__':unittest.main()
