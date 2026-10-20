import unittest
from gate_kernel import BootstrapPlanner, Gate, Resource, WorldCommitter, voice_key

class KernelTest(unittest.TestCase):
    def setUp(self):
        self.audio = Resource('voice.cafe.greeting','npc_speech',70000,9,20)
        self.mesh = Resource('cafe.glb','3d_asset',160000,6,40)
        self.rain = Resource('weather.ambient','audio',60000,3,10)
        self.g = Gate('cafe','CONVERSATION_EPISODE',0,12.0,1.5,12.0,3.0,True,(self.audio,self.mesh))
        self.p = BootstrapPlanner(230000,80)

    def test_plan_is_deterministic(self):
        a = self.p.plan([self.g],0)
        b = self.p.plan([self.g],0)
        self.assertEqual(a,b)
        self.assertEqual(a.staged_bytes,230000)
        self.assertEqual(a.eligible_gates,('cafe',))

    def test_prepare_does_not_activate(self):
        world = WorldCommitter()
        self.p.plan([self.g],0)
        self.assertEqual(world.world_revision,0)
        self.assertEqual(world.committed,{})

    def test_retreat_cancels(self):
        far = Gate('cafe','CONVERSATION_EPISODE',0,90,1,12,3,True,(self.audio,))
        r=self.p.plan([far],0)
        self.assertEqual(r.staged,())
        self.assertEqual(r.expired_gates,('cafe',))

    def test_stationary_far_does_not_predict(self):
        still = Gate('cafe','CONVERSATION_EPISODE',0,50,0,12,3,True,(self.audio,))
        self.assertEqual(self.p.plan([still],0).staged,())

    def test_near_stationary_may_prepare(self):
        still = Gate('cafe','CONVERSATION_EPISODE',0,1,0,12,3,True,(self.audio,))
        self.assertEqual(self.p.plan([still],0).staged,('voice.cafe.greeting',))

    def test_admissibility_matters(self):
        denied=Gate('cafe','CONVERSATION_EPISODE',0,1,1,12,3,False,(self.audio,))
        self.assertEqual(self.p.plan([denied],0).staged,())

    def test_byte_budget_enforced(self):
        p = BootstrapPlanner(20000,80)
        self.assertEqual(p.plan([self.g],0).staged,())

    def test_decode_budget_enforced(self):
        p = BootstrapPlanner(230000,20)
        self.assertEqual(p.plan([self.g],0).staged,('voice.cafe.greeting',))

    def test_deduplicate_shared_resource(self):
        second=Gate('balloon','MUSIC_CUE',0,9,1,12,3,True,(self.audio,))
        self.assertEqual(self.p.plan([second,self.g],0).staged.count(self.audio.id),1)

    def test_order_invariance(self):
        second=Gate('balloon','MUSIC_CUE',0,9,1,12,3,True,(self.rain,))
        self.assertEqual(self.p.plan([self.g,second],0),self.p.plan([second,self.g],0))

    def test_conflicting_resource_declaration_refused(self):
        altered = Resource('voice.cafe.greeting','npc_speech',1,9,20)
        second=Gate('balloon','MUSIC_CUE',0,9,1,12,3,True,(altered,))
        with self.assertRaises(ValueError):self.p.plan([self.g,second],0)

    def test_stale_revision_refused(self):
        with self.assertRaises(ValueError):self.p.plan([self.g],1)

    def test_activation_requires_proximity_and_approval(self):
        world=WorldCommitter()
        with self.assertRaises(PermissionError):world.activate(self.g,actual_distance_m=12,approved=True,event_id='e1',outcome='npc.line')
        with self.assertRaises(PermissionError):world.activate(self.g,actual_distance_m=2,approved=False,event_id='e1',outcome='npc.line')
        self.assertEqual(world.world_revision,0)

    def test_actual_event_commits_once(self):
        world=WorldCommitter()
        x=world.activate(self.g,actual_distance_m=2,approved=True,event_id='e1',outcome='npc.line')
        self.assertEqual(x,world.activate(self.g,actual_distance_m=1,approved=True,event_id='e1',outcome='npc.line'))
        self.assertEqual(world.world_revision,1)
        self.assertEqual(len(world.committed),1)

    def test_new_event_old_revision_refused(self):
        world=WorldCommitter()
        world.activate(self.g,actual_distance_m=2,approved=True,event_id='e1',outcome='npc.line')
        with self.assertRaises(ValueError):world.activate(self.g,actual_distance_m=2,approved=True,event_id='e2',outcome='npc.line')

    def test_voice_key_stable_and_revision_sensitive(self):
        a=voice_key('Hello','en-US','amber','model-r1','lex-r1')
        self.assertEqual(a,voice_key('Hello','en-US','amber','model-r1','lex-r1'))
        self.assertNotEqual(a,voice_key('Hello','en-US','amber','model-r2','lex-r1'))
        self.assertNotEqual(a,voice_key('مرحبا','ar-JO','amber','model-r1','lex-r1'))

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):Resource('bad','audio',-1,1)
        with self.assertRaises(ValueError):voice_key('', 'en-US', 'voice', 'model', 'lex')
        with self.assertRaises(ValueError):BootstrapPlanner(-1,0)

if __name__ == '__main__':unittest.main()
