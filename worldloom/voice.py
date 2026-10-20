"""Cached neural speech and bounded offline ASR. Text never directly executes effects."""
from __future__ import annotations
from array import array
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave

ROOT=Path(__file__).resolve().parents[1]
MODEL_DIR=ROOT/'data/voice/models'
CATALOG=ROOT/'artifacts/voice/catalog.json'
_WORKER=threading.Lock()
_ASR={}
MAX_AUDIO_BYTES=5*1024*1024
MAX_AUDIO_SECONDS=15
VOICES={
    'amber':{'model':'en_US-libritts_r-medium','speaker_index':0,'locale':'en-US','license':'CC BY 4.0 dataset; Piper GPL-3.0 runtime'},
    'river':{'model':'en_US-libritts_r-medium','speaker_index':4,'locale':'en-US','license':'CC BY 4.0 dataset; Piper GPL-3.0 runtime'},
    'cedar':{'model':'en_US-libritts_r-medium','speaker_index':10,'locale':'en-US','license':'CC BY 4.0 dataset; Piper GPL-3.0 runtime'},
    'yusuf':{'model':'ar_JO-kareem-low','speaker_index':0,'locale':'ar-JO','license':'dataset model card says See URL; redistribution review unresolved; local evaluation'},
}
PHRASES=[
    ('greet','amber','Good evening.'),
    ('notice','river','I saw the light change by the crossing.'),
    ('reply','cedar','I noticed it too. The street keeps moving.'),
    ('offer','amber','Would you like to walk with us?'),
    ('refuse','river','Thank you, but I need to finish my own route.'),
    ('acknowledge','cedar','All right. We can meet another time.'),
    ('clarify','amber','Could you say that again, please?'),
    ('farewell','river','Take care. I will see you around.'),
    ('invite','cedar','You can listen here, or keep exploring.'),
    ('thanks','amber','Thank you for sharing what you saw.'),
    ('cafe.sign','amber','The new sign says Amber Fold. I like the sound of it.'),
    ('walk.pattern','river','The walk we recorded bends left, then right by the corner.'),
    ('haven.report','cedar','We can bring the record to the haven when we meet.'),
    ('greet','amber','Hello. We were just talking about the sign.'),
    ('decline','amber','Of course. You can keep exploring.'),
    ('accept','amber','All right. Let us check the details first.'),
    ('ride','amber','Where would you like to go?'),
    ('learn','amber','We can compare the turns in a recorded walk.'),
    ('report','amber','The haven has the witnessed world record.'),
    ('look_up','amber','Look above the street. That cue belongs to our fictional sky layer.'),
    ('clarify','amber','Did you want to talk, learn a pattern, or ask about a ride?'),
    ('greet','yusuf','مَرْحَبًا. مَسَاءُ الْخَيْرِ.'),
    ('clarify','yusuf','هَلْ يُمْكِنُكَ أَنْ تُعِيدَ ذَلِكَ؟'),
]


def _deps():
    path=str(ROOT/'.cache/voice-python')
    if path not in sys.path and Path(path).exists():sys.path.insert(0,path)


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def voice_key(record):
    required=('text','locale','phoneme_version','tts_model','weights_hash','voice_id','speaker_index','speaking_rate','emotion_style','output_format','sample_rate')
    missing=set(required)-record.keys()
    if missing:raise ValueError('cache input missing '+','.join(sorted(missing)))
    return hashlib.sha256(_canonical({k:record[k] for k in required}).encode()).hexdigest()


def validate_utterance(act,text):
    # This bounded planner accepts canonical productions only. Optional paraphrasers
    # must return one of these fully grounded variants, never new entities or facts.
    return any(a==act and exact==text for a,_,exact in PHRASES)


def recognize_intent(text):
    if not isinstance(text,str) or len(text)>2000:raise ValueError('bounded transcript required')
    normalized=re.sub(r'[^\w\s]',' ',text.lower(),flags=re.UNICODE)
    groups={
      'greet':{'hello','hi','hey','مرحبا','أهلا','اهلا'},
      'farewell':{'goodbye','bye','وداعا'},
      'thanks':{'thanks','thank','شكرا'},
      'decline':{'no','decline','لا'},
      'accept':{'yes','sure','نعم'},
      'learn':{'explain','learn','why','اشرح','لماذا'},
    }
    tokens=set(normalized.split()); matches=[act for act,words in groups.items() if tokens & words]
    if len(matches)!=1:return {'status':'clarify','intent':None,'text':text,'reason':'ambiguous-or-outside-utterance-grammar','effects':[]}
    return {'status':'recognized','intent':matches[0],'text':text,'effects':[],'authorization':'intent proposal only; world authority validates before effect'}


def catalog():
    if not CATALOG.exists():return {'version':1,'clips':[],'state':'not-prepared'}
    return json.loads(CATALOG.read_text())


