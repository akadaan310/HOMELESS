"""General predictive media gates, separated from authoritative world activation.

The deterministic greedy scheduler is deliberately not claimed optimal. Preparing
verified media changes only a cache. activate() emits an authorized proposal;
WorldSession owns the actual event commit and deduplication.
"""
from __future__ import annotations

import copy
import hashlib
import math

from .grammar import digest

KINDS={'NPC_LINE','CONVERSATION_EPISODE','WHISPERED_HINT','EVENT_SCENE','MISSION_OPPORTUNITY','RENDEZVOUS_HAVEN',
       'BILLBOARD_PROGRAM','MUSIC_CUE','VEHICLE_ENTRY','AIRCRAFT_APPROACH','ASSET_CELL','PORTAL_CORRESPONDENCE','WEATHER_FIELD','SHELL_VISUAL'}


class BootstrapScheduler:
    def __init__(self,byte_budget=8*1024*1024,memory_budget=24*1024*1024,decode_budget_ms=100):
        if min(byte_budget,memory_budget,decode_budget_ms)<0:raise ValueError('nonnegative budgets required')
        self.byte_budget=byte_budget;self.memory_budget=memory_budget;self.decode_budget_ms=decode_budget_ms
        self.gates={};self.resources={};self.cache={};self.trace=[];self.last_plan=None

    def _log(self,kind,identifier,**details):
        self.trace.append({'kind':kind,'id':identifier,**details})
        self.trace=self.trace[-512:]

    def plan(self,snapshot,candidates,resources,now=0):
        if not math.isfinite(now) or now<0:raise ValueError('finite nonnegative clock required')
        if len(candidates)>256 or len(resources)>1024:raise ValueError('planning input budget exceeded')
        revision=snapshot.get('revision',snapshot.get('world_revision',0))
        pool={}
        for raw in resources:
            r=copy.deepcopy(raw)
            for key in ('id','kind','bytes','hash'):
                if key not in r:raise ValueError('incomplete resource declaration: '+key)
            if not isinstance(r['id'],str) or not r['id'] or not isinstance(r['hash'],str) or len(r['hash'])!=64:raise ValueError('invalid resource identity/hash')
            for key,default in [('bytes',0),('memory_bytes',r['bytes']),('decode_ms',0)]:
                value=r.setdefault(key,default)
                if not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:raise ValueError('invalid resource cost')
            if r['id'] in pool and pool[r['id']]!=r:raise ValueError('resource declaration conflict')
            pool[r['id']]=r
        if len({g['id'] for g in candidates})!=len(candidates):raise ValueError('duplicate gate IDs')
        eligible={};rejected={};rank={};low=snapshot.get('battery',1)<=.03
        for candidate in sorted(candidates,key=lambda g:g['id']):
            g=copy.deepcopy(candidate);identifier=g['id']
            if g.get('kind') not in KINDS:raise ValueError('unknown typed gate kind')
            nums={k:float(g.get(k,default)) for k,default in [('distance_m',0),('speed_mps',0),('horizonSeconds',15),('activation_radius_m',3),('expiry',now+30)]}
            if any(not math.isfinite(x) or x<0 for x in nums.values()):raise ValueError('invalid gate geometry/time')
            distance=nums['distance_m'];speed=nums['speed_mps'];horizon=nums['horizonSeconds']
            eta=distance/max(speed,.05) if speed>.05 else (0 if distance<=nums['activation_radius_m'] else None)
            reason=None
            if g.get('candidateStateRevision')!=revision:reason='stale-state-revision'
            elif not g.get('admitted',False):reason='grammar-refused'
            elif not g.get('navigation_feasible',True):reason='path-infeasible'
            elif nums['expiry']<=now:reason='expired'
            elif low and g.get('priority','B')!='A':reason='low-battery-lookahead'
            elif not snapshot.get('network_available',True) and g.get('priority','B')=='C':reason='offline-lookahead'
            elif eta is None and not g.get('scheduled_anticipation',False):reason='stationary-without-anticipation'
            elif eta is not None and eta+float(g.get('pause_seconds',0))+float(g.get('stale_penalty_seconds',0))>horizon:reason='outside-horizon'
            elif any(r not in pool for r in g.get('resourceSet',[])):reason='unresolved-resource'
            elif not g.get('public_information',True):reason='observer-scope-refused'
            if reason:
                rejected[identifier]=reason;continue
            g.update({'state':'STAGE','eta_seconds':eta,'candidateStateRevision':revision,'effectPolicy':'prepare-only',
                      'evaluationTrace':['OBSERVE','PREDICT','ADMIT','STAGE'],'expiry':nums['expiry']})
            g['checksum']=digest({k:v for k,v in g.items() if k!='checksum'})
            eligible[identifier]=g
            band={'A':3,'B':2,'C':1}.get(g.get('priority','B'),2)
            score=(band, float(g.get('utility',1))*float(g.get('need',1)), -(eta if eta is not None else horizon))
            for rid in g.get('resourceSet',[]):rank[rid]=max(rank.get(rid,(0,0,0)),score)
        # Deduplicate shared bytes and select under all three independent budgets.
        selected=[];used_bytes=used_memory=used_decode=0
        for rid in sorted(rank,key=lambda r:(tuple(-n for n in rank[r]),pool[r]['bytes'],r)):
            r=pool[rid]
            if (used_bytes+r['bytes']<=self.byte_budget and used_memory+r['memory_bytes']<=self.memory_budget and used_decode+r['decode_ms']<=self.decode_budget_ms):
                selected.append(rid);used_bytes+=r['bytes'];used_memory+=r['memory_bytes'];used_decode+=r['decode_ms']
        canceled=sorted(k for k,g in self.gates.items() if k not in eligible and g.get('state') not in ('CANCEL','EXPIRE','RETIRE'))
        for identifier in canceled:self.cancel(identifier,rejected.get(identifier,'prediction-changed'))
        for identifier,g in eligible.items():
            old=self.gates.get(identifier)
            if old and old.get('state')=='RETIRE':g['state']='RETIRE'
            g['selected_resources']=[r for r in g.get('resourceSet',[]) if r in selected]
            if g.get('state')!='RETIRE' and set(g.get('resourceSet',[]))<=set(self.cache):g['state']='RESERVE'
            if old is None or old.get('checksum')!=g['checksum']:self._log('predicted',identifier,revision=revision)
            self.gates[identifier]=g
        self.resources.update(pool)
        # Replace declarations of changed resources only after validation; a stale
        # byte cache cannot satisfy a changed checksum merely by sharing an ID.
        for rid in list(self.cache):
            if rid in pool and hashlib.sha256(self.cache[rid]).hexdigest()!=pool[rid]['hash']:del self.cache[rid]
        for g in self.gates.values():
            if g['state']=='RESERVE' and not set(g.get('resourceSet',[]))<=set(self.cache):g['state']='STAGE'
        body={'revision':revision,'staged':selected,'resources':[pool[r] for r in selected],
              'staged_bytes':used_bytes,'memory_bytes':used_memory,'decode_ms':used_decode,
              'eligible_gates':sorted(eligible),'rejected':rejected,'canceled':canceled,'effects_committed':[],
              'effect_policy':'prepare-only','solver':'deterministic-greedy-priority.v1','globally_optimal':False,
              'budgets':{'bytes':self.byte_budget,'memory_bytes':self.memory_budget,'decode_ms':self.decode_budget_ms}}
        body['plan_id']=digest(body);self.last_plan=copy.deepcopy(body)
        return body

    def prepare(self,resource_id,content):
        if resource_id not in self.resources:raise ValueError('unresolved resource')
        r=self.resources[resource_id]
        if not isinstance(content,bytes) or len(content)!=r['bytes'] or hashlib.sha256(content).hexdigest()!=r['hash']:raise ValueError('resource bytes/hash mismatch')
        if self.last_plan is None or resource_id not in self.last_plan['staged']:raise PermissionError('resource not selected under current budget')
        required=sum(self.resources[k]['memory_bytes'] for k in self.cache if k!=resource_id)+r['memory_bytes']
        if required>self.memory_budget:raise MemoryError('resident memory budget exceeded; evict first')
        hit=resource_id in self.cache;self.cache[resource_id]=content
        self._log('fetched',resource_id,cache_hit=hit,bytes=len(content),hash=r['hash'])
        for g in self.gates.values():
            if g['state']=='STAGE' and set(g['resourceSet'])<=set(self.cache):
                g['state']='RESERVE';g['evaluationTrace']+=['VERIFY','RESERVE']
        return {'resource_id':resource_id,'state':'ready','cache_hit':hit,'hash':r['hash'],'effects_committed':[]}

    def activate(self,gate_id,snapshot,*,actual_distance_m,authority=(),consent=True,now=0):
        g=self.gates[gate_id]
        if g['state']!='RESERVE' or not consent or not g.get('admitted') or not math.isfinite(actual_distance_m) or not 0<=actual_distance_m<=g.get('activation_radius_m',3):raise PermissionError('activation requires verified resources, consent and actual proximity')
        if g.get('authority','scene.activate') not in authority:raise PermissionError('typed activation capability required')
        if snapshot.get('revision',0)!=g['candidateStateRevision']:raise ValueError('stale activation state')
        if now>=g['expiry']:raise PermissionError('expired activation')
        proposal={'gate_id':gate_id,'expected_revision':g['candidateStateRevision'],'effect':copy.deepcopy(g.get('effect',{'kind':g['kind']})),
                  'effect_policy':'propose-only','resource_hashes':{r:self.resources[r]['hash'] for r in g['resourceSet']},
                  'witness':{'checksum':g['checksum'],'actual_distance_m':actual_distance_m,'consent':consent}}
        proposal['event_id']='gate:'+digest(proposal)
        self._log('activation-proposed',gate_id,event_id=proposal['event_id'])
        return proposal

    def played(self,gate_id,clip_id):
        if self.gates[gate_id]['state']!='RESERVE':raise PermissionError('unreserved playback')
        if clip_id not in self.gates[gate_id]['resourceSet']:raise ValueError('clip not in gate manifest')
        self._log('played',clip_id,gate_id=gate_id)
        return {'clip_id':clip_id,'gate_id':gate_id,'state':'played'}

    def cancel(self,gate_id,reason='ignored'):
        g=self.gates.get(gate_id)
        if g:g['state']='EXPIRE' if reason=='expired' else 'CANCEL'
        self._log('ignored' if reason=='ignored' else 'canceled',gate_id,reason=reason)
        return {'gate_id':gate_id,'state':g['state'] if g else 'CANCEL','reason':reason,'effects_committed':[]}

    def retire(self,gate_id):
        self.gates[gate_id]['state']='RETIRE';self._log('retired',gate_id)

    def evict(self,target_bytes):
        if target_bytes<0:raise ValueError('negative eviction target')
        evicted=[]
        for rid in sorted(self.cache):
            if sum(len(v) for v in self.cache.values())<=target_bytes:break
            del self.cache[rid];evicted.append(rid)
        for g in self.gates.values():
            if g['state']=='RESERVE' and not set(g['resourceSet'])<=set(self.cache):g['state']='STAGE'
        return evicted

    def status(self):
        return {'gates':copy.deepcopy(self.gates),'cache_bytes':sum(len(v) for v in self.cache.values()),
                'memory_bytes':sum(self.resources[k]['memory_bytes'] for k in self.cache),
                'cache_hashes':{k:self.resources[k]['hash'] for k in self.cache},'trace':copy.deepcopy(self.trace),
                'effects_committed':[]}
