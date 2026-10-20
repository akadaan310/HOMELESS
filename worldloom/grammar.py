"""Typed symbolic grammar factory and version-pinned, interpreted world programs.

Ingram's original KN3 and Tower execute here, through isolated source imports.
Usage scores never decide membership in the admitted language. Effects are typed
proposals; the authoritative session decides whether any effect is committed.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import re
import shlex
import sys
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


@lru_cache(maxsize=8)
def source_module(relative, name):
    """Load verified repository files without changing their source or sys.path."""
    path = ROOT / 'upstream' / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _ingram():
    return source_module('ingram-0.1/ingram/ingrammar.py', '_worldloom_ingrammar')


def _tower():
    return source_module('ingram-0.1/ingram/tower.py', '_worldloom_tower').Tower


SCHEMAS = {
    'walk': {'sorts': {'nodes': 'Node+'}, 'verb': 'walk', 'form': 'retial-path',
             'production': 'Walk := walk Node Node+', 'semantics': 'connected-walk', 'effects': ['journey.step'],
             'alphabet': ['walk', 'Node'], 'constraints': ['adjacent', 'walkable'],
             'positive': [('walk a b c', {'graph': {'a':['b'], 'b':['c']}})],
             'negative': [('walk a c', {'graph': {'a':['b']}}), ('fly a b', {})],
             'heldout': [('walk x y', {'graph': {'x':['y']}})]},
    'audio': {'sorts': {'cue':'Cue', 'gain':'Float[0,1]', 'duration_ms':'Int[1,10000]'}, 'verb':'emit',
              'form':'attribute-grammar', 'production':'Gesture := emit Cue Gain DurationMs', 'semantics':'bounded-audio-gesture',
              'effects':['sound.cue'], 'alphabet':['emit','bell','footstep','voice','balloon','music','aircraft'],
              'constraints':['gain-bounded','duration-bounded','balloon-event-geometry'],
              'positive':[('emit bell 0.4 200', {}), ('emit voice 0.7 1500', {})],
              'negative':[('emit bell 3 200', {}), ('emit bell 0.5 -1', {})],
              'heldout':[('emit footstep 0.3 110', {}), ('emit balloon 0.1 850', {'balloon_audience':True,'geometry_valid':True})]},
    'naming': {'sorts':{'kind':'ShopKind','name':'FictionalName'}, 'verb':'name', 'form':'attribute-grammar',
               'production':'Sign := name ShopKind FictionalName', 'semantics':'fictional-sign-proposal',
               'effects':['sign.propose'], 'alphabet':['name','cafe','market','garage','books','bakery','studio'],
               'constraints':['fictional-name','unicode-letters','length-bounded'],
               'positive':[('name cafe Amber Fold', {}), ('name market Harbor Thread', {})],
               'negative':[('name cafe Real Shop', {'real_names':['Real Shop']}), ('name warshop X', {})],
               'heldout':[('name bakery Silver Tide', {}), ('name books باب Fold', {})]},
    'haven': {'sorts': {'place':'Place','evidence':'EventID+'}, 'verb':'meet', 'form':'typed-effect-grammar',
              'production':'RENDEZVOUS_HAVEN := meet Place report EventID+', 'semantics':'evidence-based-meeting',
              'effects':['meeting.propose'], 'alphabet':['meet','report','Place','EventID'],
              'constraints':['evidence-exists','governed-place','voluntary-attendance'],
              'positive':[('meet haven report e1', {'events':['e1'],'governed':True,'consenting':True})],
              'negative':[('meet haven report e2', {'events':['e1']})],
              'heldout':[('meet marina report e3 e4', {'events':['e3','e4'],'governed':True,'consenting':True})]},
}


class GrammarFactory:
    """Select executable grammar forms from typed subject schemas and fixtures.

    This is bounded template synthesis, not unrestricted grammar induction. A
    schema's sorts, alphabet and constraints are part of the generated revision.
    Each candidate must accept positives and heldout, and reject counterexamples.
    """
    def build(self, subject, schema=None, examples=None, counterexamples=None, heldout=None):
        subject = {'shop-sign':'naming','audio-gesture':'audio','RENDEZVOUS_HAVEN':'haven'}.get(subject, subject)
        if subject not in SCHEMAS:
            raise ValueError('unsupported subject: '+str(subject))
        spec = copy.deepcopy(SCHEMAS[subject])
        if schema:
            if set(schema) - {'alphabet','sorts','constraints','max_steps'}:
                raise ValueError('unimplemented schema operation')
            spec.update(copy.deepcopy(schema))
        fixtures = {'positive': examples if examples is not None else spec.pop('positive'),
                    'negative': counterexamples if counterexamples is not None else spec.pop('negative'),
                    'heldout': heldout if heldout is not None else spec.pop('heldout')}
        for key in ('positive','negative','heldout'):
            spec.pop(key, None)
        description = {'version':1,'subject':subject,'alphabet':spec['alphabet'],'sorts':spec['sorts'],
                       'productions':[spec['production']], 'form':spec['form'], 'semantics':spec['semantics'],
                       'constraints':spec['constraints'], 'effects':spec['effects'], 'budget':{'max_steps':spec.get('max_steps',3000)},
                       'generator':'Grammatica-Generatrix.bounded-template.v1',
                       'limitations':['finite symbolic domain; no unrestricted grammar induction','effect interpretation proposes, never commits']}
        description['revision'] = digest(description)
        description['model_id'] = f"grammar:world.{subject}.v1@{description['revision']}"
        rows = []
        for group, cases in fixtures.items():
            for source, context in cases:
                result = _parse(subject, source, context, description)
                rows.append({'partition':group,'source':source,'context_hash':digest(context),
                             'accepted':result['valid'],'expected':group!='negative',
                             'diagnostics':result['diagnostics']})
        description['fixtures'] = rows
        description['certificate'] = {'passed':all(r['accepted']==r['expected'] for r in rows),
                                      'heldout_passed':sum(r['partition']=='heldout' and r['accepted'] for r in rows),
                                      'fixture_digest':digest(rows), 'checks':['type-safety','admissibility','counterexamples','heldout','bounded-evaluator']}
        description['derivation'] = ['select '+spec['form'], 'instantiate typed sorts', 'bind semantic interpreter', 'run separated fixture partitions']
        return description


def _diagnostic(code, message):
    return {'code':code,'message':message}


def _parse(subject, source, context, grammar):
    diagnostics = []
    ast = None
    if not isinstance(source, str) or len(source.encode()) > 32768:
        return {'valid':False,'diagnostics':[_diagnostic('BUDGET','source must be text <= 32768 bytes')],'program':None}
    try:
        tokens = shlex.split(source)
    except ValueError as exc:
        return {'valid':False,'diagnostics':[_diagnostic('SYNTAX_INVALID',str(exc))],'program':None}
    budget = min(context.get('max_steps',3000),grammar['budget']['max_steps'])
    if len(tokens)>budget or budget<=0:
        diagnostics.append(_diagnostic('BUDGET','finite token budget exceeded'))
    elif subject=='walk':
        if len(tokens)<3 or tokens[0]!='walk' or any(not re.fullmatch(r'[\w.:/-]+',n) for n in tokens[1:]):
            diagnostics.append(_diagnostic('SYNTAX_INVALID','expected walk Node Node+'))
        else:
            nodes=tokens[1:]; graph=context.get('graph')
            ast={'op':'walk','nodes':nodes}
            if graph is None:
                diagnostics.append(_diagnostic('MISSING_INFORMATION','a versioned navigation graph is required'))
            elif any(b not in graph.get(a,[]) for a,b in zip(nodes,nodes[1:])):
                diagnostics.append(_diagnostic('SEMANTIC_IMPOSSIBLE','route uses a disconnected edge'))
            elif any(n in context.get('blocked_nodes',[]) for n in nodes):
                diagnostics.append(_diagnostic('SEMANTIC_IMPOSSIBLE','route uses a blocked node'))
    elif subject=='audio':
        if len(tokens)!=4 or tokens[0]!='emit' or tokens[1] not in grammar['alphabet'][1:]:
            diagnostics.append(_diagnostic('SYNTAX_INVALID','expected emit Cue Gain DurationMs'))
        else:
            try:
                gain=float(tokens[2]); duration=int(tokens[3])
                if not math.isfinite(gain) or not 0<=gain<=1 or not 1<=duration<=10000: raise ValueError()
                ast={'op':'emit','cue':tokens[1],'gain':gain,'duration_ms':duration}
            except ValueError:
                diagnostics.append(_diagnostic('TYPE_INVALID','gain 0..1, duration integer 1..10000 required'))
            if tokens[1]=='balloon' and not (context.get('balloon_audience') and context.get('geometry_valid')):
                diagnostics.append(_diagnostic('SEMANTIC_IMPOSSIBLE','balloon audience requires admitted event and coherent geometry'))
    elif subject=='naming':
        if len(tokens)<3 or tokens[0]!='name' or tokens[1] not in grammar['alphabet'][1:]:
            diagnostics.append(_diagnostic('SYNTAX_INVALID','expected name ShopKind FictionalName'))
        else:
            name=' '.join(tokens[2:])
            if not 3<=len(name)<=64 or not all(c.isalpha() or c in " '-" for c in name):
                diagnostics.append(_diagnostic('TYPE_INVALID','fictional name must contain 3..64 Unicode letters/spaces'))
            elif name.casefold() in {n.casefold() for n in context.get('real_names',[])}:
                diagnostics.append(_diagnostic('SEMANTIC_IMPOSSIBLE','name collides with a declared factual business'))
            ast={'op':'name','kind':tokens[1],'name':name,'source_kind':'constructed-fiction'}
    elif subject=='haven':
        if len(tokens)<4 or tokens[0]!='meet' or tokens[2]!='report':
            diagnostics.append(_diagnostic('SYNTAX_INVALID','expected meet Place report EventID+'))
        else:
            ast={'op':'meet','place':tokens[1],'evidence':tokens[3:]}
            known={e if isinstance(e,str) else e.get('id') for e in context.get('events',[])}
            if not set(tokens[3:])<=known:
                diagnostics.append(_diagnostic('MISSING_INFORMATION','report refers to unrecorded event evidence'))
            if not context.get('governed') or not context.get('consenting'):
                diagnostics.append(_diagnostic('REFUSED','meeting needs governed venue and voluntary participants'))
    return {'valid':not diagnostics,'diagnostics':diagnostics,'program':ast}


@lru_cache(maxsize=4)
def _usage(subject):
    examples={'walk':['walk a b c']*5, 'audio':['emit bell 0.4 200']*8+['emit voice 0.7 1500']*4,
              'naming':['name cafe Amber Fold']*5+['name market Harbor Thread']*3,
              'haven':['meet haven report e1']*3}
    return _ingram().KN3().fit([s.split() for s in examples[subject]])


def compile_program(subject, source, context=None):
    subject={'shop-sign':'naming','audio-gesture':'audio','RENDEZVOUS_HAVEN':'haven'}.get(subject,subject)
    context=copy.deepcopy(context or {})
    grammar=GrammarFactory().build(subject)
    result=_parse(subject,source,context,grammar)
    result.update({'subject':subject,'grammar_revision':grammar['revision'],'source':source,
                   'context':context,'context_hash':digest(context),'semantics':grammar['semantics'],
                   'effects_declared':grammar['effects'],'identity_depth':'chain','budget':grammar['budget'],
                   'usage_logprob':_usage(subject).logprob(source.split()) if isinstance(source,str) else None,
                   'usage_backend':'upstream/ingram-0.1/ingram/ingrammar.py:KN3',
                   'observable':{'walk':'route-and-step-trace','audio':'spatial-sound-cue','naming':'fictional-sign','haven':'evidence-report'}[subject]})
    result['diagnosis']='UNUSUAL_LEGITIMATE' if result['valid'] and subject=='audio' and result['program']['cue']=='balloon' else ('ADMITTED' if result['valid'] else result['diagnostics'][0]['code'])
    if result['valid']:
        text=canonical(result['program'])
        tower=_tower()().fit([text]*3,n_merges=24,min_count=2)
        result['fold']={'letters':tower.implicate(text),'tower':json.loads(tower.to_json()),'derivation_address':tower.address(text)}
        result['address']=f"purl://dark/grammatical/{subject}/{grammar['revision']}/{digest({'program':result['program'],'context':context})}"
        result['witness']={'parse_roundtrip':tower.unaddress(tower.address(text))==text,
                           'fold_unfold':tower.explicate(tower.implicate(text))==text,
                           'source_digest':digest(source),'context_hash':digest(context), 'grammar_certificate':grammar['certificate']}
    else:
        result['address']=None;result['witness']=None
    return result


def validate_program(program):
    try:
        fresh=compile_program(program['subject'],program['source'],program.get('context'))
    except (KeyError,ValueError,TypeError) as exc:
        return {'valid':False,'diagnostics':[_diagnostic('TYPE_INVALID',str(exc))]}
    ok=fresh['valid'] and all(fresh.get(k)==program.get(k) for k in ('program','grammar_revision','context_hash','address','fold','effects_declared','witness'))
    return {'valid':ok,'diagnostics':[] if ok else [_diagnostic('VERSION_OR_WITNESS_MISMATCH','program differs from pinned parse/semantics')]}


class Grammatical:
    def __init__(self, compiled): self.compiled=copy.deepcopy(compiled)

    def describe(self): return copy.deepcopy(self.compiled)

    def validate(self): return validate_program(self.compiled)

    def expand(self):
        if not self.validate()['valid']: raise ValueError('invalid version-pinned grammatical')
        fold=self.compiled['fold']; tower=_tower().from_json(canonical(fold['tower']))
        return json.loads(tower.explicate(fold['letters']))

    def run(self):
        ast=self.expand(); op=ast['op']
        if op=='walk':
            trace=[{'from':a,'to':b,'index':i} for i,(a,b) in enumerate(zip(ast['nodes'],ast['nodes'][1:]))]
            effects=[{'kind':'journey.step','channel':'movement',**x} for x in trace]
        elif op=='emit':
            trace=[{'cue':ast['cue'],'duration_ms':ast['duration_ms'],'gain':ast['gain']}]
            effects=[{'kind':'sound.cue','channel':'sound',**trace[0]}]
        elif op=='name':
            trace=[{'fictional_name':ast['name'],'shop_kind':ast['kind']}]
            effects=[{'kind':'sign.propose','channel':'signage',**trace[0]}]
        else:
            trace=[{'place':ast['place'],'verified_evidence':ast['evidence']}]
            effects=[{'kind':'meeting.propose','channel':'society',**trace[0]}]
        result={'address':self.compiled['address'],'effects':effects,'trace':trace,'effect_policy':'propose-only',
                'semantics':self.compiled['semantics'],'grammar_revision':self.compiled['grammar_revision']}
        result['trace_digest']=digest(result)
        return result

    invoke=run
    replay=run


def registry():
    """Full required registry. Status states the scope of each actual adapter."""
    contracts={
        'Actor':('synthetic-ID','lazy deterministic record','worldloom.society:World.resolve_actor'),
        'Activity':('48 half-hour activities','schedule admissibility','REALMS ActivityModel + stdlib fallback'),
        'Event':('typed observations','causal local event ledger','worldloom.society:World.emit'),
        'Mission':('goal/act/evidence','bounded organic learning plans','worldloom.society:World.mission_opportunity'),
        'Spatial':('coordinates/edges','connected walk','worldloom.grammar:walk'),
        'Portal':('visit/overlay/braid','certificate required','external adapter required'),
        'Society':('relationships/cohorts','observer-limited memory','worldloom.society:World'),
        'Asset':('content hashes','source and delivery verification','external asset adapter'),
        'Language':('discourse acts','bounded intent grammar','worldloom.society:speech_intent'),
        'Governance':('delegation/proposal','consent/expiry/revocation','worldloom.society:World.dispatch'),
        'Sound':('cue/gain/duration','bounded audio gesture','worldloom.grammar:audio'),
        'Sky':('catalog stars','catalog witness required','external sky adapter'),
        'Weather':('observed/constructed fields','range and source tags','external weather adapter'),
        'Camera':('pose/follow','collision and comfort','external camera adapter'),
        'Vehicle':('ride/decline','consent/seats/compatibility','worldloom.society:World.invite_ride'),
        'Transport':('walk/ride','typed permitted paths','walk grammar and ride decisions'),
        'Economic':('fictional credit','authorship by contribution','authorship proposal ledger'),
        'Emergence':('causal effects','bounded reach/decay','local event propagation'),
        'Grammar Generator':('typed schemas','fixture-certified template synthesis','worldloom.grammar:GrammarFactory'),
        'Continuity':('snapshot/replay','version pinned deterministic restoration','worldloom.society:World.from_snapshot'),
        'Procedural Signage':('fictional names','Unicode name grammar/coauthorship','worldloom.grammar:naming'),
    }
    return {name:{'version':1,'alphabet':alphabet,'grammar':grammar,'ingrammar':'declared symbolic priors; Ingram KN3 for compiled programs',
                  'context':['seed','world_revision','actor','source_versions'],'transitions':'typed propose/validate/commit',
                  'observer':'scoped world witness','verifier':'module predicates + tests','budget':{'max_steps':3000,'max_active_actors':96},
                  'capability':'typed-effects-only','interface':interface,
                  'status':'adapter-required' if 'external' in interface else 'implemented-reference'}
            for name,(alphabet,grammar,interface) in contracts.items()}
