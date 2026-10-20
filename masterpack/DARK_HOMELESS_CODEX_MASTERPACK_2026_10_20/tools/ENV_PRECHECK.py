"""Inspect build prerequisites; read-only and portable. Does not attempt installation."""
import json,os,pathlib,platform,shutil,subprocess
commands={'python':'python','node':'node','git':'git','clang++':'clang++','cmake':'cmake','cmake3':'cmake3','adb':'adb','gradle':'gradle','java':'java','octave':'octave','quickjs':'qjs','wasmtime':'wasmtime','ffmpeg':'ffmpeg','ninja':'ninja','unreal_editor':'UnrealEditor'}
report={'host':platform.platform(),'cpu':platform.processor(),'commands':{k:shutil.which(v) for k,v in commands.items()},'env':{k:bool(os.environ.get(k)) for k in ['ANDROID_HOME','ANDROID_SDK_ROOT','UE_ROOT','JAVA_HOME','CUDA_PATH']}, 'gpu':{'nvidia_smi':shutil.which('nvidia-smi')}}
if shutil.which('nvidia-smi'):
    try:report['gpu']['detail']=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],text=True,timeout=3).strip()
    except Exception as e:report['gpu']['detail_error']=type(e).__name__
print(json.dumps(report,indent=2))
