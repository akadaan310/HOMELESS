#!/usr/bin/env python3
"""Machine-readable, fail-closed Unreal SDK/GPU/source/map gates."""
import argparse,json,os,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def detect():
    configured=os.environ.get('UE_ROOT');candidates=[pathlib.Path(configured)] if configured else []
    candidates += [pathlib.Path('/opt/UnrealEngine'),pathlib.Path('/opt/unreal-engine'),pathlib.Path.home()/'UnrealEngine']
    sdk=next((p for p in candidates if (p/'Engine/Build/Build.version').exists()),None)
    version=json.loads((sdk/'Engine/Build/Build.version').read_text()) if sdk else None
    gpu=None
    if shutil.which('nvidia-smi'):
        out=subprocess.run(['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader'],capture_output=True,text=True);gpu=out.stdout.strip() if out.returncode==0 else None
    mapfile=ROOT/'unreal/Homeless/Content/WorldLoom/Maps/TampaEntry.umap'
    blockers=[]
    if sdk is None:blockers.append({'code':'UE_SDK_MISSING','detail':'Unreal Engine5.8 SDK not installed. Set UE_ROOT to a licensed installation; acquisition requires Epic account/source access.'})
    elif version.get('MajorVersion')!=5 or version.get('MinorVersion')!=8:blockers.append({'code':'UE_VERSION_MISMATCH','detail':'Expected UE5.8 compatible patch; observed '+json.dumps(version)})
    if not gpu:blockers.append({'code':'GPU_ENCODER_UNAVAILABLE','detail':'No NVIDIA GPU/driver observable via nvidia-smi; rendering/NVENC/WebRTC performance cannot be verified.'})
    if not mapfile.exists():blockers.append({'code':'UE_SCENE_NOT_IMPORTED','detail':'TampaEntry.umap is created by tools/unreal_import.py after source import; it does not exist yet.'})
    plugin=None
    if sdk:
        found=list((sdk/'Engine/Plugins').glob('**/PixelStreaming2.uplugin'));plugin=str(found[0]) if found else None
        if not plugin:blockers.append({'code':'PIXEL_STREAMING2_PLUGIN_MISSING','detail':'SDK does not contain PixelStreaming2.uplugin.'})
    return {'schema':'worldloom.unreal-preflight.v1','ue_root':str(sdk) if sdk else None,'build_version':version,'gpu':gpu,'pixel_streaming2_plugin':plugin,'project':'unreal/Homeless/Homeless.uproject','source_project_present':(ROOT/'unreal/Homeless/Homeless.uproject').is_file(),'imported_map_present':mapfile.exists(),'compiled':False,'cooked':False,'rendered':False,'status':'blocked' if blockers else 'ready-for-build','blockers':blockers}
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(ROOT/'evidence/unreal_preflight.json'));p.add_argument('--allow-blocked',action='store_true');a=p.parse_args();report=detect();path=pathlib.Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0 if a.allow_blocked or not report['blockers'] else 2
if __name__=='__main__':raise SystemExit(main())
