#!/usr/bin/env python3
"""Actual CPU TTS/ASR benchmark; synthetic tests are labeled, not human WER claims."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from worldloom import voice as v
from worldloom.audio import synthesize
import hashlib,json,math,platform,re,resource,statistics,time,unicodedata,wave
from array import array


def tokens(s):
    s=''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
    return re.sub(r'[^\w\s]',' ',s).split()


def wer(reference,hypothesis):
    a,b=tokens(reference),tokens(hypothesis);row=list(range(len(b)+1))
    for i,x in enumerate(a):
        nxt=[i+1]
        for j,y in enumerate(b):nxt.append(min(nxt[j]+1,row[j+1]+1,row[j]+(x!=y)))
        row=nxt
    return row[-1]/max(1,len(a))


def run():
    c=v.catalog();results=[];start=time.perf_counter()
    fixture=v.ROOT/'data/voice/asr/sherpa-onnx-moonshine-tiny-en-int8/test_wavs/0.wav'
    reference='AFTER EARLY NIGHTFALL THE YELLOW LAMPS WOULD LIGHT UP HERE AND THERE THE SQUALID QUARTER OF THE BROTHELS'
    english=next(x for x in c['clips'] if x['semantic_act']=='greet' and x['text'].startswith('Hello.'))
    arabic=next(x for x in c['clips'] if x['locale']=='ar-JO')
    tests=[('moonshine','bundled-read-speech',fixture,reference,'en-US'),('moonshine','synthesized-NPC-clean',v.ROOT/english['wav_path'],english['text'],'en-US'),('whisper','bundled-read-speech',fixture,reference,'en-US'),('whisper','synthesized-NPC-clean',v.ROOT/english['wav_path'],english['text'],'en-US'),('whisper','synthesized-Arabic-Jordanian',v.ROOT/arabic['wav_path'],arabic['text'],'ar-JO')]
    noise_path=v.ROOT/'artifacts/voice/asr_noisy_10db.wav'
    with wave.open(str(v.ROOT/english['wav_path'])) as w:
        sr=w.getframerate();audio=array('h');audio.frombytes(w.readframes(w.getnframes()))
    # Deterministic traffic generator, RMS scaled to exactly 10dB source SNR.
    import random
    rng=random.Random(42);noise=[rng.gauss(0,1) for _ in audio]
    rms=math.sqrt(sum((x/32768)**2 for x in audio)/len(audio));nrms=math.sqrt(sum(x*x for x in noise)/len(noise));scale=rms/(10**(.5)*nrms)
    mixed=array('h',(round(max(-1,min(1,x/32768+scale*z))*32767) for x,z in zip(audio,noise)))
    with wave.open(str(noise_path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(mixed.tobytes())
    tests.append(('moonshine','synthesized-NPC-10dB-white-noise',noise_path,english['text'],'en-US'))
    for engine,kind,path,expected,locale in tests:
        record={'fixture':str(path.relative_to(v.ROOT)),'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'kind':kind,'reference_text':expected,'locale':locale,'engine':engine}
        try:
            got=v.transcribe_audio(path.read_bytes(),mime_type='audio/wav',locale=locale,engine=engine)
            record.update({'observed':got,'word_error_rate':wer(expected,got['text']),'status':'executed'})
        except Exception as e:record.update({'status':'failed','error':type(e).__name__+': '+str(e)})
        results.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
    clips=c['clips'];lat=[x['synthesis_ms'] for x in clips];rtf=[x['real_time_factor'] for x in clips]
    # Verify exact-byte cache reuse without model load or new audio writes.
    before={x['path']:(v.ROOT/x['path'].lstrip('/')).stat().st_mtime_ns for x in clips}
    began=time.perf_counter();cached=v.prepare_voice_catalog();cache_ms=(time.perf_counter()-began)*1000
    reused=sum(before.get(x['path'])==(v.ROOT/x['path'].lstrip('/')).stat().st_mtime_ns for x in cached['clips'])
    report={'environment':{'machine':platform.machine(),'platform':platform.platform(),'cpu_count':__import__('os').cpu_count(),'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},'tts':{'clips':len(clips),'voices':len({x['voice_id'] for x in clips}),'encoded_bytes':sum(x['bytes'] for x in clips),'duration_ms':sum(x['duration_ms'] for x in clips),'synthesis_p50_ms':statistics.median(lat),'synthesis_p95_ms':sorted(lat)[int(.95*(len(lat)-1))],'real_time_factor_p50':statistics.median(rtf),'model_loads':c['model_loads'],'cache_repeat_elapsed_ms':cache_ms,'cache_reused_clips':reused,'cache_hit_fraction':reused/len(clips)},'asr':results,'elapsed_s':time.perf_counter()-start,'blockers':{'Oracle2vCPU_ARM64':'not connected; no resource/service-health or concurrency1vs2 claims','physical_microphone':'no physical microphone/Samsung hardware in container','Arabic_human_accuracy':'only synthesized Arabic candidate tested; dialect/noise/native-speaker corpus untested','human_audition':'no human listening scores captured','latency_target':'device cached-onset p95<250ms must be tested by client audio traces'},'limitations':['small scripted sample set; no population-level ASR accuracy conclusion','backend has no calibrated confidence; confidence null is explicit','cold model load included in elapsed times; warm and cold distinguished by model_load_ms','white-noise stress fixture is synthetic and not a validated live traffic recording']}
    path=v.ROOT/'evidence/voice_benchmarks.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


if __name__=='__main__':run()
