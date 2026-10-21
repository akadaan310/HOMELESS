#!/usr/bin/env python3
"""Portable integrity checks, deliberately NOT Unity compilation or gameplay acceptance."""
import hashlib,json,pathlib,struct,wave
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'Packages/manifest.json').read_text())
    assert manifest['dependencies']['com.unity.render-pipelines.universal']=='17.0.4'
    guids={}
    for meta in (ROOT/'Assets').rglob('*.meta'):
        guid=next(line[6:] for line in meta.read_text().splitlines() if line.startswith('guid: '))
        assert len(guid)==32 and guid not in guids,meta
        guids[guid]=str(meta)
    scene=(ROOT/'Assets/Scenes/StreetFixture.unity').read_text()
    for guid in ['43c393d374ac02de5b5686be919e4911','573eb56c2f51e0bd6d7d1f3d22b716f7']:
        assert guid in scene and guid in guids
    records=json.loads((ROOT/'Evidence/audio-manifest.json').read_text())['assets']
    for record in records:
        path=ROOT/record['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
        with wave.open(str(path)) as wav:
            assert wav.getnchannels()==1 and wav.getsampwidth()==2 and wav.getframerate()==24000
            assert wav.getnframes()==record['frames']
            pcm=wav.readframes(wav.getnframes());values=struct.unpack('<'+'h'*(len(pcm)//2),pcm)
            assert max(map(abs,values))<32767 and any(values)
    print(json.dumps({'status':'PASS','scope':'portable file and WAV integrity only','audio_assets':len(records),'unique_meta_guids':len(guids),'unity_compile':'NOT_RUN','native_gameplay':'NOT_RUN'},indent=2))

if __name__=='__main__':main()
