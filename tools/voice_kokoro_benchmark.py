#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from worldloom.voice import ROOT,_deps
_deps()
import hashlib,json,platform,resource,time,wave
from array import array
from kokoro_onnx import Kokoro

base=ROOT/'data/voice/kokoro';out=ROOT/'artifacts/voice';records=[]
try:
 t=time.perf_counter();m=Kokoro(str(base/'kokoro-v1.0.int8.onnx'),str(base/'voices-v1.0.bin'));cold=(time.perf_counter()-t)*1000
 for i,text in enumerate(['Good evening. The street is quiet.','Would you like to walk with us?']):
  start=time.perf_counter();samples,sr=m.create(text,voice='af_heart',speed=1,lang='en-us');elapsed=(time.perf_counter()-start)*1000
  path=out/('kokoro_evaluation_'+str(i)+'.wav');pcm=array('h',(round(max(-1,min(1,float(x)))*32767) for x in samples))
  with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
  duration=len(samples)/sr
  records.append({'text':text,'voice':'af_heart','file':str(path.relative_to(ROOT)),'sample_rate':sr,'duration_ms':duration*1000,'elapsed_ms':elapsed,'real_time_factor':elapsed/(duration*1000),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 report={'status':'executed','model':'kokoro-v1.0.int8.onnx','weights_sha256':hashlib.sha256((base/'kokoro-v1.0.int8.onnx').read_bytes()).hexdigest(),'voices_sha256':hashlib.sha256((base/'voices-v1.0.bin').read_bytes()).hexdigest(),'source':'https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0','cold_load_ms':cold,'records':records,'environment':platform.platform(),'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limitations':['CPU x86 container; not reported Oracle ARM64','two synthetic evaluation lines; human audio quality ranking not measured','Arabic not included in this English contender test']}
except Exception as e:report={'status':'failed','error':type(e).__name__+': '+str(e),'records':records}
(ROOT/'evidence/voice_kokoro_benchmarks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
