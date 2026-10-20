import json
from gate_kernel import Resource, Gate, BootstrapPlanner, WorldCommitter, voice_key

voice=Resource('speech.en.hello-amber','audio',65000,10,12)
anim=Resource('npc-amber-gesture.glb','animation',84000,7,26)
city=Resource('cafe-exterior-cell.glb','model',110000,8,30)
bill=Resource('street-billboard-program','display',4000,6,3)
scenario=[Gate('overheard-cafe','CONVERSATION_EPISODE',0,14,1.8,12,3,True,(voice,anim,city)),
          Gate('billboard','BILLBOARD_PROGRAM',0,28,1.8,12,3,True,(bill,))]
planner=BootstrapPlanner(260000,80)
plan=planner.plan(scenario,0)
world=WorldCommitter()
before={'world_revision':world.world_revision,'committed_events':len(world.committed)}
# The player walks nearer, explicitly starts a conversation; activation is a separate deliberate step.
confirmed=world.activate(scenario[0],actual_distance_m=2,approved=True,event_id='evt-hello',outcome='npc.speaks')
print(json.dumps({'scenario':'synthetic Tampa café; no real TTS/audio or asset transfer executed',
   'prefetch_plan':plan.__dict__, 'before_activation':before,
   'after_activation':{'world_revision':world.world_revision,'committed_events':len(world.committed)},
   'committed_event_hash':confirmed['hash'],
   'voice_cache_key':voice_key('Welcome back.','en-US','amber','piper-model-r1','en-phonemes-r1')},indent=2))
