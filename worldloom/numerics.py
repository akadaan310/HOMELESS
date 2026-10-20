"""Typed, bounded numerical authority; no numerical method advances world state."""
from __future__ import annotations
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'worldloom-native-1'
STATUSES = ['optimal-certified', 'infeasible', 'unsupported', 'unbounded', 'timed-out']
_LIB = None


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _finite(value, name):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(name + ' must be finite')
    return value


def build_native():
    target = ROOT / 'artifacts/native'
    target.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'native/worldloom_math.cpp'
    outputs = [target / 'libworldloom_math.so', target / 'worldloom-math']
    commands = []
    for output, flags in zip(outputs, (['-shared', '-fPIC', '-DWORLDLOOM_LIBRARY'], [])):
        cmd = ['g++', '-std=c++17', '-O2', '-fno-fast-math', '-Wall', '-Wextra', *flags, str(source), '-o', str(output)]
        if not output.exists() or source.stat().st_mtime > output.stat().st_mtime:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if p.returncode:
                raise RuntimeError(p.stderr)
        commands.append(cmd)
    return {'version': VERSION, 'commands': commands, 'compiler': subprocess.check_output(['g++', '--version'], text=True).splitlines()[0], 'source_hash': hashlib.sha256(source.read_bytes()).hexdigest(), 'outputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs}}


def _lib():
    global _LIB
    if _LIB is None:
        build_native()
        _LIB = ctypes.CDLL(str(ROOT / 'artifacts/native/libworldloom_math.so'))
        dp = ctypes.POINTER(ctypes.c_double)
        _LIB.wl_box_qp.argtypes = [ctypes.c_int, dp, dp, dp, dp, dp]
        _LIB.wl_decay.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int, dp]
        _LIB.wl_game.argtypes = [ctypes.c_int, ctypes.c_int, dp, dp, ctypes.POINTER(ctypes.c_int)]
        _LIB.wl_camera.argtypes = [ctypes.c_double, dp, ctypes.c_int]
        _LIB.wl_weather.argtypes = [ctypes.c_double]*4+[dp]
    return _LIB


def _result(problem, status, primal, objective=None, residuals=None, **extras):
    r = {'status': status, 'primal': primal, 'dual': None, 'objective_value': objective, 'residuals': residuals or {}, 'optimality_gap': 0 if status == 'optimal-certified' else None, 'seed': problem.get('seed', 0), 'solver': VERSION, 'numerical_policy': {'float': 'IEEE754 binary64', 'tolerance': 1e-9, 'fast_math': False}, **extras}
    r['witness_hash'] = _hash({'problem':problem, 'result':r})
    return r


def solve_box_qp(problem):
    p = dict(problem)
    h = [_finite(v,'hessian') for v in p.get('hessian_diagonal', [2, 4])]
    g = [_finite(v,'linear') for v in p.get('linear', [-6, 8])]
    lo = [-math.inf if v is None else _finite(v,'lower') for v in p.get('lower', [0, -1])]
    hi = [math.inf if v is None else _finite(v,'upper') for v in p.get('upper', [2, 3])]
    n = len(h)
    if not n or len(g)!=n or len(lo)!=n or len(hi)!=n:
        raise ValueError('equal nonempty coefficient dimensions required')
    if n > 256:
        return _result(p,'timed-out',[],reason='dimension budget 256')
    arr = ctypes.c_double*n
    x = arr()
    status = STATUSES[_lib().wl_box_qp(n,arr(*h),arr(*g),arr(*lo),arr(*hi),x)]
    if status != 'optimal-certified':
        return _result(p,status,[])
    x = list(x)
    grad = [h[i]*x[i]+g[i] for i in range(n)]
    kkt = [0 if lo[i] == hi[i] else abs(v) if lo[i]+1e-12 < x[i] < hi[i]-1e-12 else max(0,-v) if x[i]<=lo[i]+1e-12 else max(0,v) for i,v in enumerate(grad)]
    return _result(p,status,x,sum(.5*h[i]*v*v+g[i]*v for i,v in enumerate(x)), {'primal_inf':max([0]+[max(lo[i]-x[i],x[i]-hi[i],0) for i in range(n)]), 'kkt_inf':max(kkt)}, proof='separable convex quadratic; signed bound KKT suffices', resource_usage={'coordinates':n,'iterations':1}, units=p.get('units','declared-dimensionless-fixture'))


