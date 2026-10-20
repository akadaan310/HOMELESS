"""Reproducible procedural stereo assets and bounded spatial cue policy.

Offline WAV fixtures are real rendered samples, not a claim of a rendered UE mix.
Equal-power stereo panning is intentionally not presented as a measured HRTF.
"""
from __future__ import annotations
from array import array
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import wave

SAMPLE_RATE = 24000
ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('engine','traffic','voice','pedestrian','airplane','music','weather')


def synthesize(family, duration=3, seed=7):
    if family not in FAMILIES or not 0<duration<=60:
        raise ValueError('known source family and duration (0,60] required')
    rng=random.Random(seed); n=round(duration*SAMPLE_RATE); result=[]; noise=0; phase=0
    for i in range(n):
        t=i/SAMPLE_RATE; noise=.94*noise+.06*rng.uniform(-1,1)
        if family=='engine':
            phase+=2*math.pi*(45+12*math.sin(1.2*t))/SAMPLE_RATE
            x=.3*math.sin(phase)+.12*math.sin(2*phase)+.06*math.sin(4*phase)
        elif family=='traffic':
            x=.3*noise+.1*math.sin(2*math.pi*73*t); x*=.3+.7*math.sin(math.pi*t/duration)**2
        elif family=='pedestrian':
            elapsed=t%.5
            x=.8*math.sin(2*math.pi*110*elapsed)*math.exp(-40*elapsed)*(1-math.exp(-300*elapsed))
        elif family=='airplane':
            x=.2*math.sin(2*math.pi*(90*t+12*math.sin(.6*t)))+.6*noise
        elif family=='music':
            x=sum(.10*math.sin(2*math.pi*f*t) for f in (261.625565,329.627557,391.995436))
        elif family=='weather':
            x=.7*noise+.025*rng.uniform(-1,1)
        else:
            # Diagnostic formant-like voice used only when actual TTS unavailable.
            x=.1*math.sin(2*math.pi*130*t)*(1+.3*math.sin(2*math.pi*620*t))
        fade=min(1,i/(.035*SAMPLE_RATE),(n-1-i)/(.035*SAMPLE_RATE))
        result.append(x*math.sin(max(0,fade)*math.pi/2)**2)
    return result


def spatialize(mono, azimuth=0, distance=1, occlusion=0):
    if not all(math.isfinite(x) for x in (azimuth,distance,occlusion)) or distance<0 or not 0<=occlusion<=1:
        raise ValueError('finite azimuth, nonnegative distance, occlusion [0,1] required')
    pan=math.sin(math.radians(max(-90,min(90,azimuth))))
    gains=(math.sqrt((1-pan)/2), math.sqrt((1+pan)/2))
    gain=1/(1+distance/10)*(1-.65*occlusion)
    alpha=1 if not occlusion else 1-math.exp(-2*math.pi*(12000-11200*occlusion)/SAMPLE_RATE)
    filtered=0; left=[]; right=[]
    for x in mono:
        filtered+=alpha*(x-filtered)
        left.append(filtered*gain*gains[0]); right.append(filtered*gain*gains[1])
    return left,right


def write_wav(path,left,right):
    data=array('h')
    for l,r in zip(left,right):
        data.extend((round(max(-1,min(1,l))*32767), round(max(-1,min(1,r))*32767)))
    import sys
    if sys.byteorder!='little': data.byteswap()
    with wave.open(str(path),'wb') as w:
        w.setparams((2,2,SAMPLE_RATE,0,'NONE','not compressed')); w.writeframes(data.tobytes())


