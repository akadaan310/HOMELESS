"""Renderer-neutral, deterministic synthetic society with sparse actor activation.

This is a symbolic reference simulation, not eight billion continuously ticking
people. Founder identity is metadata; privileges are supplied by authenticated
WorldSession capability checks, never inferred from a display name.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import math
import json
import sys
from datetime import datetime, timezone, timedelta
from functools import lru_cache

from .grammar import ROOT, Grammatical, compile_program, digest, registry

CAPACITY=8_190_000_000
ACTS=['sleep','wake','commute','work','eat','walk','shop','socialize','worship','exercise','rest']
OCCUPATIONS=['vendor','driver','teacher','nurse','cook','barista','courier','musician']
EPOCH=datetime(2026,10,20,14,0,tzinfo=timezone.utc)
TAMPA_ORIGIN={'lat':27.95946425,'lon':-82.5055696,'height':0,'source_kind':'source-confirmed',
              'source_ref':'osm:tampa','source_node_ids':['2057042478','1603574189'],
              'method':'midpoint of shared OSM junction nodes','terrain':'ellipsoidal origin 0; terrain height absent'}


def _unit(*parts):
    return int(digest(list(parts))[:13],16)/float(16**13)


@lru_cache(maxsize=1)
def realms_adapter():
    """Optional original REALMS API, loaded without global path pollution.

    numpy is optional for this adapter; core world operation remains stdlib.
    All historical files stay unmodified.
    """
    name='_worldloom_realms'
    path=ROOT/'upstream/homeless-realms-0.1/realms'
    try:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
        models=importlib.import_module(name+'.models')
        society=importlib.import_module(name+'.society')
        return {'models':models,'society':society,'backend':'REALMS-0.1-original'}
    except (ImportError,FileNotFoundError) as exc:
        return {'backend':'stdlib-declared-synthetic','reason':str(exc)}


def _schedule(actor,day):
    adapter=realms_adapter()
    if 'models' in adapter:
        npc={'id':actor['numeric_id'],'occupation':actor['occupation'],'chronotype_h':actor['chronotype_h'],
             'age':actor['age'],'sociability':actor['sociability'],'home':[27.9597,-82.506]}
        result=adapter['models'].ActivityModel().schedule(npc,day)
        ok,_=adapter['models'].ActivityModel().check(result)
        if ok:return result
    # Explicit fallback: adult seven-hour sleep, work, meals and free time.
    result=['walk']*48
    for i in list(range(0,12))+[46,47]:result[i]='sleep'
    for i in range(17,33):result[i]='work'
    for i in (14,25,37):result[i]='eat'
    return result


@lru_cache(maxsize=1)
def _navigation():
    try:
        compiled=ROOT/'evidence/grammar_world_navigation.json'
        if compiled.is_file() and hashlib.sha256(compiled.read_bytes()).hexdigest()=='c33ca16f54902bfa48f72c4c9e83c9f2ae460952549e1b6db3e2f4425855f65e':
            r=json.loads(compiled.read_text())
        else:
            from .geo import route
            r=route(city='tampa',max_distance=200)
        if r.get('status')=='ok' and len(r.get('points_enu',[]))>1:
            return {'points':[[p[0],0,-p[1]] for p in r['points_enu']], 'length_m':r['length_m'],
                    'source':'source-confirmed OSM pedestrian path; movement remains synthetic',
                    'certificate':r['certificate'],'limitation':'tag-inferred pedestrian access; no dynamic crowd collision solver'}
    except (ImportError,ValueError,KeyError,OSError):pass
    return {'points':[[0,0,0],[50,0,0]],'length_m':50,'source':'constructed fallback segment',
            'certificate':None,'limitation':'source route unavailable'}


def _path_position(distance):
    nav=_navigation();points=nav['points']
    total=sum(math.dist(a,b) for a,b in zip(points,points[1:]))
    phase=distance%(total*2)
    if phase>total:phase=total*2-phase
    for a,b in zip(points,points[1:]):
        length=math.dist(a,b)
        if phase<=length:
            fraction=phase/max(length,1e-9)
            return [round(x+(y-x)*fraction,4) for x,y in zip(a,b)]
        phase-=length
    return list(points[-1])


def speech_intent(text,confidence=1,locale='en-US'):
    """A finite discourse recognizer: transcripts are never executable code."""
    if not isinstance(text,str) or len(text)>1000 or not math.isfinite(float(confidence)):
        return {'act':'clarify','text':'Could you say that a little more simply?','response_text':'Could you say that a little more simply?'}
    value=text.casefold().strip(' .!?')
    acts={'greet':{'hello','hi','hey','مرحبا','أهلا','اهلا'},'decline':{'no','no thanks','لا','لا شكرا'},
          'accept':{'yes','yes please','نعم'},'ride':{'can i ride','i would like a ride','ride','أريد رحلة'},
          'learn':{'teach me','what is this pattern','learn','علمني'},'report':{'report','show the report','تقرير'},
          'look_up':{'look up','what is in the sky','انظر للأعلى'}}
    matched=[act for act,phrases in acts.items() if value in phrases]
    act=matched[0] if len(matched)==1 and confidence>=.65 else 'clarify'
    response={'greet':'Hello. We were just talking about the sign.', 'decline':'Of course. You can keep exploring.',
              'accept':'All right. Let us check the details first.', 'ride':'Where would you like to go?',
              'learn':'We can compare the turns in a recorded walk.', 'report':'The haven has the witnessed world record.',
              'look_up':'Look above the street. That cue belongs to our fictional sky layer.',
              'clarify':'Did you want to talk, learn a pattern, or ask about a ride?'}[act]
    return {'act':act,'semantic_act':act,'confidence':float(confidence),'locale':locale,'text':response,
            'response_text':response,'transcript_retained':False,'provenance':'finite-discourse-grammar.v1',
            'effects_permitted':[] if act=='clarify' else ['dialogue.act']}


def ride_equilibria(tie_break='share'):
    """Enumerate pure Nash equilibria of a declared two-player coordination game."""
    actions=['share','separate']; payoffs={('share','share'):(3,3),('share','separate'):(0,2),('separate','share'):(2,0),('separate','separate'):(2,2)}
    eq=[]
    for a in actions:
        for b in actions:
            u=payoffs[a,b]
            if all(u[0]>=payoffs[x,b][0] for x in actions) and all(u[1]>=payoffs[a,x][1] for x in actions):eq.append([a,b])
    selected=next(e for e in eq if e[0]==tie_break)
    return {'equilibria':eq,'selected':selected,'tie_break':tie_break,'solver':'pure-Nash-enumeration.v1',
            'payoffs':{'/'.join(k):list(v) for k,v in payoffs.items()},'residual':0.0,'tolerance':0.0}


class World:
    VERSION=1

    def __init__(self,seed=7):
        self.seed=int(seed);self.time=0.0;self.tick_count=0;self.revision=0
        self.actors={};self.events=[];self.decisions=[];self.cohorts={};self.invitations={}
        self.proposals={};self.signs={'tampa-shop':{'name':'Amber Fold','kind':'cafe','source_kind':'constructed-fiction','revision':1}}
        self.journeys={};self.missions={};self.heard={};self._event_ids={};self._conversation_slot=-1
        self.founder={'actor_id':'founder','display_name':'Dark','legal_name':'Abed Kadan','historical_source_spelling':'Abed Kadaan','name_assurance':'user-declared; not independent identity verification',
                      'origin':'Marina del Rey','identity_kind':'authentic-founder','authority_source':'authenticated-session-capability'}
        self.conversations=[]
        for i in range(24):
            a=self.resolve_actor(i)
            a['position']=_path_position(6+i*4)
            a['active']=True;a['activity']='walk';a['schedule']=_schedule(a,0)
            self.actors[a['actor_id']]=a
        # Three independently acting nearby speakers; no player-triggered encounter.
        self._ambient_conversation()

    @property
    def world_tick(self):return self.tick_count

    def resolve_actor(self,identifier):
        if isinstance(identifier,str):
            if not identifier.startswith('npc:'):raise ValueError('synthetic NPC ID required')
            identifier=int(identifier.split(':',1)[1])
        if isinstance(identifier,bool) or not isinstance(identifier,int) or not 0<=identifier<CAPACITY:raise IndexError(identifier)
        key=f'npc:{identifier}'
        if key in self.actors:return copy.deepcopy(self.actors[key])
        u=_unit(self.seed,identifier)
        return {'actor_id':key,'numeric_id':identifier,'name':f"{['Mira','Rami','Sana','Jules','Nora','Tariq'][identifier%6]} {identifier//6+1}",
                'synthetic':True,'world_cell':f'virtual:{identifier//100000}', 'role':'resident',
                'appearance':{'preset':identifier%8},'culture_language_metadata':{'locale':'en-US','source_kind':'constructed'},
                'occupation':OCCUPATIONS[identifier%len(OCCUPATIONS)],'age':20+int(u*50),'chronotype_h':round(u*2-1,4),
                'sociability':round(.2+u*.7,4),'goals':['keep-schedule','maintain-relationships'],
                'needs':{'energy':round(.5+u*.5,4),'hunger':round(u*.5,4)},'preferences':{'conversation':u},
                'knowledge_distribution':{},'beliefs':{},'relationships':{},'capabilities':['dialogue','walk','refuse'],
                'policies':['consent-required','local-observation'],'memory':[],'autonomy_budget':16,'render_LOD':'virtual',
                'position':[0,0,0],'orientation':[0,0,1],'active':False,'activity':'unmaterialized',
                'mood':'calm','schedule':[],'schedule_day':0,'identity_source':'seeded-synthetic-not-real-resident'}

    def _ambient_conversation(self):
        slot=int(self.time//8)
        if slot==self._conversation_slot:return
        self._conversation_slot=slot
        texts=[('npc:0','cafe.sign','The new sign says '+self.signs['tampa-shop']['name']+'. I like the sound of it.'),
               ('npc:1','walk.pattern','The walk we recorded bends left, then right by the corner.'),
               ('npc:2','haven.report','We can bring the record to the haven when we meet.')]
        speaker,phrase,text=texts[slot%3]
        self.conversations=[{'episode_id':'tampa-cafe-independent','act_id':f'cafe:{slot}','speaker_actor':speaker,
                             'participants':['npc:0','npc:1','npc:2'],'source_context_hash':digest({'sign':self.signs['tampa-shop'],'slot':slot}),
                             'semantic_act':'statement','canonical_content':{'phrase_id':phrase},'utterance_variant_id':phrase,
                             'phrase_id':phrase,'exact_text':text,'text':text,'voice_id':['amber','river','cedar'][slot%3],
                             'locale':'en-US','speaker_style':'conversational','world_timestamp':slot*8,
                             'position':copy.deepcopy(self.actors[speaker]['position']),'audibility_range':22,
                             'provenance':'independent-conversation-grammar.v1','addresses_player':False}]
        self.emit('speak',speaker,self.actors[speaker]['position'],{'text':text,'phrase_id':phrase,'belief_type':'character-statement'},event_id=f'ambient:cafe:{slot}')

    def tick(self,dt):
        if isinstance(dt,bool) or not isinstance(dt,(float,int)) or not math.isfinite(dt) or dt<0 or dt>86400:
            raise ValueError('dt must be finite seconds in 0..86400')
        if dt==0:return self.snapshot()
        self.time=round(self.time+dt,6);self.tick_count+=1;self.revision+=1
        local=(10+self.time/3600)%24;day=int(self.time//86400)
        decisions=[]
        for actor in self.actors.values():
            if day!=actor['schedule_day']:
                actor['schedule']=_schedule(actor,day);actor['schedule_day']=day
            planned=actor['schedule'][int(local*2)%48]
            feasible=sorted(set([planned,'rest','walk','decline']))
            utilities={act:round((3 if act==planned else .3)+(actor['needs']['energy'] if act=='walk' else 0),6) for act in feasible}
            selected=min(feasible,key=lambda x:(-utilities[x],x))
            witness={'tie_break':'lexicographic-action-name','inputs':{'schedule_slot':int(local*2)%48,'energy':actor['needs']['energy']},
                     'constraints':['own-schedule','finite-energy','local-navigation'],'residual':0.0,'tolerance':0.0}
            decision={'actor_id':actor['actor_id'],'world_tick':self.tick_count,'world_state_revision':self.revision,
                      'available_actions':feasible,'constraints':witness['constraints'],'objective':'maximize-declared-personal-utility',
                      'selected_action':selected,'policy_id':'scheduled-independent.v1','utility_estimates':utilities,
                      'solver':'enumerated-best-response.v1','seed':self.seed,'witness':witness}
            decision['causality_hash']=digest(decision);decisions.append(decision)
            actor['activity']=selected
            if selected in ('walk','commute','shop','exercise'):
                actor['position']=_path_position(6+self.time*1.2+actor['numeric_id']*4)
            actor['memory']=[m for m in actor['memory'] if m['expires_at']>=self.time]
        self.decisions=decisions
        self._ambient_conversation()
        return self.snapshot()

    def emit(self,kind,actor,position,payload=None,event_id=None,reach_m=25):
        allowed={'walk','pause','notice','look_up','speak','gesture','enter_vehicle','accept_ride','observe_sign','recognize_pattern',
                 'save_skill','propose_name','join_cohort','dialogue.act','authorship.adopt','meeting.enter','mission.accept','event.activate'}
        if kind not in allowed:raise ValueError('untyped event kind')
        if len(position)!=3 or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in position):raise ValueError('position must be finite xyz')
        body={'kind':kind,'actor':actor,'position':list(position),'payload':copy.deepcopy(payload or {}),'world_time':self.time}
        event_id=event_id or f"event:{len(self.events)+1}:{digest(body)[:16]}"
        if event_id in self._event_ids:
            old=self._event_ids[event_id]
            if {k:v for k,v in old.items() if k not in ('id','hash','previous','observers','revision')}!=body:raise ValueError('conflicting event ID')
            return copy.deepcopy(old)
        observed=[]
        for a in self.actors.values():
            d=math.dist(position,a['position'])
            # Explicitly bounded voice/line-of-sight model; unknown is not observed.
            blocked=a['actor_id'] in body['payload'].get('occluded_from',[])
            if d<=reach_m and not blocked and a['activity']!='sleep':
                observed.append(a['actor_id'])
                a['memory'].append({'event_id':event_id,'type':'direct-observation','kind':kind,'scope':'local',
                                    'confidence':1.0,'observed_at':self.time,'expires_at':self.time+7*86400,
                                    'source_version':'world-observation.v1'})
                a['memory']=a['memory'][-64:]
        self.revision+=1
        event={**body,'id':event_id,'previous':self.events[-1]['hash'] if self.events else '0'*64,
               'observers':observed,'revision':self.revision}
        event['hash']=digest(event);self.events.append(event);self._event_ids[event_id]=event
        return copy.deepcopy(event)

    def memory(self,actor):return copy.deepcopy(self.actors[actor]['memory'])

    def invite_ride(self,actor,compatibility=1,seats=1,time_available=20,trust=.5):
        npc=self.actors.get(actor) or self.resolve_actor(actor)
        constraints={'compatible_destination':compatibility>.5,'seat_available':seats>0,'schedule_time':time_available>=10,'trust':trust>=.3}
        accept=all(constraints.values())
        utilities={'accept':round(2*compatibility+trust-time_available/100,6) if accept else -1e9,'decline':.3}
        action=max(utilities,key=lambda a:(utilities[a],a))
        d={'actor_id':npc['actor_id'],'world_tick':self.tick_count,'available_actions':['accept','decline'] if accept else ['decline'],
           'constraints':constraints,'objective':'destination-benefit-minus-schedule-cost','selected_action':action,
           'policy_id':'ride-consent.v1','utility_estimates':utilities,'solver':'enumerated-best-response.v1','seed':self.seed,
           'witness':{'inputs':{'compatibility':compatibility,'seats':seats,'time_available':time_available,'trust':trust},
                      'tie_break':'prefer-decline-on-equal-utility','residual':0.0},
           'refusal_reason':None if action=='accept' else ', '.join(k for k,v in constraints.items() if not v) or 'personal preference'}
        d['causality_hash']=digest(d)
        return d

    def authorized(self,actor,role):
        m=self.cohorts.get(actor,{})
        return bool(m.get('accepted') and not m.get('revoked') and role in m.get('roles',[]) and m.get('expires_at',0)>self.time)

    def social_impact(self,contributions):
        if not 1<=len(contributions)<=6:raise ValueError('exact attribution budget is 1..6 contributors')
        adapter=realms_adapter()
        if 'models' not in adapter:raise ValueError('REALMS numerical adapter unavailable')
        graph={i:[j for j in range(12) if j!=i and abs(j-i)<=2] for i in range(12)}
        model=adapter['models'].EventModel()
        shares,total=adapter['society'].shapley(model,graph,[],contributions,self.seed)
        first=next(iter(contributions.values()))
        counterfactual=adapter['society'].impact(model,graph,[],first,self.seed)
        return {'backend':adapter['backend'],'shares':shares,'total':total,'counterfactual':counterfactual,
                'spectral_radius':model.rho,'seed':self.seed,'graph':graph,'solver':'REALMS exact permutation Shapley',
                'limitation':'small declared synthetic social graph; not real social causation'}

    def mission_opportunity(self,facts):
        evidence=sorted(set(facts.get('evidence',[])))
        if not facts.get('goal') or not evidence:return None
        plan={'goal':facts['goal'],'allowable_acts':['observe','approach','overhear','converse','learn','compare','report','return','decline'],
              'steps':['observe','compare','learn','report'],'evidence':evidence,'requires_consent':True,
              'completion_invariant':'evidence-recorded-and-reported','failure_and_refusal':['declined','evidence-unavailable'],
              'budget':{'max_plan_steps':16},'policy_revision':'organic-learning.v1'}
        plan['address']='purl://dark/mission/'+digest(plan)
        return plan

    def dispatch(self,operation,payload=None,actor='player',capabilities=()):
        payload=copy.deepcopy(payload or {});caps=set(capabilities)
        try:
            data=self._dispatch(operation,payload,actor,caps)
            return {'status':'ok','data':data,'trace_digest':digest({'operation':operation,'actor':actor,'data':data}),
                    'effects':[],'source_versions':['world.v1','scheduled-independent.v1'],'warnings':[]}
        except PermissionError as exc:return {'status':'refused','data':{},'warnings':[str(exc)],'effects':[]}
        except (ValueError,KeyError,TypeError,IndexError) as exc:return {'status':'infeasible','data':{},'warnings':[str(exc)],'effects':[]}

    def _dispatch(self,op,p,actor,caps):
        if op in ('query','world.query'):return self.snapshot()
        if op in ('compile','grammar.compile'):return compile_program(p['subject'],p['source'],p.get('context'))
        if op in ('speech.act','npc.interact'):
            target=p.get('target',p.get('npc_id',p.get('actor_id','npc:0')))
            if isinstance(target,int):target='npc:'+str(target)
            fallback={'greet':'hello','ask':'teach me','decline':'no thanks'}.get(p.get('act'),'hello')
            intent=speech_intent(p.get('text',fallback),p.get('confidence',1),p.get('locale','en-US'))
            intent['speaker_actor']=target
            if target in self.actors:
                npc=self.actors[target]
                distance=math.dist(p.get('position',[0,0,0]),npc['position'])
                if distance>25 or p.get('occluded'):
                    intent.update({'act':'not-noticed','response_text':'','text':'','reason':'outside verified voice reach'})
                    return intent
                if p.get('act')=='coauthor':
                    proposal=self.proposals[p['proposal_id']]
                    eligible=npc['needs']['energy']>=.3 and npc['activity']!='sleep'
                    utilities={'endorse':round(npc['preferences']['conversation']+.2,6) if eligible else -1e9,'decline':.5}
                    selected=min(utilities,key=lambda a:(-utilities[a],a))
                    decision={'actor_id':target,'world_tick':self.tick_count,'world_state_revision':self.revision,
                              'available_actions':['endorse','decline'] if eligible else ['decline'],
                              'selected_action':selected,'objective':'creative-interest-with-schedule-and-energy-constraints',
                              'constraints':['local-voice-reach','own-consent','energy-and-schedule'],
                              'utility_estimates':utilities,'solver':'enumerated-best-response.v1','policy_id':'voluntary-coauthor.v1','seed':self.seed,
                              'witness':{'tie_break':'lexicographic-action-name','source_proposal':proposal['proposal_id'],'residual':0.0}}
                    decision['causality_hash']=digest(decision)
                    if target not in proposal['endorsements']+proposal['declines']:
                        proposal['endorsements' if selected=='endorse' else 'declines'].append(target)
                        if selected=='endorse':proposal['collaborators'].append(target)
                    text='I can add my name to that proposal.' if selected=='endorse' else 'I will leave that choice to someone else.'
                    self.emit('dialogue.act',target,npc['position'],{'act':'coauthor' if selected=='endorse' else 'decline','proposal_id':proposal['proposal_id'],'decision':decision})
                    return {'act':'coauthor' if selected=='endorse' else 'decline','semantic_act':'coauthor' if selected=='endorse' else 'decline',
                            'speaker_actor':target,'text':text,'response_text':text,'decision':decision,'outcome':'npc-coauthors' if selected=='endorse' else 'npc-declines'}
                if npc['activity']=='sleep' or (intent['act'] not in ('greet','clarify','decline') and npc['needs']['energy']<.3):
                    intent.update({'act':'decline','response_text':'I need to rest. Perhaps another time.','text':'I need to rest. Perhaps another time.'})
                if intent['act']=='learn':
                    intent['outcome']='npc-teaches'
                    witnessed={m['event_id'] for m in npc['memory']}
                    evidence=[e['id'] for e in self.events if e['id'] in witnessed][-3:]
                    intent['opportunity']=self.mission_opportunity({'goal':'learn-route-pattern','evidence':evidence})
                if intent['act']=='look_up':intent['outcome']='npc-notices-sky-cue'
            if intent['act']!='clarify':self.emit('dialogue.act',actor,p.get('position',[0,0,0]),{'act':intent['act'],'target':target})
            return intent
        if op in ('journey.record','player.action'):
            kind=p.get('kind','walk');event=self.emit(kind,actor,p.get('position',[0,0,0]),p.get('details',{}),p.get('event_id'))
            j=self.journeys.setdefault(actor,{'events':[],'identity_depth':'chain','interpretation':'typed recorded journey; not native C++'})
            if event['id'] not in {x['event_id'] for x in j['events']}:j['events'].append({'event_id':event['id'],'kind':kind,'position':event['position']})
            j['address']='purl://dark/journey/'+digest(j['events'])+'/program'
            j['unfold_witness']={'event_hashes':[self._event_ids[x['event_id']]['hash'] for x in j['events']], 'trace_digest':digest(j['events'])}
            return copy.deepcopy(j)
        if op.startswith('cohort.'):
            member=p.get('member',actor)
            if op=='cohort.accept':
                if actor not in self.invitations or self.invitations[actor]['expiry']<=self.time:raise PermissionError('no live voluntary invitation')
                self.cohorts[actor]={'accepted':True,'roles':[],'expires_at':self.invitations[actor]['expiry'],'revoked':False,'display':'Dark cohort member'}
                self.revision+=1;return copy.deepcopy(self.cohorts[actor])
            if 'founder' not in caps:raise PermissionError('authenticated founder capability required')
            if op=='cohort.invite':
                self.invitations[member]={'expiry':self.time+min(float(p.get('duration',86400)),86400*30),'invited_by':actor}
                return copy.deepcopy(self.invitations[member])
            if op=='cohort.delegate':
                if not self.cohorts.get(member,{}).get('accepted'):raise PermissionError('member has not consented')
                roles=p.get('roles',[])
                if set(roles)-{'signage','event.propose','report','coauthor'}:raise PermissionError('role cannot delegate founder or shell powers')
                self.cohorts[member].update({'roles':roles,'expires_at':self.time+min(max(0,float(p.get('duration',3600))),86400*30),'delegated_by':actor,'display':'Delegated Dark cohort member'})
            elif op=='cohort.revoke':self.cohorts.setdefault(member,{})['revoked']=True
            else:raise ValueError('unsupported cohort operation')
            self.revision+=1;return copy.deepcopy(self.cohorts[member])
        if op in ('authorship.propose','governance.propose'):
            name=p.get('name',p.get('text',''));kind=p.get('kind','cafe')
            compiled=compile_program('naming',f'name {kind} {name}')
            if not compiled['valid']:raise ValueError(str(compiled['diagnostics']))
            pid='proposal:'+digest({'author':actor,'scene':p.get('scene_id','tampa-shop'),'program':compiled['program'],'revision':self.revision})
            proposal={'proposal_id':pid,'source_grammars':[compiled['grammar_revision']],'author':actor,'collaborators':[],
                      'scene_id':p.get('scene_id','tampa-shop'),'scope':'fictional-shop-sign','details':compiled['program'],
                      'endorsements':[],'declines':[],'adoption_event':None,'revision':1,'unfold_witness':compiled['witness'],
                      'program':compiled,'prior':copy.deepcopy(self.signs.get(p.get('scene_id','tampa-shop')))}
            self.proposals[pid]=proposal;self.revision+=1;return copy.deepcopy(proposal)
        if op=='authorship.endorse':
            prop=self.proposals[p['proposal_id']]
            if actor not in prop['endorsements']+prop['declines']:
                prop['endorsements' if p.get('consent') else 'declines'].append(actor)
                if p.get('consent') and actor!=prop['author']:prop['collaborators'].append(actor)
            self.revision+=1;return copy.deepcopy(prop)
        if op in ('authorship.adopt','authorship.revert'):
            if 'founder' not in caps:raise PermissionError('founder adoption capability required')
            prop=self.proposals[p['proposal_id']]
            if op=='authorship.revert':
                if prop['prior'] is None:self.signs.pop(prop['scene_id'],None)
                else:self.signs[prop['scene_id']]=copy.deepcopy(prop['prior'])
                self.revision+=1;return {'proposal_id':prop['proposal_id'],'reverted':True}
            if not prop['endorsements']:raise PermissionError('at least one consenting endorsement required')
            name=prop['details']['name'];scene=prop['scene_id']
            self.signs[scene]={'name':name,'kind':prop['details']['kind'],'source_kind':'constructed-fiction','revision':prop['revision']+1,
                               'author':prop['author'],'collaborators':prop['collaborators']}
            event=self.emit('authorship.adopt',actor,[0,0,0],{'proposal_id':prop['proposal_id'],'name':name})
            prop['adoption_event']=event['id'];prop['revision']+=1
            return copy.deepcopy(prop)
        if op=='haven.enter':
            evidence=p.get('evidence',[e['id'] for e in self.events[-12:]])
            compiled=compile_program('haven','meet '+p.get('place','tampa-haven')+' report '+' '.join(evidence),
                                     {'events':[e['id'] for e in self.events],'governed':True,'consenting':bool(p.get('consent',True))})
            if not compiled['valid']:raise ValueError(str(compiled['diagnostics']))
            # Report speakers can only cite records they observed or authored.
            reports={a['actor_id']:[e for e in evidence if e in {m['event_id'] for m in a['memory']}] for a in self.actors.values()}
            report={'grammatical':compiled,'report':Grammatical(compiled).run(),'speaker_evidence':{k:v for k,v in reports.items() if v}}
            self.emit('meeting.enter',actor,p.get('position',[0,0,0]),{'place':p.get('place','tampa-haven'),'evidence':evidence})
            return report
        if op in ('mission.opportunity','mission.accept'):
            facts={'goal':p.get('goal','learn-route-pattern'),'evidence':p.get('evidence',[e['id'] for e in self.events[-3:]])}
            m=self.mission_opportunity(facts)
            if op=='mission.accept':
                if not p.get('consent',True):return {'status':'declined'}
                if m is None:raise ValueError('mission requires actual world evidence')
                if not set(m['evidence'])<={e['id'] for e in self.events}:raise ValueError('mission evidence not in world')
                self.missions[m['address']]={**m,'actor':actor,'status':'accepted'}
                self.emit('mission.accept',actor,p.get('position',[0,0,0]),{'mission':m['address']})
            return m
        if op=='event.activate':
            if 'scene.activate' not in caps and 'founder' not in caps:raise PermissionError('typed event activation capability required')
            if p.get('expected_revision',self.revision)!=self.revision:raise ValueError('stale activation precondition')
            return self.emit('event.activate',actor,p.get('position',[0,0,0]),p.get('effect',{}),p.get('event_id'))
        raise ValueError('unsupported world operation: '+op)

    def snapshot(self):
        return copy.deepcopy({'schema_version':self.VERSION,'seed':self.seed,'revision':self.revision,'tick':self.tick_count,'world_time':self.time,
                              'clock':{'world_epoch':(EPOCH+timedelta(seconds=self.time)).isoformat(),'logical_tick':self.tick_count,'driver':'world-seconds'},
                              'rng':{'algorithm':'sha256-keyed-stateless.v1','seed':self.seed,'position':'keys=(seed,actor,logical-tick)'},
                              'cell':'tampa-dale-mabry-spruce','origin':TAMPA_ORIGIN,
                              'founder':self.founder,'population':{'capacity':CAPACITY,'active':len(self.actors),
                               'cohort_background':CAPACITY-len(self.actors),'decrements_on_player_join':False,'source_kind':'synthetic-capacity'},
                              'actors':list(self.actors.values()),'events':self.events,'decisions':self.decisions,'cohorts':self.cohorts,
                              'invitations':self.invitations,'proposals':self.proposals,'signs':self.signs,'journeys':self.journeys,'missions':self.missions,
                              'conversations':self.conversations,'conversation_slot':self._conversation_slot,'heard':self.heard,
                              'mission_opportunities':[self.mission_opportunity({'goal':'learn-route-pattern','evidence':[e['id'] for e in self.events[-2:]]})],
                              'navigation':{'source':_navigation()['source'],'certificate':_navigation()['certificate'],'limitation':_navigation()['limitation']},
                              'background':{'method':'aggregate-synthetic-cohorts','activity_phase':int(self.time//1800),'individual_ticks':len(self.actors)},
                              'model_versions':{'world':'world.v1','registry':digest(registry()),'activity_backend':realms_adapter()['backend']}})

    @classmethod
    def from_snapshot(cls,snapshot):
        if snapshot.get('schema_version')!=cls.VERSION:raise ValueError('unsupported world snapshot version')
        w=cls.__new__(cls)
        w.seed=snapshot['seed'];w.time=snapshot['world_time'];w.tick_count=snapshot['tick'];w.revision=snapshot['revision']
        w.actors={a['actor_id']:copy.deepcopy(a) for a in snapshot['actors']}
        for field in ('events','decisions','cohorts','invitations','proposals','signs','journeys','missions','founder','conversations','heard'):
            setattr(w,field,copy.deepcopy(snapshot[field]))
        w._conversation_slot=snapshot['conversation_slot'];w._event_ids={e['id']:e for e in w.events}
        return w
