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
 def test_public_observer_does_not_gain_private_npc_memory(self):
  from worldloom.society import World
  snapshot=World(seed=7).snapshot();snapshot['actors'][0]['memory']=[{'secret':'hidden'}]
  self.commit(payload={'kind':'world.snapshot','snapshot':snapshot})
  r=self.engine.invoke({'operation':'query'})
  self.assertNotIn('memory',r['data']['world']['actors'][0]);self.assertNotIn('schedule',r['data']['world']['actors'][0])
 def test_operator_revocation_survives_restart(self):
  token=self.store.operator_token;self.store.revoke(token);self.store.close();self.store=Store(self.db)
  self.assertFalse(self.store.authorized(token,'dark','*'))
 def test_incomplete_typed_effects_never_enter_the_ledger(self):
  for payload in [{'kind':'world.snapshot'},{'kind':'event.activate'},{'kind':'journey.append','position':'bad'}]:
   self.assertEqual(self.commit(payload=payload)['status'],'error')
  self.assertEqual(self.store.verify()['count'],0)
 def test_pinned_context_replays_old_version_without_side_effects(self):
  first=self.commit()['commit_id']
  q={'operation':'query','program':'purl://dark/world/state','context_hash':first}
  before=self.engine.invoke(q)
  self.commit(event_id='e2',payload={'kind':'sign.rename','object':'cafe','text':'Second Name'})
  count=self.store.verify()['count'];after=self.engine.invoke(q)
  self.assertEqual(before,after);self.assertEqual(after['data']['objects']['cafe']['text'],'Golden Haven')
  self.assertEqual(self.store.verify()['count'],count)
  self.assertEqual(self.engine.invoke({**q,'context_hash':'unknown'})['status'],'error')
 def test_corruption_detected(self):
  self.commit();self.store.db.execute("UPDATE events SET body='{}'");self.store.db.commit();self.assertFalse(self.store.verify()['valid'])

if __name__=='__main__':unittest.main()