def prepare_voice_catalog(force=False):
    _deps()
    from piper import PiperVoice
    from piper.config import SynthesisConfig, PiperConfig
    import onnxruntime
    out=CATALOG.parent;out.mkdir(parents=True,exist_ok=True)
    existing=catalog(); records={r['cache_key']:r for r in existing.get('clips',[])}
    models={}; loads=[]; clips=[]; source_hashes={}
    for actor,voice in VOICES.items():
        name=voice['model'];path=MODEL_DIR/(name+'.onnx')
        if not path.exists():raise FileNotFoundError('missing downloaded voice '+str(path))
        if name not in source_hashes:source_hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    with _WORKER:
      for act,actor,text in PHRASES:
        if not validate_utterance(act,text):raise ValueError('inadmissible utterance')
        v=VOICES[actor];model=v['model'];config=json.loads((MODEL_DIR/(model+'.onnx.json')).read_text());sr=config['audio']['sample_rate']
        spec={'text':text,'locale':v['locale'],'phoneme_version':hashlib.sha256((MODEL_DIR/(model+'.onnx.json')).read_bytes()).hexdigest(),'tts_model':'piper/'+model,'weights_hash':source_hashes[model],'voice_id':model+':speaker-'+str(v['speaker_index']),'speaker_index':v['speaker_index'],'speaking_rate':1,'emotion_style':'neutral','output_format':'opus','sample_rate':sr}
        key=voice_key(spec);wav_path=out/(key+'.wav');opus_path=out/(key+'.opus')
        old=records.get(key)
        if not force and old and wav_path.exists() and opus_path.exists() and hashlib.sha256(opus_path.read_bytes()).hexdigest()==old['audio_hash']:
            old = {**old, 'speaker_actor': {'amber':'npc:0','river':'npc:1','cedar':'npc:2'}.get(actor,actor), 'speaker_name': actor}
            clips.append(old);continue
        if model not in models:
            started=time.perf_counter()
            options=onnxruntime.SessionOptions();options.intra_op_num_threads=1;options.inter_op_num_threads=1
            models[model]=PiperVoice(config=PiperConfig.from_dict(config),session=onnxruntime.InferenceSession(str(MODEL_DIR/(model+'.onnx')),sess_options=options,providers=['CPUExecutionProvider']))
            loads.append({'model':model,'cold_load_ms':(time.perf_counter()-started)*1000})
        started=time.perf_counter()
        with wave.open(str(wav_path),'wb') as w:
            models[model].synthesize_wav(text,w,syn_config=SynthesisConfig(speaker_id=v['speaker_index']))
        synthesis_ms=(time.perf_counter()-started)*1000
        with wave.open(str(wav_path)) as w:duration=w.getnframes()/w.getframerate();sample_rate=w.getframerate();frames=w.getnframes()
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav_path),'-c:a','libopus','-b:a','48k','-application','voip',str(opus_path)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        if p.returncode:raise RuntimeError(p.stderr)
        data=opus_path.read_bytes()
        clips.append({'id':actor+'-'+act+'-'+key[:8],'kind':'npc_speech','speaker_actor':{'amber':'npc:0','river':'npc:1','cedar':'npc:2'}.get(actor,actor),'speaker_name':actor,'voice_id':spec['voice_id'],'speaker_index':v['speaker_index'],'locale':v['locale'],'semantic_act':act,'canonical_content':act,'utterance_variant_id':key[:16],'source_context_hash':hashlib.sha256(('authored-ambient-v1:'+act).encode()).hexdigest(),'exact_text':text,'text':text,'subtitle':text,'model':'piper/'+model,'model_revision':source_hashes[model],'phoneme_version':spec['phoneme_version'],'cache_key':key,'audio_hash':hashlib.sha256(data).hexdigest(),'path':'/'+str(opus_path.relative_to(ROOT)),'url':'/'+str(opus_path.relative_to(ROOT)),'wav_path':str(wav_path.relative_to(ROOT)),'wav_url':'/'+str(wav_path.relative_to(ROOT)),'codec':'opus','container':'ogg','sample_rate':sample_rate,'duration_ms':round(duration*1000,3),'frames':frames,'bytes':len(data),'synthesis_ms':synthesis_ms,'real_time_factor':synthesis_ms/(duration*1000),'state':'ready','provenance':{'model_source':'https://huggingface.co/rhasspy/piper-voices','license':v['license'],'text':'authored bounded grammatical production; no neural text generator'},'aligned_visemes':None})
    result={'version':1,'clips':clips,'assets':clips,'voices':VOICES,'model_loads':(existing.get('model_loads',[])+loads)[-20:],'source_models':source_hashes,'worker_concurrency':1,'inference_threads':1,'generated_on_startup':False,'preparation_commits_world_events':False,'optional_paraphraser':'disconnected; baseline grammar works without it','limits':['sample perceptual quality requires human listening','Arabic/Jordanian locale is upstream model metadata; accent quality not certified','device decoding/spatial onset measured separately in client','Oracle ARM64 host unavailable in this environment']}
    CATALOG.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    data=ROOT/'data/voice/catalog.json';data.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def ambient_conversation(snapshot,elapsed):
    actors=snapshot.get('actors',{}); clips=catalog().get('clips',[])
    episode=[('amber','greet'),('river','notice'),('cedar','reply'),('amber','offer'),('river','refuse'),('cedar','acknowledge')]
    speeches=[]
    for index,(speaker,act) in enumerate(episode):
        clip=next((c for c in clips if c.get('speaker_name')==speaker and c['semantic_act']==act),None)
        if clip and clip['speaker_actor'] in actors and actors[clip['speaker_actor']].get('available',False):
            speeches.append({'speaker_actor':clip['speaker_actor'],'clip':clip,'world_timestamp':elapsed+index*5.5,'engagement':'independent NPC conversation'})
    return {'speeches':speeches,'requires_player':False,'committed_events':0,'prepared_only':True,'limitation':'world authority schedules actual accepted branch; audio preparation does not make an event true'}