def _actual_speech(duration):
    # Prefer generated neural catalog audio; eSpeak is marked diagnostic fallback.
    catalog=ROOT/'data/voice/catalog.json'
    if catalog.exists():
        c=json.loads(catalog.read_text())
        for record in c.get('assets',[]):
            path=ROOT/record.get('wav_path','')
            if path.is_file():
                return _read_resample(path,duration), {'kind':'neural-tts','model':record.get('model'),'source':str(path.relative_to(ROOT))}
    executable=shutil.which('espeak-ng') or shutil.which('espeak')
    sysroot=ROOT/'.cache/sysroot/usr'
    if not executable and (sysroot/'bin/espeak-ng').exists(): executable=str(sysroot/'bin/espeak-ng')
    if executable:
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'voice.wav'; cmd=[executable]
            env=None
            if '.cache/sysroot' in executable:
                import os
                env=dict(os.environ,LD_LIBRARY_PATH=str(sysroot/'lib/x86_64-linux-gnu'));cmd+=['--path='+str(sysroot/'lib/x86_64-linux-gnu')]
            cmd+=['-s','155','-w',str(path),'The light changed. I will meet you by the harbor.']
            proc=subprocess.run(cmd,capture_output=True,text=True,timeout=20,env=env)
            if proc.returncode==0 and path.exists():
                return _read_resample(path,duration), {'kind':'diagnostic-tts','model':'eSpeak NG','limitation':'diagnostic fallback, not cinematic release voice'}
    return synthesize('voice',duration), {'kind':'procedural-diagnostic','limitation':'actual speech unavailable; not an intelligible dialogue asset'}


def _read_resample(path,duration):
    with wave.open(str(path)) as w:
        frames=w.getnframes(); sr=w.getframerate(); channels=w.getnchannels(); width=w.getsampwidth()
        if width!=2: raise ValueError('16-bit PCM speech required')
        raw=array('h'); raw.frombytes(w.readframes(frames)); mono=[sum(raw[i:i+channels])/(channels*32768) for i in range(0,len(raw),channels)]
    n=round(duration*SAMPLE_RATE); out=[]
    peak=max([1e-9]+[abs(v) for v in mono])
    for i in range(n):
        pos=i*sr/SAMPLE_RATE; j=int(pos)
        x=0 if j>=len(mono)-1 else (mono[j]*(1-(pos-j))+mono[j+1]*(pos-j))*.5/peak
        fade=min(1,i/(.035*SAMPLE_RATE),(n-1-i)/(.035*SAMPLE_RATE))
        out.append(x*math.sin(max(0,fade)*math.pi/2)**2)
    return out


def cue_policy(events, enabled=True, cooldown=30, salience_cap=.35):
    emitted=[]; suppressed=[]; ignored=set(); last={}
    for e in sorted(events,key=lambda x:x['time']):
        eid=e['event_id']; now=float(e['time'])
        if e.get('response') in ('ignore','dismiss','mute','decline'):
            ignored.add(eid)
        reason='disabled' if not enabled else 'declined-or-ignored' if eid in ignored else 'cooldown' if now-last.get(eid,-1e100)<cooldown else None
        if reason: suppressed.append({**e,'reason':reason}); continue
        emitted.append({**e,'salience':min(salience_cap,max(0,e.get('salience',.2))), 'source_exists_independently':True});last[eid]=now
    return {'emitted':emitted,'suppressed':suppressed,'response_state':sorted(ignored)}


