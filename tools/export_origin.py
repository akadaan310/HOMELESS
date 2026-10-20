#!/usr/bin/env python3
"""Export witnessed cached projections; never export credentials or private memories."""
import json,pathlib,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from worldloom.session import WorldSession
from worldloom.society import World
from worldloom.protocol import digest,public_projection

def write(name,value):
 p=ROOT/'data/world'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def main():
 with tempfile.TemporaryDirectory() as t:
  w=WorldSession(pathlib.Path(t)/'origin.db');w.world.tick(1)
  event={'version':1,'event_id':'origin-seed-v1','session':'ambient','actor':'simulation','payload':{'kind':'world.snapshot','snapshot':w.world.snapshot(),'operation':'ambient.origin'},'source_revision':'worldloom-v1','parents':[],'world_tick':w.world.world_tick}
  w.store.append(event);s=w.snapshot();s.update(mode='cached-authoritative-snapshot-offline',cached_snapshot_notice='Witnessed server snapshot. Offline motion is local presentation; new authoritative decisions require the world service.',billboard=w.invoke({'operation':'billboard.inspect','payload':{}})['data']);write('origin-snapshot.json',s);w.close()
 w=World(seed=7);episodes=[]
 for i in range(8):
  w.tick(8 if i else 1);snapshot=w.snapshot();episodes.append({'time_seconds':w.time,'conversations':public_projection(snapshot['conversations']),'world_revision':w.revision,'world_snapshot_hash':digest(snapshot),'source':'deterministic witnessed server-world replay; offline presentation only'})
 write('origin-timeline.json',{'mode':'cached-authoritative-replay-offline','episodes':episodes})
 previews=[]
 for text in ['hello','no thanks','teach me','show the report','can i ride','look up','something unclear']:
  w=World(seed=7);r=w.dispatch('speech.act',{'text':text,'npc_id':'npc:0','position':w.actors['npc:0']['position']},actor='offline-preview');previews.append({'input':text,'result':r,'snapshot_hash':digest(World(seed=7).snapshot()),'effect_policy':'projection-only; no world activation','grammar_revision':'finite-discourse-grammar.v1'})
 write('dialogue-previews.json',{'mode':'cached-utterance-preview','previews':previews})
 print('Exported scrubbed origin snapshot, eight conversation episodes and seven cached dialogue previews.')
if __name__=='__main__':main()