def _recognizer(engine,locale):
    _deps();import sherpa_onnx
    language='ar' if locale.startswith('ar') else 'en'
    key=(engine,language)
    if key in _ASR:return _ASR[key]
    base=ROOT/'data/voice/asr'
    if engine=='moonshine':
        if language!='en':raise ValueError('Moonshine tiny English does not support Arabic')
        p=base/'sherpa-onnx-moonshine-tiny-en-int8'
        r=sherpa_onnx.OfflineRecognizer.from_moonshine(preprocessor=str(p/'preprocess.onnx'),encoder=str(p/'encode.int8.onnx'),uncached_decoder=str(p/'uncached_decode.int8.onnx'),cached_decoder=str(p/'cached_decode.int8.onnx'),tokens=str(p/'tokens.txt'),num_threads=1)
    elif engine=='whisper':
        p=base/'sherpa-onnx-whisper-tiny'
        r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=str(p/'tiny-encoder.int8.onnx'),decoder=str(p/'tiny-decoder.int8.onnx'),tokens=str(p/'tiny-tokens.txt'),language=language,task='transcribe',num_threads=1)
    else:raise ValueError('supported ASR engines: moonshine, whisper')
    _ASR[key]=r;return r


def transcribe_audio(audio_bytes,mime_type='audio/webm',locale='en-US',engine=None):
    if locale not in ('en-US','en','ar-JO','ar'):
        raise ValueError('supported tested locale requests: en-US, ar-JO')
    if not isinstance(audio_bytes,bytes) or not 32<=len(audio_bytes)<=MAX_AUDIO_BYTES:
        raise ValueError('audio payload must be 32 bytes to 5 MiB')
    if mime_type not in ('audio/webm','audio/wav','audio/x-wav','audio/ogg','audio/mp4','audio/mpeg','application/octet-stream'):
        raise ValueError('unsupported audio MIME type')
    engine=engine or ('whisper' if locale.startswith('ar') else 'moonshine')
    if not _WORKER.acquire(timeout=.1):
        return {'status':'busy','text':'','confidence':None,'locale':locale,'engine':'sherpa-onnx/'+engine,'intent':{'status':'clarify','effects':[]}}
    started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix='home-speech-') as td:
        source=Path(td)/'capture';source.write_bytes(audio_bytes);pcm=Path(td)/'capture.wav'
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-i',str(source),'-t',str(MAX_AUDIO_SECONDS+1),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(pcm)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
        if p.returncode:raise ValueError('audio could not be decoded')
        with wave.open(str(pcm)) as w:
            sr=w.getframerate();frames=w.getnframes();data=array('h');data.frombytes(w.readframes(frames))
        if frames>sr*MAX_AUDIO_SECONDS:raise ValueError('audio capture exceeds 15-second budget')
        if sys.byteorder!='little':data.byteswap()
        samples=[x/32768 for x in data]
        loaded=time.perf_counter();recognizer=_recognizer(engine,locale);load_ms=(time.perf_counter()-loaded)*1000
        stream=recognizer.create_stream();stream.accept_waveform(sr,samples);recognizer.decode_stream(stream)
        text=stream.result.text.strip();total_ms=(time.perf_counter()-started)*1000
        rms=math.sqrt(sum(x*x for x in samples)/max(1,len(samples)))
        return {'status':'transcribed' if text else 'clarify','text':text,'confidence':None,'confidence_source':'backend exposes no calibrated confidence; never fabricated','locale':locale,'engine':'sherpa-onnx/'+engine,'duration_ms':1000*frames/sr,'elapsed_ms':total_ms,'model_load_ms':load_ms,'real_time_factor':total_ms/max(1,1000*frames/sr),'signal_rms_dbfs':20*math.log10(max(rms,1e-12)),'intent':recognize_intent(text),'retained_audio':False,'retained_transcript':False}
    finally:_WORKER.release()


def overview():
    c=catalog()
    return {'tts':'Piper ONNX CPU','asr':'sherpa-onnx Moonshine tiny English / Whisper tiny multilingual','catalog':'/artifacts/voice/catalog.json','clips_ready':len(c.get('clips',[])),'voices':list(VOICES),'push_to_talk':True,'max_capture_seconds':MAX_AUDIO_SECONDS,'worker_concurrency':1,'optional_llm_required':False,'oracle_status':'BLOCKED: no connected node/credentials; no existing services modified'}