def render_soundscape(output_dir='artifacts/audio', duration=10):
    if not 1<=duration<=60: raise ValueError('duration [1,60]')
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);n=round(duration*SAMPLE_RATE)
    left=[0.0]*n;right=[0.0]*n;sources={};events=[]
    for idx,family in enumerate(FAMILIES):
        start=.03+idx*.137;start_sample=round(start*SAMPLE_RATE)
        source_duration=duration-start
        if family=='voice': mono,provenance=_actual_speech(source_duration)
        else: mono=synthesize(family,source_duration,11+idx);provenance={'kind':'procedural','generator':'worldloom.audio.synthesize/v1','seed':11+idx}
        azimuth=-70+idx*140/6;distance=4+idx*2
        l,r=spatialize(mono,azimuth,distance,.15 if family=='traffic' else 0)
        write_wav(out/(family+'.wav'),l,r)
        for i,(lv,rv) in enumerate(zip(l,r)):
            if i+start_sample<n:left[i+start_sample]+=lv;right[i+start_sample]+=rv
        raw=(out/(family+'.wav')).read_bytes()
        sources[family]={'file':family+'.wav','url':'/artifacts/audio/'+family+'.wav','azimuth_deg':azimuth,'distance_m':distance,'onset_s':start,'sample_index':start_sample,'provenance':provenance,'sha256':hashlib.sha256(raw).hexdigest()}
        events.append({'source':family,'requested_s':start,'sample_index':start_sample,'error_samples':abs(start*SAMPLE_RATE-start_sample),'buffer_size':512,'buffer_dispatch_lateness_samples':math.ceil(start_sample/512)*512-start_sample})
    peak=max(max(abs(v) for v in left),max(abs(v) for v in right));gain=min(1,.85/max(peak,1e-12))
    left=[v*gain for v in left];right=[v*gain for v in right]
    write_wav(out/'world_mix.wav',left,right)
    deltas=[abs(x-y) for channel in (left,right) for x,y in zip(channel[1:],channel)]
    energy=sum(v*v for c in (left,right) for v in c)/(2*n)
    corr=sum(l*r for l,r in zip(left,right))/max(1e-12,math.sqrt(sum(v*v for v in left)*sum(v*v for v in right)))
    metrics={'sample_peak':peak*gain,'sample_peak_dbfs':20*math.log10(max(peak*gain,1e-12)),'rms_dbfs':10*math.log10(max(energy,1e-12)),'max_adjacent_sample_delta':max(deltas),'heavy_click_count':sum(v>.15 for v in deltas),'heavy_click_threshold':.15,'stereo_correlation':corr,'event_error_max_samples':max(e['error_samples'] for e in events),'buffer_dispatch_max_samples':max(e['buffer_dispatch_lateness_samples'] for e in events),'master_gain':gain}
    manifest={'version':1,'sample_rate':SAMPLE_RATE,'channels':2,'format':'PCM16 WAV','duration_s':duration,'sources':sources,'events':events,'metrics':metrics,'mix_sha256':hashlib.sha256((out/'world_mix.wav').read_bytes()).hexdigest(),'limits':['offline synthetic stereo fixture; no rendered Unreal/MetaSound mix','equal-power panning, no HRTF localization measurement','RMS/sample-peak measured; LUFS/true peak and human intelligibility not certified','buffer dispatch is a simulated 512-sample scheduler, not device dropout measurement']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def overview():
    return {'sources':list(FAMILIES),'sample_rate':SAMPLE_RATE,'channels':2,'operations':['render','cue-policy','spatialize'],'audio_manifest':'artifacts/audio/manifest.json','voice_catalog':'data/voice/catalog.json','runtime':'offline PCM fixtures + client spatial playback'}


def crossfade(street,car,overlap_samples):
    """Equal-power domain transition; caller applies changing source occlusion separately."""
    count=int(overlap_samples)
    if not 2<=count<=min(len(street),len(car)):
        raise ValueError('overlap must fit both buffers and have at least 2 samples')
    result=list(street[:-count])
    for i in range(count):
        phase=i/(count-1)*math.pi/2
        result.append(street[-count+i]*math.cos(phase)+car[i]*math.sin(phase))
    return result+list(car[count:])


def loop_metrics(mono,window=1024):
    if not mono:raise ValueError('nonempty signal required')
    count=min(int(window),len(mono)//2)
    if count<2:raise ValueError('loop correlation needs at least 4 samples')
    head,tail=mono[:count],mono[-count:]
    norm=math.sqrt(sum(v*v for v in head)*sum(v*v for v in tail))
    return {'boundary_sample_jump':abs(mono[-1]-mono[0]),'boundary_correlation':sum(a*b for a,b in zip(head,tail))/max(norm,1e-15),'window_samples':count,'limitation':'correlation at declared segment alignment; no perceptual seamless-loop claim'}
