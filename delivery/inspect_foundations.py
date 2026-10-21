#!/usr/bin/env python3
"""HD-004/008/009/034/048/079/080: read-only, no archive code execution."""
import argparse, datetime, hashlib, io, json, os, pathlib, platform, shutil, subprocess, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(data): return hashlib.sha256(data).hexdigest()
def cmd(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=10)
        return {'exit_code':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}
    except (OSError,subprocess.TimeoutExpired) as e: return {'unavailable':type(e).__name__}
def archive(data, label, depth=0):
    if len(data)>256*1024*1024: raise ValueError('archive byte budget exceeded')
    records=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        infos=z.infolist()
        if len(infos)>100000 or sum(i.file_size for i in infos)>512*1024*1024: raise ValueError('expanded budget exceeded')
        for i in infos:
            if i.is_dir(): continue
            name=pathlib.PurePosixPath(i.filename)
            safe=not name.is_absolute() and '..' not in name.parts
            b=z.read(i)
            r={'path':i.filename,'bytes':len(b),'sha256':digest(b),'safe_relative_path':safe}
            if i.filename.lower().endswith('.zip') and depth<2: r['archive']=archive(b,label+'!'+i.filename,depth+1)
            records.append(r)
    return {'source':label,'sha256':digest(data),'bytes':len(data),'members':records}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=pathlib.Path,default=pathlib.Path('/home/ubuntu/homeless/masterpack/masterpack.zip'));ap.add_argument('--output',type=pathlib.Path,default=ROOT/'delivery/inventory.json');a=ap.parse_args()
    mem={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines()) if k in ('MemTotal','MemAvailable','SwapTotal')}
    disk=shutil.disk_usage(ROOT)
    tools={t:shutil.which(t) for t in ['Unity','unity','unity-editor','java','javac','adb','sdkmanager','dotnet','octave','julia','python3','node','docker','nvidia-smi']}
    candidates=[pathlib.Path(p) for p in ['/opt/Unity','/opt/unity','/home/ubuntu/Unity','/home/ubuntu/Android/Sdk','/opt/android-sdk','/usr/lib/jvm','/dev/dri','/dev/bus/usb']]
    report={'schema':'dark.delivery.inventory.v1','commission_revision':'1.1','commission_sha256':digest((ROOT/'HOMELESS_DARK_CONSTITUTIONAL_COMMISSION.md').read_bytes()),'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'git_head':cmd(['git','rev-parse','HEAD']),'branch':cmd(['git','branch','--show-current']),'host':{'architecture':platform.machine(),'os_release':pathlib.Path('/etc/os-release').read_text(),'cpu_count':os.cpu_count(),'cpu':cmd(['lscpu']),'memory_bytes':mem,'disk_bytes':dict(zip(['total','used','free'],disk)),'tools':tools,'paths_exist':{str(p):p.exists() for p in candidates},'environment_presence_only':{k:bool(os.environ.get(k)) for k in ['ANDROID_HOME','ANDROID_SDK_ROOT','JAVA_HOME','UNITY_LICENSE','UNITY_SERIAL','DISPLAY','WAYLAND_DISPLAY']},'network':'Tool network enabled; external connectivity/service entitlements not established by this inventory.','credentials':'Values deliberately not inspected or emitted. Unity Build Automation entitlement, repository integration and spending authority unverified.'},'foundation':archive(a.archive.read_bytes(),str(a.archive)),'native_status':{'status':'BLOCKED','reason':'No Unity Editor or Android toolchain on PATH or inspected standard locations; ARM host, no inspected GPU or attached Android device. No supported build worker entitlement established.','release_acceptance':False}}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'output':str(a.output),'commission_sha256':report['commission_sha256'],'archive_sha256':report['foundation']['sha256'],'archive_members':len(report['foundation']['members']),'native_status':report['native_status']},indent=2))
if __name__=='__main__': main()
