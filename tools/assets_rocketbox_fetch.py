#!/usr/bin/env python3
"""Download selected MIT Rocketbox masters; no replacement art is generated."""
import concurrent.futures,json,pathlib,sys,urllib.parse
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,curl,archive,write_json
tree_path=ASSETS/'discovery/rocketbox-tree.json'
curl('https://api.github.com/repos/microsoft/Microsoft-Rocketbox/git/trees/master?recursive=1',tree_path)
TREE=json.load(open(tree_path))['tree']
BASE='https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/'
OUT=ASSETS/'originals'/'rocketbox'
NAMES=['Male_Adult_01','Male_Adult_05','Female_Adult_03']
FILES=[x['path'] for x in TREE if any(x['path'].startswith('Assets/Avatars/Adults/'+n+'/') for n in NAMES) and x.get('type')=='blob']
ANIMS=['m_walk_neutral_01.max.fbx','m_idle_neutral_01.max.fbx','m_gestic_talk_neutral_01.max.fbx','f_walk_neutral_01.max.fbx','f_idle_neutral_01.max.fbx','f_gestic_talk_neutral_01.max.fbx']
for a in ANIMS:
 matches=[x['path'] for x in TREE if x['path'].endswith('/'+a)]
 if not matches:
  print('animation not present:',a)
 else:FILES.extend(matches)
FILES+=['LICENSE.md','README.md']
def get(path):
 out=OUT/path;url=BASE+urllib.parse.quote(path);curl(url,out);return {**archive(out),'url':url}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:files=list(pool.map(get,FILES))
write_json(OUT/'source-manifest.json',{'canonical_id':'world://collection/microsoft-rocketbox','category':'realistic-rigged-human','license':'MIT','attribution':'Microsoft and Rocketbox contributors; preserve LICENSE.md','source_url':'https://github.com/microsoft/Microsoft-Rocketbox','state':'retrieved','files':files,'selected_characters':NAMES,'animation_sources':ANIMS,'source_claim':'professional authored human library; facial/body textures and authored rigs'})
print(json.dumps({'files':len(files),'bytes':sum(f['bytes'] for f in files),'characters':NAMES}))
