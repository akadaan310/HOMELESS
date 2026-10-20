import json
import unittest

from worldloom.society import World, ride_equilibria


class WorldTests(unittest.TestCase):
    def test_population_is_lazy_and_does_not_decrement_on_join(self):
        w = World(seed=7)
        s = w.snapshot()
        self.assertEqual(s['population']['capacity'], 8_190_000_000)
        self.assertLess(s['population']['active'], 100)
        self.assertEqual(w.resolve_actor(8_189_999_999), w.resolve_actor(8_189_999_999))
        self.assertEqual(w.snapshot()['population']['capacity'], s['population']['capacity'])
        with self.assertRaises(IndexError): w.resolve_actor(8_190_000_000)

    def test_founder_identity_and_ambient_life_preexist_entry(self):
        s = World().snapshot()
        self.assertEqual(s['founder']['legal_name'], 'Abed Kadan')
        self.assertEqual(s['founder']['origin'], 'Marina del Rey')
        self.assertTrue(s['conversations'])
        self.assertGreater(len(s['actors']), 10)

    def test_replay_and_restore_after_time_passes(self):
        a, b = World(seed=11), World(seed=11)
        a.tick(90); b.tick(90)
        self.assertEqual(a.snapshot(), b.snapshot())
        restored = World.from_snapshot(json.loads(json.dumps(a.snapshot())))
        restored.tick(50); a.tick(50)
        self.assertEqual(restored.snapshot(), a.snapshot())

    def test_actor_decisions_have_solver_witness_and_schedules(self):
        w = World(); w.tick(60)
        s = w.snapshot()
        self.assertTrue(s['decisions'])
        for d in s['decisions']:
            self.assertIn(d['selected_action'], d['available_actions'])
            self.assertEqual(d['solver'], 'enumerated-best-response.v1')
            self.assertIn('tie_break', d['witness'])
        self.assertTrue(all(len(a['schedule']) == 48 for a in s['actors']))

    def test_refusal_and_observer_limited_memory(self):
        w = World()
        near, far = w.snapshot()['actors'][:2]
        w.actors[near['actor_id']]['position'] = [0,0,0]
        w.actors[far['actor_id']]['position'] = [1000,0,0]
        e = w.emit('speak', 'player', [0,0,0], {'text': 'hello'})
        self.assertIn(e['id'], [m['event_id'] for m in w.memory(near['actor_id'])])
        self.assertNotIn(e['id'], [m['event_id'] for m in w.memory(far['actor_id'])])
        r = w.invite_ride(near['actor_id'], compatibility=0, seats=0, time_available=0)
        self.assertEqual(r['selected_action'], 'decline')
        self.assertTrue(r['refusal_reason'])

    def test_speech_intents_clarify_and_never_run_commands(self):
        w = World()
        self.assertEqual(w.dispatch('speech.act', {'text': 'ride or walk', 'confidence': .4}, 'player')['data']['act'], 'clarify')
        self.assertEqual(w.dispatch('speech.act', {'text': 'rm -rf /', 'confidence': 1}, 'player')['data']['act'], 'clarify')
        self.assertEqual(w.dispatch('speech.act', {'text': 'hello', 'confidence': .99}, 'player')['data']['act'], 'greet')

    def test_two_equilibria_recorded_and_tie_break_changes_outcome(self):
        a, b = ride_equilibria('share'), ride_equilibria('separate')
        self.assertGreaterEqual(len(a['equilibria']), 2)
        self.assertNotEqual(a['selected'], b['selected'])

    def test_founder_role_cannot_be_claimed_by_name(self):
        w = World()
        r = w.dispatch('cohort.delegate', {'member': 'p', 'roles': ['signage']}, 'dark')
        self.assertEqual(r['status'], 'refused')
        inv = w.dispatch('cohort.invite', {'member': 'p'}, 'founder', capabilities=['founder'])
        self.assertEqual(inv['status'], 'ok')
        self.assertEqual(w.dispatch('cohort.accept', {}, 'p')['status'], 'ok')
        w.dispatch('cohort.delegate', {'member':'p', 'roles':['signage'], 'duration':60}, 'founder', capabilities=['founder'])
        self.assertTrue(w.authorized('p','signage'))
        w.dispatch('cohort.revoke', {'member':'p'}, 'founder', capabilities=['founder'])
        self.assertFalse(w.authorized('p','signage'))

    def test_journey_and_coauthor_adoption_have_unfold_witness(self):
        w = World()
        r = w.dispatch('journey.record', {'kind':'walk', 'position':[1,0,1]}, 'p')
        self.assertEqual(r['status'], 'ok')
        j = w.snapshot()['journeys']['p']
        self.assertTrue(j['address'].startswith('purl://'))
        self.assertEqual(j['events'][0]['kind'], 'walk')
        p = w.dispatch('authorship.propose', {'name':'Amber Fold', 'kind':'cafe', 'scene_id':'tampa-shop'}, 'p')['data']
        w.dispatch('authorship.endorse', {'proposal_id':p['proposal_id'], 'consent':True}, 'npc:0')
        a = w.dispatch('authorship.adopt', {'proposal_id':p['proposal_id']}, 'founder', capabilities=['founder'])
        self.assertEqual(a['status'], 'ok')
        self.assertTrue(a['data']['unfold_witness'])
        self.assertEqual(w.snapshot()['signs']['tampa-shop']['name'], 'Amber Fold')

    def test_missions_have_no_arbitrary_lifetime_count_ceiling(self):
        w = World()
        a = w.mission_opportunity({'goal':'learn', 'evidence':['e1'], 'consent':True})
        b = w.mission_opportunity({'goal':'learn', 'evidence':['e2'], 'consent':True})
        self.assertNotEqual(a['address'], b['address'])
        self.assertEqual(a['completion_invariant'], 'evidence-recorded-and-reported')

    def test_distinct_knowledge_and_social_outcomes(self):
        w=World()
        w.actors['npc:0']['needs']['energy']=1
        w.actors['npc:0']['activity']='rest'
        self.assertEqual(w.dispatch('npc.interact',{'npc_id':'npc:0','text':'teach me'},'p')['data']['outcome'],'npc-teaches')
        self.assertEqual(w.dispatch('npc.interact',{'npc_id':'npc:0','text':'look up'},'p')['data']['outcome'],'npc-notices-sky-cue')
        self.assertEqual(w.dispatch('npc.interact',{'npc_id':'npc:0','position':[1000,0,0]},'p')['data']['act'],'not-noticed')

    def test_actual_realms_counterfactual_adapter(self):
        w=World()
        witness=w.social_impact({'p':(0,'help'),'npc:1':(1,'gift')})
        self.assertEqual(witness['backend'],'REALMS-0.1-original')
        self.assertAlmostEqual(sum(witness['shares'].values()),witness['total'])
        self.assertLess(witness['spectral_radius'],1)

    def test_npc_coauthor_chooses_and_records_own_consent(self):
        w=World();w.actors['npc:0']['needs']['energy']=1;w.actors['npc:0']['preferences']['conversation']=1
        proposal=w.dispatch('authorship.propose',{'name':'Golden Thread','scene_id':'tampa-shop'},'p')['data']
        result=w.dispatch('npc.interact',{'npc_id':'npc:0','act':'coauthor','proposal_id':proposal['proposal_id']},'p')
        self.assertEqual(result['data']['act'],'coauthor')
        self.assertEqual(result['data']['decision']['selected_action'],'endorse')
        self.assertIn('npc:0',w.proposals[proposal['proposal_id']]['collaborators'])
        w.actors['npc:1']['position']=[1000,0,0]
        refused=w.dispatch('npc.interact',{'npc_id':'npc:1','act':'coauthor','proposal_id':proposal['proposal_id']},'p')
        self.assertEqual(refused['data']['act'],'not-noticed')


if __name__ == '__main__': unittest.main()
