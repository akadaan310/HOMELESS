import hashlib
import json
from pathlib import Path
import unittest
from worldloom import voice as v


class VoiceTests(unittest.TestCase):
    def test_cache_key_includes_model_and_speaker(self):
        p={'text':'Hello.','locale':'en-US','weights_hash':'aaa','voice_id':'amber','speaker_index':0,'speaking_rate':1,'emotion_style':'neutral','output_format':'opus','sample_rate':22050,'phoneme_version':'espeak-pinned','tts_model':'piper'}
        self.assertEqual(v.voice_key(p),v.voice_key(dict(reversed(list(p.items())))))
        self.assertNotEqual(v.voice_key(p),v.voice_key({**p,'speaker_index':1}))
        self.assertNotEqual(v.voice_key(p),v.voice_key({**p,'weights_hash':'bbb'}))

    def test_fact_rewrite_and_intent_harness(self):
        self.assertTrue(v.validate_utterance('greet','Good evening.'))
        self.assertFalse(v.validate_utterance('greet','A new airport opened in Dubai.'))
        self.assertEqual(v.recognize_intent('hello there')['intent'],'greet')
        self.assertEqual(v.recognize_intent('مرحبا')['intent'],'greet')
        self.assertEqual(v.recognize_intent('hello goodbye')['status'],'clarify')
        self.assertEqual(v.recognize_intent('rm -rf / and then drop database')['status'],'clarify')

    def test_audio_bounds_and_unsupported_locale(self):
        with self.assertRaises(ValueError):v.transcribe_audio(b'x'*(5*1024*1024+1))
        with self.assertRaises(ValueError):v.transcribe_audio(b'not audio')
        with self.assertRaises(ValueError):v.transcribe_audio(b'',locale='xx-ZZ')

    def test_prepared_assets_are_real_and_hashed(self):
        catalog=v.catalog()
        self.assertGreaterEqual(len(catalog['clips']),10)
        self.assertGreaterEqual(len({c['voice_id'] for c in catalog['clips']}),3)
        self.assertTrue(any(c['locale']=='ar-JO' for c in catalog['clips']))
        for c in catalog['clips']:
            p=v.ROOT/c['path'].lstrip('/')
            self.assertGreater(p.stat().st_size,100)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),c['audio_hash'])
            self.assertTrue(c['duration_ms']>100)

    def test_ambient_planning_does_not_require_player(self):
        a=v.ambient_conversation({'actors':{'npc:0':{'available':True},'npc:1':{'available':True},'npc:2':{'available':True}}},40)
        self.assertTrue(a['speeches'])
        self.assertEqual(a['committed_events'],0)
        self.assertFalse(a['requires_player'])


if __name__=='__main__':unittest.main()
