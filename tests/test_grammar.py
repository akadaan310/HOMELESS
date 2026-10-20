import json
import unittest

from worldloom.grammar import GrammarFactory, Grammatical, compile_program, registry


class GrammarTests(unittest.TestCase):
    def setUp(self):
        self.factory = GrammarFactory()

    def test_three_generated_languages_certify_heldout(self):
        for subject in ('walk', 'audio', 'naming'):
            g = self.factory.build(subject)
            self.assertTrue(g['certificate']['passed'], g)
            self.assertGreater(g['certificate']['heldout_passed'], 0)
            self.assertTrue(g['productions'])
            self.assertEqual(g, self.factory.build(subject))

    def test_walk_graph_semantics_and_syntax_are_distinct(self):
        c = {'graph': {'a': ['b'], 'b': ['c'], 'c': []}}
        self.assertTrue(compile_program('walk', 'walk a b c', c)['valid'])
        self.assertEqual(compile_program('walk', 'walk a c', c)['diagnostics'][0]['code'], 'SEMANTIC_IMPOSSIBLE')
        self.assertEqual(compile_program('walk', 'fly a b', c)['diagnostics'][0]['code'], 'SYNTAX_INVALID')

    def test_audio_is_runnable_with_bounded_effects(self):
        p = compile_program('audio', 'emit bell 0.4 200')
        self.assertTrue(p['valid'])
        self.assertEqual(Grammatical(p).run()['effects'][0]['channel'], 'sound')
        self.assertFalse(compile_program('audio', 'emit bell 2 200')['valid'])

    def test_naming_is_fiction_and_real_name_collision_rejected(self):
        self.assertTrue(compile_program('naming', 'name cafe Amber Fold')['valid'])
        p = compile_program('naming', 'name cafe Real Shop', {'real_names': ['Real Shop']})
        self.assertFalse(p['valid'])

    def test_usage_prior_does_not_define_validity(self):
        common = compile_program('audio', 'emit bell 0.4 200')
        rare = compile_program('audio', 'emit balloon 0.1 850', {'balloon_audience': True, 'geometry_valid': True})
        self.assertTrue(rare['valid'])
        self.assertLess(rare['usage_logprob'], common['usage_logprob'])
        self.assertEqual(rare['diagnosis'], 'UNUSUAL_LEGITIMATE')
        self.assertFalse(compile_program('audio', 'emit balloon 0.1 850', {'balloon_audience': True, 'geometry_valid': False})['valid'])

    def test_fold_unfold_and_version_pinned_execution(self):
        p = compile_program('naming', 'name cafe باب Fold')
        g = Grammatical(p)
        self.assertEqual(g.expand(), p['program'])
        self.assertEqual(g.run(), g.run())
        altered = json.loads(json.dumps(p))
        altered['grammar_revision'] = 'forged'
        with self.assertRaises(ValueError):
            Grammatical(altered).run()

    def test_budget_and_missing_information(self):
        self.assertEqual(compile_program('walk', 'walk a b')['diagnostics'][0]['code'], 'MISSING_INFORMATION')
        self.assertEqual(compile_program('audio', 'emit bell 0.4 200', {'max_steps': 0})['diagnostics'][0]['code'], 'BUDGET')

    def test_registry_covers_contracts_without_fake_implementation(self):
        required = {'Actor','Activity','Event','Mission','Spatial','Portal','Society','Asset','Language','Governance','Sound','Sky','Weather','Camera','Vehicle','Transport','Economic','Emergence','Grammar Generator','Continuity','Procedural Signage'}
        self.assertTrue(required <= set(registry()))
        for model in registry().values():
            for k in ('alphabet','grammar','ingrammar','context','transitions','observer','verifier','budget','capability','status'):
                self.assertIn(k, model)

    def test_haven_requires_actual_evidence(self):
        self.assertFalse(compile_program('haven', 'meet haven report e1', {'events': []})['valid'])
        p = compile_program('haven', 'meet haven report e1', {'events': ['e1'], 'governed': True, 'consenting': True})
        self.assertTrue(p['valid'])
        self.assertEqual(Grammatical(p).run()['effects'][0]['kind'], 'meeting.propose')


if __name__ == '__main__':
    unittest.main()
