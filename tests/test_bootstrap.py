import copy
import hashlib
import unittest

from worldloom.bootstrap import BootstrapScheduler


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.s = {'revision': 2, 'events': [], 'cell': 'tampa'}
        self.resources = [{'id':'voice', 'kind':'npc_speech', 'bytes':4, 'memory_bytes':8, 'decode_ms':2, 'hash':hashlib.sha256(b'clip').hexdigest()}, {'id':'mesh','kind':'glb','bytes':12,'memory_bytes':20,'decode_ms':4,'hash':hashlib.sha256(b'mesh'*3).hexdigest()}]
        self.g = {'id':'cafe', 'kind':'CONVERSATION_EPISODE', 'candidateStateRevision':2, 'distance_m':12, 'speed_mps':2, 'horizonSeconds':10, 'activation_radius_m':3, 'admitted':True, 'resourceSet':['voice','mesh'], 'priority':'A', 'expiry':20, 'sourceActor':'npc:0', 'authority':'scene.activate', 'effect':{'kind':'conversation.listen'}}

    def test_plan_deterministic_bounded_and_does_not_commit_world(self):
        p = BootstrapScheduler(byte_budget=10,memory_budget=10,decode_budget_ms=3)
        before = copy.deepcopy(self.s)
        a = p.plan(self.s,[self.g],self.resources,now=0)
        self.assertEqual(a,p.plan(self.s,[self.g],self.resources,now=0))
        self.assertEqual(a['staged'],['voice'])
        self.assertEqual(self.s,before)
        self.assertEqual(a['effects_committed'],[])

    def test_retreat_cancels_and_cache_reuses(self):
        p = BootstrapScheduler()
        p.plan(self.s,[self.g],self.resources,now=0)
        p.prepare('voice', b'clip')
        far = dict(self.g,distance_m=100)
        r = p.plan(self.s,[far],self.resources,now=1)
        self.assertEqual(r['canceled'],['cafe'])
        self.assertEqual(p.status()['cache_bytes'],4)

    def test_stale_invalid_and_stationary_far_do_not_stage(self):
        for g in (dict(self.g,candidateStateRevision=1),dict(self.g,speed_mps=0),dict(self.g,admitted=False)):
            self.assertFalse(BootstrapScheduler().plan(self.s,[g],self.resources,now=0)['staged'])

    def test_resource_hash_verified_and_atomic_reservation(self):
        p = BootstrapScheduler(); p.plan(self.s,[self.g],self.resources,now=0)
        with self.assertRaises(ValueError):p.prepare('voice',b'fake')
        p.prepare('voice',b'clip')
        self.assertEqual(p.status()['gates']['cafe']['state'],'STAGE')
        p.prepare('mesh',b'mesh'*3)
        self.assertEqual(p.status()['gates']['cafe']['state'],'RESERVE')

    def test_activation_is_proposal_requires_live_predicates_and_capability(self):
        p=BootstrapScheduler();p.plan(self.s,[self.g],self.resources,now=0)
        p.prepare('voice',b'clip');p.prepare('mesh',b'mesh'*3)
        with self.assertRaises(PermissionError):p.activate('cafe', self.s,actual_distance_m=2,authority=[])
        with self.assertRaises(PermissionError):p.activate('cafe', self.s,actual_distance_m=8,authority=['scene.activate'])
        r=p.activate('cafe',self.s,actual_distance_m=2,authority=['scene.activate'])
        self.assertEqual(r['effect_policy'],'propose-only')
        self.assertEqual(len(self.s['events']),0)

    def test_expiry_and_low_battery_reduce_prefetch(self):
        p=BootstrapScheduler()
        self.assertFalse(p.plan(self.s,[self.g],self.resources,now=30)['staged'])
        low=dict(self.s,battery=0.03)
        c=dict(self.g,priority='C')
        self.assertFalse(p.plan(low,[c],self.resources,now=0)['staged'])

    def test_order_invariance_conflict_detection_and_eviction(self):
        p=BootstrapScheduler(memory_budget=30)
        a=p.plan(self.s,[self.g],self.resources,now=0)
        self.assertEqual(a,p.plan(self.s,[self.g],list(reversed(self.resources)),now=0))
        p.prepare('voice',b'clip');p.prepare('mesh',b'mesh'*3)
        self.assertEqual(p.evict(0),['mesh','voice'])
        with self.assertRaises(ValueError):p.plan(self.s,[self.g],self.resources+[dict(self.resources[0],bytes=99)],now=0)

    def test_changed_hash_invalidates_reservation(self):
        p=BootstrapScheduler();p.plan(self.s,[self.g],self.resources,now=0)
        p.prepare('voice',b'clip');p.prepare('mesh',b'mesh'*3)
        revised=[dict(self.resources[0],hash=hashlib.sha256(b'dlip').hexdigest()),self.resources[1]]
        p.plan(self.s,[self.g],revised,now=1)
        self.assertEqual(p.status()['gates']['cafe']['state'],'STAGE')

    def test_world_session_uses_scheduler_without_ledger_commit(self):
        import tempfile
        from pathlib import Path
        from worldloom.session import WorldSession
        with tempfile.TemporaryDirectory() as directory:
            session=WorldSession(Path(directory)/'world.db')
            before=session.store.verify()['count']
            result=session.invoke({'operation':'gate.plan','payload':{'position':[0,0,0],'velocity':[0,0,0]}})
            self.assertEqual(result['status'],'ok',result)
            self.assertEqual(result['data']['solver'],'deterministic-greedy-priority.v1')
            prepared=session.invoke({'operation':'gate.prepare','payload':{'plan_id':result['data']['plan_id']}})
            self.assertEqual(prepared['status'],'ok',prepared)
            self.assertEqual(before,session.store.verify()['count'])
            session.close()

    def test_world_session_prepares_assets_animation_report_and_cancels_on_retreat(self):
        import tempfile
        from pathlib import Path
        from worldloom.session import WorldSession
        with tempfile.TemporaryDirectory() as directory:
            session=WorldSession(Path(directory)/'world.db')
            before=session.store.verify()['count']
            query={'operation':'gate.plan','payload':{'position':[0,0,0],'velocity':[0,0,-2]}}
            plan=session.invoke(query)['data']
            self.assertIn('animated_glb',{r['kind'] for r in plan['resources']})
            self.assertIn('BILLBOARD_PROGRAM',{g['kind'] for g in plan['gates']})
            self.assertIn('RENDEZVOUS_HAVEN',{g['kind'] for g in plan['gates']})
            prepared=session.invoke({'operation':'gate.prepare','payload':{'plan_id':plan['plan_id']}})
            self.assertEqual(prepared['status'],'ok',prepared)
            self.assertTrue(prepared['data']['prepared'])
            retreat=session.invoke({'operation':'gate.plan','payload':{'position':[1000,0,1000],'velocity':[0,0,0]}})['data']
            self.assertTrue(retreat['canceled'])
            self.assertEqual(before,session.store.verify()['count'])
            session.close()


if __name__ == '__main__':unittest.main()
