import tempfile, pathlib, unittest, uuid
from worldloom.protocol import Engine, Store, ProtocolError

class Continuity(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=pathlib.Path(self.tmp.name)/'world.db';self.store=Store(self.db);self.engine=Engine(self.store)
 def tearDown(self):self.store.close();self.tmp.cleanup()
 def commit(self,**kw):
  q={'protocol':'seurl.world.v1','operation':'commit','actor':'dark','capability':self.store.operator_token,'event_id':'e1','session':'s1','payload':{'kind':'sign.rename','object':'cafe','text':'Golden Haven'}};q.update(kw);return self.engine.invoke(q)
 def test_read_is_pure_and_founder_string_is_not_authority(self):
  before=self.store.verify();self.assertEqual(self.engine.invoke({'operation':'query','program':'purl://dark/world/state'})['status'],'ok');self.assertEqual(self.store.verify(),before)
  self.assertEqual(self.commit(capability='forged')['status'],'refused');self.assertEqual(self.store.verify()['count'],0)
 def test_dedup_conflict_restart_and_hash_chain(self):
  a=self.commit();self.assertEqual(a['status'],'ok');self.assertEqual(self.commit()['commit_id'],a['commit_id']);self.assertEqual(self.store.verify()['count'],1)
  self.assertEqual(self.commit(payload={'kind':'sign.rename','object':'cafe','text':'Other'})['status'],'conflict')
  checkpoint=self.store.checkpoint();self.store.close();self.store=Store(self.db);self.assertEqual(self.store.checkpoint(),checkpoint)
  self.assertEqual(self.store.state()['objects']['cafe']['text'],'Golden Haven');self.assertTrue(self.store.verify()['valid'])
 def test_malformed_nonfinite_unknown_and_parent_conflict(self):
  self.assertEqual(self.engine.invoke({'operation':'query','program':'https://bad'})['status'],'error')
  self.assertEqual(self.commit(payload={'kind':'sign.rename','object':'cafe','text':'a','x':float('nan')})['status'],'error')
  self.assertEqual(self.commit(expected_head='bad')['status'],'conflict')
  self.assertEqual(self.engine.invoke({'operation':'erase.everything'})['status'],'unsupported')
 def test_revoke_scoped_capability(self):
  cap=self.store.grant('alice',['sign.rename']);a=self.commit(actor='alice',capability=cap);self.assertEqual(a['status'],'ok')
  self.store.revoke(cap);self.assertEqual(self.commit(actor='alice',capability=cap,event_id='e2')['status'],'refused')
 def test_corruption_detected(self):
  self.commit();self.store.db.execute("UPDATE events SET body='{}'");self.store.db.commit();self.assertFalse(self.store.verify()['valid'])

if __name__=='__main__':unittest.main()
