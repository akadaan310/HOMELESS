import math
import tempfile
import unittest
import wave
from pathlib import Path
from worldloom import audio as a


class AudioTests(unittest.TestCase):
    def test_spatial_direction_attenuation_and_occlusion(self):
        mono = [math.sin(i * .3) for i in range(1000)]
        left, right = a.spatialize(mono, azimuth=-60, distance=2)
        self.assertGreater(sum(v*v for v in left), 5 * sum(v*v for v in right))
        far = a.spatialize(mono, azimuth=-60, distance=20)
        self.assertLess(sum(v*v for v in far[0]), sum(v*v for v in left))
        occluded = a.spatialize(mono, azimuth=-60, distance=2, occlusion=1)[0]
        self.assertLess(sum((x-y)**2 for x,y in zip(occluded[1:], occluded)), sum((x-y)**2 for x,y in zip(left[1:], left)))

    def test_deterministic_sources_and_click_envelopes(self):
        for family in ('engine', 'traffic', 'pedestrian', 'airplane', 'music', 'weather'):
            m = a.synthesize(family, duration=.1, seed=5)
            self.assertEqual(m, a.synthesize(family, duration=.1, seed=5))
            self.assertLess(abs(m[0]), 1e-5)
            self.assertLess(abs(m[-1]), 1e-5)
        with self.assertRaises(ValueError):
            a.synthesize('imaginary')

    def test_render_actual_wav_stems_and_mix(self):
        with tempfile.TemporaryDirectory() as td:
            m = a.render_soundscape(td, duration=4)
            self.assertEqual(set(m['sources']), {'engine', 'traffic', 'voice', 'pedestrian', 'airplane', 'music', 'weather'})
            with wave.open(str(Path(td) / 'world_mix.wav')) as w:
                self.assertEqual(w.getnchannels(), 2)
                self.assertEqual(w.getnframes(), 4 * a.SAMPLE_RATE)
            self.assertLessEqual(m['metrics']['sample_peak'], .86)
            self.assertEqual(m['metrics']['heavy_click_count'], 0)
            self.assertLessEqual(m['metrics']['event_error_max_samples'], .5)

    def test_cue_decline_cancels_replay(self):
        result = a.cue_policy([{'event_id':'bell', 'time':0}, {'event_id':'bell','time':20,'response':'ignore'}, {'event_id':'bell','time':100}])
        self.assertEqual(len(result['emitted']), 1)
        self.assertEqual(result['suppressed'][-1]['reason'], 'declined-or-ignored')
        self.assertEqual(a.cue_policy([{'event_id':'bell','time':0}], enabled=False)['emitted'], [])


if __name__ == '__main__':
    unittest.main()

class CrossfadeTests(unittest.TestCase):
    def test_equal_power_domain_crossfade_and_loop_metrics(self):
        street = [1.] * 200
        car = [0.] * 200
        mixed = a.crossfade(street, car, 100)
        self.assertEqual(len(mixed), 300)
        self.assertEqual(mixed[0], 1)
        self.assertEqual(mixed[-1], 0)
        self.assertLess(max(abs(x-y) for x,y in zip(mixed[1:],mixed)), .016)
        loop = [math.sin(2*math.pi*i/100) for i in range(1000)]
        metric = a.loop_metrics(loop,100)
        self.assertAlmostEqual(metric['boundary_correlation'],1,places=9)