def solve_decay_ode(problem):
    p = dict(problem)
    rate = _finite(p.get('rate',.7),'rate')
    initial = _finite(p.get('initial',3),'initial')
    duration = _finite(p.get('duration',4),'duration')
    steps = int(p.get('steps',400))
    if not 1<=steps<=100000:
        return _result(p,'timed-out',[],reason='step budget [1,100000]')
    y = ctypes.c_double()
    code = _lib().wl_decay(rate,initial,duration,steps,ctypes.byref(y))
    if code:
        return _result(p,STATUSES[code],[])
    reference = initial*math.exp(-rate*duration)
    return _result(p,'approximate-feasible',[y.value],residuals={'analytic_error':abs(y.value-reference)}, equation='dy/dt = -rate*y', resource_usage={'steps':steps, 'evaluations':4*steps}, units={'time':'s','rate':'s^-1'})


def solve_game(problem):
    a,b = problem['row'],problem['column']
    nr,nc = len(a),len(a[0]) if a else 0
    if not 1<=nr<=8 or not 1<=nc<=8 or len(b)!=nr or any(len(row)!=nc for row in a+b):
        raise ValueError('both payoff matrices must have same dimensions in [1,8]')
    av = [_finite(x,'payoff') for row in a for x in row]
    bv = [_finite(x,'payoff') for row in b for x in row]
    arr=ctypes.c_double*(nr*nc); out=(ctypes.c_int*64)()
    count=_lib().wl_game(nr,nc,arr(*av),arr(*bv),out)
    eq = [[out[i]//nc,out[i]%nc] for i in range(count)]
    status='optimal-certified' if count==1 else 'ambiguous-equilibria' if count>1 else 'not-converged'
    return _result(problem,status,eq, objective='no profitable unilateral deviation', tie_break='lexicographic only when explicitly selected; all pure equilibria returned', limitation='bounded pure-strategy enumeration; absent pure equilibrium does not mean no mixed equilibrium')


def negotiate(problem):
    reservation = problem.get('reservation',[0,0])
    actions=problem.get('actions',[])
    feasible=[a for a in actions if all(a['utility'][i]>=reservation[i] for i in range(2))]
    ranked=sorted(feasible,key=lambda a:(-min(a['utility'][i]-reservation[i] for i in range(2)),-sum(a['utility']),a['id']))
    outcome='agreement' if ranked else 'refusal' if any(all(a['utility'][i]<reservation[i] for a in actions) for i in range(2)) else 'indeterminate-conflict'
    return {'outcome':outcome, 'chosen':ranked[0] if ranked else None, 'feasible_actions':[a['id'] for a in feasible], 'independent_utilities':actions, 'reservation':reservation, 'objective':'maximize minimum individual surplus, then joint surplus', 'tie_break':'lexicographic action id', 'may_decline':True,'unknowns':problem.get('unknowns',[])}


def negotiation_cases():
    return [negotiate(p) for p in [
        {'actions':[{'id':'share-route','utility':[3,2]},{'id':'rush','utility':[5,-2]}]},
        {'actions':[{'id':'demand','utility':[4,-3]}]},
        {'actions':[{'id':'east','utility':[3,-1]},{'id':'west','utility':[-1,3]}], 'unknowns':['meeting time preference']}]]


def _percentile(values,p):
    a=sorted(values)
    return a[min(len(a)-1,int((len(a)-1)*p))] if a else 0


def camera_trace(problem=None):
    p=dict(problem or {}); fps=_finite(p.get('fps',60),'fps'); duration=_finite(p.get('duration',6),'duration')
    modes={'trailing-elevated':(-6,3), 'over-shoulder':(-2,1.7), 'cinema-arc':(-8,4), 'street-eye':(-2,1.65), 'first-person-AR':(0,1.65), 'free-look':(-8,5), 'vehicle-interior':(0,1.2), 'vehicle-follow':(-8,2.8), 'distant-witness':(-20,10), 'portal-transition':(-5,3), 'balloon-aerial':(-15,30)}
    mode=p.get('mode','trailing-elevated')
    if not 1<=fps<=240 or not 0<duration<=60 or mode not in modes:
        raise ValueError('fps [1,240], duration (0,60], known mode required')
    count=round(duration*720)+1; out=(ctypes.c_double*(count*5))()
    count=_lib().wl_camera(duration,out,count)
    micro=[list(out[i*5:i*5+5]) for i in range(count)]
    samples=[]
    for i in range(int(duration*fps)+1):
        idx=min(count-1,round(i/fps*720)); t,x,v,a,target=micro[idx]
        samples.append({'time':t,'x':x,'y':modes[mode][0],'z':modes[mode][1],'velocity':v,'acceleration':a,'target_x':target,'roll':0})
    jerk=[abs((micro[i][3]-micro[i-1][3])*720) for i in range(1,count)]
    # Same observed target and time grid for controlled direct-follow baseline.
    baseline_jerk=[abs((micro[i+3][4]-3*micro[i+2][4]+3*micro[i+1][4]-micro[i][4])*720**3) for i in range(count-3)]
    metrics={'jerk_max_m_s3':max(jerk),'jerk_p95_m_s3':_percentile(jerk,.95),'jerk_p99_m_s3':_percentile(jerk,.99),'roll_jitter_deg':0,'angular_velocity_deg_s':0,'collision_violations':sum(abs(s['x'])>20 for s in samples),'target_framing_normalized_rmse':math.sqrt(sum(((s['target_x']-s['x'])/20)**2 for s in samples)/len(samples)), 'occlusion_exposure_s':None}
    return {'mode':mode,'fps':fps,'samples':samples,'metrics':metrics,'baseline':{'jerk_p99_m_s3':_percentile(baseline_jerk,.99)},'budget':{'fixed_hz':720,'steps':count-1,'max_steps':43200},'limitations':['synthetic one-dimensional target track in bounded corridor','no engine ray casts, projected framing, horizon image or stream packet measurements'], 'witness_hash':_hash(samples)}


def _wind(x,y,t,radius):
    out=(ctypes.c_double*4)(); _lib().wl_weather(x,y,t,radius,out)
    return list(out)


def weather_field(problem=None):
    p=dict(problem or {}); t=_finite(p.get('time',2),'time'); rain=_finite(p.get('rain',.4),'rain'); initial=_finite(p.get('initial_wetness',.1),'wetness'); radius=_finite(p.get('radius',12),'radius')
    if not 0<=initial<=1 or not 0<=rain<=2 or not 0<=t<=3600 or not 1<=radius<=1000:
        raise ValueError('wetness [0,1], rain [0,2], time [0,3600], radius [1,1000] required')
    k=.06; eq=rain/(rain+k) if rain+k else 0; wet=eq+(initial-eq)*math.exp(-(rain+k)*t)
    samples=[]; div=[]; epsilon=radius/1000
    for ix in range(-8,9):
        for iy in range(-8,9):
            x,y=ix*radius/6,iy*radius/6
            vx,vy,vz,w=_wind(x,y,t,radius)
            divergence=(_wind(x+epsilon,y,t,radius)[0]-_wind(x-epsilon,y,t,radius)[0]+_wind(x,y+epsilon,t,radius)[1]-_wind(x,y-epsilon,t,radius)[1])/(2*epsilon)
            div.append(abs(divergence)); samples.append({'x':x,'y':y,'wind':[vx,vy,vz],'vorticity':w,'wetness':wet,'roughness':.82-.64*wet,'reflectance':.04+.35*wet})
    speed=max(math.hypot(*s['wind'][:2]) for s in samples)
    return {'kind':'authored-game-effect','source_weather':None,'time':t,'samples':samples,'metrics':{'divergence_inf_s_1':max(div),'speed_max_m_s':speed,'wetness_min':wet,'wetness_max':wet,'cfl_dt_max_s':(radius/6)/max(speed,1e-12)},'material':{'dry':{'wetness':0,'roughness':.82,'reflectance':.04},'wet':{'wetness':1,'roughness':.18,'reflectance':.39}},'equations':{'wind':'v=(2+dpsi/dy,-dpsi/dx,0), psi=A(1-r^2/R^2)^3_+ sin(.8t)','wetness':'dm/dt=rain*(1-m)-.06*m'},'limitations':['analytic divergence-free compact swirl; not full atmospheric simulation or hazard forecast','material parameters require renderer/light-buffer verification'], 'witness_hash':_hash(samples)}


def overview():
    return {'version':VERSION,'operations':['box-qp','decay-ode','pure-game','negotiate','camera','weather'],'runtime':'bounded native C++ via C ABI','max_qp_variables':256,'max_ode_steps':100000,'max_game_actions':8,'state_mutation':False,'reference':'math/reference_octave.m'}


def run_benchmarks(output_dir='evidence'):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    build=build_native();(out/'math_native_build.json').write_text(json.dumps(build,indent=2)+'\n')
    native_cli=json.loads(subprocess.check_output([str(ROOT/'artifacts/native/worldloom-math'),'self-test'],text=True))
    p={'hessian_diagonal':[2,4],'linear':[-6,8],'lower':[0,-1],'upper':[2,3],'seed':7,'data_revision':'math-fixtures-v1'}
    qp=solve_box_qp(p);ode=solve_decay_ode({'rate':.7,'initial':3,'duration':4,'steps':400,'seed':7})
    octave=shutil.which('octave') or str(ROOT/'.cache/bin/octave')
    reference_path=out/'math_octave_reference.json'
    proc=subprocess.run([octave,'--quiet',str(ROOT/'math/reference_octave.m'),str(reference_path)],capture_output=True,text=True,timeout=60)
    if proc.returncode: raise RuntimeError(proc.stderr)
    ref=json.loads(reference_path.read_text())
    delta_qp=max(abs(a-b) for a,b in zip(qp['primal'],ref['qp']['primal']))
    delta_ode=abs(ode['primal'][0]-ref['ode']['final'])
    cameras=[camera_trace({'fps':fps,'duration':6}) for fps in (24,30,60,90)]
    camera_records=[]
    base=cameras[0]['samples']
    for c in cameras:
        diffs=[]
        for i in range(7):
            s=min(c['samples'],key=lambda s:abs(s['time']-i)); b=min(base,key=lambda s:abs(s['time']-i));diffs.append(abs(s['x']-b['x']))
        c['metrics']['common_time_path_error_m']=max(diffs)
        camera_records.append({'fps':c['fps'],'metrics':c['metrics'],'baseline':c['baseline'],'witness_hash':c['witness_hash']})
        (out/f'math_camera_{c["fps"]}fps.json').write_text(json.dumps(c,indent=2)+'\n')
    weather=weather_field({'time':2,'rain':.4,'initial_wetness':.1})
    (out/'math_weather_field.json').write_text(json.dumps(weather,indent=2)+'\n')
    # Timings exclude compilation/import and are CPU fixture measurements, not UE thread traces.
    durations=[]
    for i in range(200):
        start=time.perf_counter_ns();solve_box_qp(p);durations.append((time.perf_counter_ns()-start)/1e6)
    report={'environment':{'platform':platform.platform(),'processor':platform.processor(),'python':platform.python_version(),'cpu_count':os.cpu_count()},'reference':ref,'runtime':{'qp':qp,'ode':ode,'cli':native_cli},'comparison':{'qp_primal_max_abs':delta_qp,'ode_final_abs':delta_ode,'tolerance':1e-8,'pass':delta_qp<=1e-8 and delta_ode<=1e-8},'camera':camera_records,'weather':weather['metrics'],'negotiation':negotiation_cases(),'performance':{'qp_cpu_p50_ms':_percentile(durations,.5),'qp_cpu_p95_ms':_percentile(durations,.95),'qp_cpu_max_ms':max(durations),'trials':len(durations),'scope':'native kernel through Python wrapper; not game-thread measurement'},'reference_sha256':hashlib.sha256(reference_path.read_bytes()).hexdigest(),'limitations':['A06 engine foreground thread budget requires UE runtime trace','V06 occlusion, collision with scene meshes, image horizon and network jitter require rendered-engine verification','V09 vector field is exported; genuine Niagara/material light response requires UE runtime verification']}
    report['witness_hash']=_hash(report)
    (out/'math_benchmarks.json').write_text(json.dumps(report,indent=2)+'\n')
    findings=[
        {'id':'MATH-01','label':'M','hypothesis':'Native separable convex QP agrees with independent Octave qp','status':'accepted' if delta_qp<=1e-8 else 'rejected','observed':delta_qp,'threshold':1e-8,'fixture':'math/reference_octave.m','witness':str(out/'math_benchmarks.json')},
        {'id':'MATH-02','label':'M','hypothesis':'Bounded RK4 agrees with adaptive Octave ode45','status':'accepted' if delta_ode<=1e-8 else 'rejected','observed':delta_ode,'threshold':1e-8,'fixture':'math/reference_octave.m'},
        {'id':'MATH-03','label':'C','hypothesis':'Finite games always have a pure equilibrium','status':'rejected','counterexample':solve_game({'row':[[1,-1],[-1,1]],'column':[[-1,1],[1,-1]]}),'next_experiment':'add an independently verified mixed-strategy solver'},
        {'id':'MATH-04','label':'M','hypothesis':'Fixed lattice bounded controller reduces jerk over direct-follow synthetic track at all tested display rates','status':'accepted' if all(c['metrics']['jerk_p99_m_s3']<c['baseline']['jerk_p99_m_s3'] for c in cameras) else 'rejected','observed':camera_records,'limitation':'no perceptual/scene occlusion conclusion'},
        {'id':'MATH-05','label':'M','hypothesis':'Analytic compact-support streamfunction has low finite-difference divergence','status':'accepted' if weather['metrics']['divergence_inf_s_1']<.002 else 'rejected','observed':weather['metrics'],'threshold':.002,'limitation':'does not establish full Navier-Stokes or real weather fidelity'}]
    (out/'math_findings.jsonl').write_text(''.join(json.dumps(f,sort_keys=True)+'\n' for f in findings))
    return report


if __name__=='__main__':
    print(json.dumps(run_benchmarks(),indent=2))
