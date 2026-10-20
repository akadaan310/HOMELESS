"""Measured HYG sky with bounded motif mining and explicit approximation masks.

Source positions are immutable J2000.0 catalog values.  Fictional overlays never
change these values.  This small catalog is a regression fixture, not Gaia.
"""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import math
import time

import numpy as np

DATA = Path(__file__).resolve().parents[1] / 'data' / 'sky'
MAS_TO_RAD = math.pi / (180 * 3_600_000)


def unit_vector(ra_deg, dec_deg):
    """ICRS-like equatorial unit vectors; RA wrap and poles need no branches."""
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    return np.stack((np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)), axis=-1)


def angular_separation(u, v):
    """Stable great-circle separation in radians, including very small angles."""
    return np.arctan2(np.linalg.norm(np.cross(u, v), axis=-1), np.sum(np.asarray(u)*v, axis=-1))


def propagate(position, tangent_velocity, years):
    """Constant angular-speed great-circle transport; returns position and tangent.

    This invertible approximation ignores radial-velocity perspective effects.
    Tangent units are radians/year, unlike catalog proper motions (mas/year).
    """
    u = np.asarray(position, dtype=float)
    u = u / np.linalg.norm(u, axis=-1, keepdims=True)
    v = np.asarray(tangent_velocity, dtype=float)
    v = v - np.sum(v*u, axis=-1, keepdims=True)*u
    speed = np.linalg.norm(v, axis=-1, keepdims=True)
    t = np.divide(v, speed, out=np.zeros_like(v), where=speed > 0)
    angle = speed*float(years)
    return np.cos(angle)*u + np.sin(angle)*t, speed*(-np.sin(angle)*u + np.cos(angle)*t)


def _datetime(at):
    if isinstance(at, datetime):
        t = at
    elif at is None:
        t = datetime(2026, 10, 20, 2, tzinfo=timezone.utc)
    else:
        t = datetime.fromisoformat(str(at).replace('Z', '+00:00'))
    if t.tzinfo is None:
        raise ValueError('UTC offset is required')
    return t.astimezone(timezone.utc)


def gmst_deg(at):
    """IAU 1982 GMST, treating UTC as UT1 (sub-arcminute game approximation)."""
    jd = _datetime(at).timestamp()/86400 + 2440587.5
    T = (jd-2451545.0)/36525
    return (280.46061837 + 360.98564736629*(jd-2451545.0) + .000387933*T*T - T*T*T/38710000) % 360


def horizontal(ra_deg, dec_deg, lat, lon, at):
    """Geometric altitude/azimuth; east-positive longitude; azimuth north=0."""
    if not -90 <= float(lat) <= 90 or not math.isfinite(float(lon)):
        raise ValueError('invalid observer coordinates')
    H = np.radians((gmst_deg(at)+float(lon)-np.asarray(ra_deg)) % 360)
    d, p = np.radians(dec_deg), math.radians(float(lat))
    sinalt = np.sin(d)*math.sin(p)+np.cos(d)*math.cos(p)*np.cos(H)
    alt = np.degrees(np.arcsin(np.clip(sinalt,-1,1)))
    az = np.degrees(np.arctan2(-np.sin(H)*np.cos(d), np.sin(d)*math.cos(p)-np.cos(d)*math.sin(p)*np.cos(H))) % 360
    return alt, az


def precess(vectors, year):
    """IAU 1976 J2000->mean equinox of year rotation; no nutation/aberration."""
    T = (float(year)-2000)/100
    zeta = math.radians((2306.2181*T + .30188*T*T + .017998*T**3)/3600)
    z = math.radians((2306.2181*T + 1.09468*T*T + .018203*T**3)/3600)
    theta = math.radians((2004.3109*T - .42665*T*T - .041833*T**3)/3600)
    def rz(a):
        c,s=math.cos(a),math.sin(a)
        return np.array([[c,-s,0],[s,c,0],[0,0,1]])
    c,s=math.cos(theta),math.sin(theta)
    ry = np.array([[c,0,-s],[0,1,0],[s,0,c]])
    rotation = rz(z) @ ry @ rz(zeta)
    return np.asarray(vectors) @ rotation.T


class Catalog:
    """One immutable 119k-row catalog and a 5-degree spatial index.

    A query visits declination/RA cells intersecting its spherical cap, then
    applies exact dot-product filtering.  No dense all-pairs sky graph is kept.
    """
    def __init__(self, arrays=None):
        if arrays is None:
            with np.load(DATA/'catalog.npz', allow_pickle=False) as f:
                arrays = {k:f[k] for k in f.files}
        self.arrays = arrays
        self.ra, self.dec = arrays['ra'], arrays['dec']
        self.vectors = unit_vector(self.ra,self.dec)
        cells = np.floor((self.dec+90)/5).astype(int).clip(0,35)*72 + np.floor(self.ra%360/5).astype(int)
        ordering = np.argsort(cells, kind='stable')
        keys,starts,counts=np.unique(cells[ordering],return_index=True,return_counts=True)
        self.cells = {int(k):ordering[s:s+n] for k,s,n in zip(keys,starts,counts)}
        for a in self.arrays.values():
            a.setflags(write=False)
        self.vectors.setflags(write=False)

    def query_cone(self, ra_deg, dec_deg, radius_deg):
        ra,dec,r=float(ra_deg)%360,float(dec_deg),float(radius_deg)
        if not -90<=dec<=90 or not 0<=r<=180:
            raise ValueError('invalid sky cone')
        lo,hi=max(-90,dec-r),min(90,dec+r)
        db0,db1=max(0,int((lo+90)//5)),min(35,int((hi+90)//5))
        if lo<=-90 or hi>=90 or r>=90:
            rabins=range(72)
        else:
            width=math.degrees(math.asin(min(1,math.sin(math.radians(r))/math.cos(math.radians(dec)))))
            rabins={i%72 for i in range(math.floor((ra-width)/5),math.floor((ra+width)/5)+1)}
        groups=[self.cells[d*72+a] for d in range(db0,db1+1) for a in rabins if d*72+a in self.cells]
        if not groups:
            return np.array([],dtype=int)
        candidates=np.concatenate(groups)
        return candidates[self.vectors[candidates]@unit_vector(ra,dec)>=math.cos(math.radians(r))-1e-15]

    def positions(self, epoch=2000.0, equinox=None):
        if not 1900<=float(epoch)<=2100:
            raise ValueError('epoch outside guarded 1900–2100 approximation')
        a,d=np.radians(self.ra),np.radians(self.dec)
        era=np.stack((-np.sin(a),np.cos(a),np.zeros_like(a)),axis=-1)
        edec=np.stack((-np.sin(d)*np.cos(a),-np.sin(d)*np.sin(a),np.cos(d)),axis=-1)
        tangent=(self.arrays['pmra'][:,None]*era+self.arrays['pmdec'][:,None]*edec)*MAS_TO_RAD
        moved,_=propagate(self.vectors,tangent,float(epoch)-2000)
        return precess(moved,equinox) if equinox is not None else moved


@lru_cache(maxsize=1)
def catalog():
    return Catalog()


@lru_cache(maxsize=1)
def _source():
    return json.loads((DATA/'source.json').read_text())


def overview():
    result=dict(_source())
    result.update(status='ok',frame='J2000 equatorial source; mean equinox of date for observer',
                  index={'scheme':'5-degree RA/declination cells, exact angular cap filter','resident_catalogs':1,'query_result_limit':2000},
                  quality_mask={'source_positions':'confirmed_factual','astrometry':'approximate_inference','weather':'incomplete','fictional_overlay':'separate'},
                  reliable_epoch_range=[1900,2100],gaia_scale=False)
    return result



def body_reference(body='Sun', at=None):
    """Replay a pinned Horizons result; missing dates remain explicitly absent.

    These are geocentric ICRF reference ephemerides, not topocentric predictions.
    No interpolation is performed between the two sourced sample instants.
    """
    target=str(body).title()
    stamp=_datetime(at).isoformat()
    references=json.loads((DATA/'horizons_references.json').read_text())
    for row in references['records']:
        if row['body']==target and row['at']==stamp:
            return dict(row,status='ok',quality_mask='confirmed_factual_reference')
    return {'status':'unsupported','body':target,'at':stamp,'quality_mask':'incomplete',
            'reason':references['coverage']}


def observer(lat=27.95, lon=-82.5, at=None, epoch=None, max_mag=6.5, limit=100, height_m=0):
    t=_datetime(at)
    year=t.year+(t-datetime(t.year,1,1,tzinfo=timezone.utc)).total_seconds()/((datetime(t.year+1,1,1,tzinfo=timezone.utc)-datetime(t.year,1,1,tzinfo=timezone.utc)).total_seconds())
    epoch=year if epoch is None else float(epoch)
    if not 1900<=epoch<=2100 or not 1900<=year<=2100:
        raise ValueError('epoch outside guarded 1900–2100 approximation')
    if not math.isfinite(float(height_m)) or not -1000<=float(height_m)<=1_000_000:
        raise ValueError('invalid observer height')
    c=catalog()
    vectors=c.positions(epoch,equinox=year)
    ra=np.degrees(np.arctan2(vectors[:,1],vectors[:,0]))%360
    dec=np.degrees(np.arcsin(vectors[:,2].clip(-1,1)))
    alt,az=horizontal(ra,dec,lat,lon,t)
    horizon=-math.degrees(math.acos(6371008.8/(6371008.8+max(0,float(height_m)))))
    visible=np.flatnonzero((alt>horizon)&(c.arrays['mag']<=float(max_mag)))
    order=visible[np.argsort(c.arrays['mag'][visible],kind='stable')]
    count=len(order)
    order=order[:max(0,min(2000,int(limit)))]
    labels=json.loads((DATA/'benchmark_labels.json').read_text())
    stars=[{'source_id':f"hyg:{int(c.arrays['id'][i])}",'name':labels.get(str(int(c.arrays['id'][i])),{}).get('name',''),
            'ra_deg':float(ra[i]),'dec_deg':float(dec[i]),'source_ra_deg':float(c.ra[i]),'source_dec_deg':float(c.dec[i]),
            'magnitude':float(c.arrays['mag'][i]),'altitude_deg':float(alt[i]),'azimuth_deg':float(az[i]),
            'unit_vector':[float(x) for x in vectors[i]]} for i in order]
    bodies=[]
    for name in ('Sun','Moon'):
        body=body_reference(name,t)
        if body['status']=='ok':
            bv=precess(unit_vector(body['ra_deg'],body['dec_deg']),year)
            bra=math.degrees(math.atan2(bv[1],bv[0]))%360
            bdec=math.degrees(math.asin(float(bv[2])))
            ba,bz=horizontal(bra,bdec,lat,lon,t)
            body.update(altitude_deg=float(ba),azimuth_deg=float(bz),
                        horizon_quality='approximate geocentric direction; lunar topocentric parallax omitted')
        bodies.append(body)
    return {'status':'ok','source_catalog':'HYG','source_release':'4.1','source_sha256':_source()['source_sha256'],
            'solar_system':bodies,'observer_coords':{'lat':float(lat),'lon':(float(lon)+180)%360-180,'height_m':float(height_m)},
            'at':t.isoformat(),'epoch':epoch,'equinox':year,'visible_count':count,'returned_count':len(stars),'stars':stars,
            'geometric_horizon_deg':horizon,'quality_mask':overview()['quality_mask'],
            'method':'HYG proper-motion geodesic + IAU1976 precession + IAU1982 GMST; UTC approximates UT1',
            'uncertainty':'Game-scale mean positions, not precision apparent astrometry; refraction/nutation/aberration/parallax omitted.',
            'weather_mask':'unknown; visibility is geometric only','fictional_overlay':None}


def _mine(vectors, magnitudes):
    """Labels/IDs are intentionally unavailable to this geometric candidate miner."""
    dots=np.clip(vectors@vectors.T,-1,1)
    np.fill_diagonal(dots,-1)
    nearest=np.argpartition(-dots,3,axis=1)[:,:3]
    groups=np.column_stack((np.arange(len(vectors)),nearest))
    # Score brightness and compactness, rewarding a non-collapsed angular shape.
    pts=vectors[groups]
    pairs=np.array([(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)])
    angles=np.arctan2(np.linalg.norm(np.cross(pts[:,pairs[:,0]],pts[:,pairs[:,1]]),axis=-1),np.sum(pts[:,pairs[:,0]]*pts[:,pairs[:,1]],axis=-1))
    span=angles.max(axis=1)
    shape=angles.min(axis=1)/np.maximum(span,1e-12)
    brightness=np.mean(4.5-magnitudes[groups],axis=1)
    scores=brightness*np.exp(-span/math.radians(12))*(.5+.5*np.sqrt(shape))
    valid=(span>math.radians(.3))&(span<math.radians(25))
    scores=np.where(valid,scores,-1)
    best=int(np.argmax(scores))
    return np.sort(groups[best]),float(scores[best]),angles[best]


@lru_cache(maxsize=8)
def _discover_cached(seed, null_trials, max_mag):
    started=time.perf_counter()
    c=catalog()
    selected=np.flatnonzero(c.arrays['mag']<=max_mag)
    # Fixed brightness threshold and motif size are chosen before null generation.
    v,mag=c.vectors[selected],c.arrays['mag'][selected]
    group,score,_=_mine(v,mag)
    indices=selected[group]
    ids=[f"hyg:{int(c.arrays['id'][i])}" for i in indices]
    # Freeze discovery before reading any historical naming field.
    frozen=sha256(json.dumps({'star_ids':ids,'score':score,'algorithm':'nearest3-brightness-compactness-v1'},sort_keys=True).encode()).hexdigest()
    def null_scores(null_seed):
        rng=np.random.default_rng(null_seed)
        scores=[]
        for _ in range(null_trials):
            # Conditional null preserves magnitudes and declination distribution.
            random_v=unit_vector(rng.uniform(0,360,len(selected)),c.dec[selected])
            scores.append(_mine(random_v,mag)[1])
        return scores
    training=null_scores(seed)
    heldout_seed=seed+104729
    heldout=null_scores(heldout_seed)
    p=(1+sum(s>=score for s in heldout))/(null_trials+1)
    threshold=float(np.quantile(training,.95))
    pairs=[(i,j) for i in range(4) for j in range(i+1,4)]
    edges=[{'from':ids[i],'to':ids[j],'angle_rad':float(angular_separation(c.vectors[indices[i]],c.vectors[indices[j]]))} for i,j in pairs]
    signature=sorted(e['angle_rad'] for e in edges)
    signature=[x/max(signature) for x in signature]
    # Historical labels are loaded only now, after candidate/hash/calibration freeze.
    labels=json.loads((DATA/'benchmark_labels.json').read_text())
    con=[labels.get(str(int(c.arrays['id'][i])),{}).get('constellation','') for i in indices]
    counts={key:con.count(key) for key in set(con) if key}
    label=max(counts,key=counts.get) if counts else None
    overlap=counts.get(label,0)/len(indices)
    template_meta=json.loads((DATA/'template_source.json').read_text())
    templates=json.loads((DATA/'known_templates.json').read_text())['constellations']
    discovered_hips={int(labels.get(str(int(c.arrays['id'][i])),{}).get('hip') or -1) for i in indices}
    choices=[]
    for template in templates:
        vertices={int(hip) for line in template['lines'] for hip in line}
        shared=vertices & discovered_hips
        precision=len(shared)/len(discovered_hips)
        recall=len(shared)/len(vertices) if vertices else 0
        choices.append((precision,recall,template['id'],template,vertices))
    precision,recall,_,template,vertices=max(choices,key=lambda x:x[:3])
    template_edges={tuple(sorted((int(a),int(b)))) for line in template['lines'] for a,b in zip(line,line[1:])}
    recovered=sum(a in discovered_hips and b in discovered_hips for a,b in template_edges)
    benchmark={'method':'post-freeze observed Hipparcos ID overlap with sourced traditional line-art vertices and edges',
               'catalog_region':label,'membership_precision':overlap,
               'template_source':template_meta['template_source'],'template_source_sha256':template_meta['template_source_sha256'],
               'template_source_revision':template_meta['revision'],'template_lookup_after_freeze_hash':frozen,
               'template_id':template['id'],'template_name':template.get('common_name',{}).get('english',''),
               'template_hip_ids':sorted(vertices),'star_precision':precision,'star_recall':recall,
               'traditional_edges_recovered':recovered,'traditional_edge_count':len(template_edges),
               'traditional_shape_match':'exact_vertex_agreement' if precision==1 and recall==1 else ('partial_vertex_agreement' if precision>0 else 'no_match'),
               'names':[labels.get(str(int(c.arrays['id'][i])),{}).get('name','') for i in indices],
               'result':'source star overlap is measured; candidate edges were independently constructed and are not a recovered traditional drawing'}
    stable=[]
    original=c.vectors[indices]
    for y in [1900,2000,2100]:
        epoch_vectors=c.positions(y)
        moved=epoch_vectors[indices]
        epoch_group,_,_=_mine(epoch_vectors[selected],mag)
        epoch_ids=[f"hyg:{int(c.arrays['id'][i])}" for i in selected[epoch_group]]
        a=[float(angular_separation(original[i],original[j])) for i,j in pairs]
        b=[float(angular_separation(moved[i],moved[j])) for i,j in pairs]
        stable.append({'epoch':y,'maximum_edge_drift_arcsec':math.degrees(max(abs(x-y) for x,y in zip(a,b)))*3600,
                       'selected_winner_star_ids':epoch_ids,'winner_identity_stable':epoch_ids==ids})
    return {'status':'ok','pattern_id':f'purl://dark/sky/pattern/{frozen[:20]}','source_catalog':'HYG','source_release':'4.1',
            'source_sha256':_source()['source_sha256'],'epoch':2000,'observer_coords':None,'star_ids':ids,'angular_edges':edges,
            'pattern_signature':signature,'score':score,'p_value':p,'content_hash':frozen,'discovery_freeze_hash':frozen,
            'algorithm':'nearest3-brightness-compactness-v1','candidate_count':len(selected),'motif_size':4,
            'null_model':'RA randomized independently, conditioned on observed declination and magnitude; rerun full maximum search',
            'calibration':{'selection_adjusted':True,'training_seed':seed,'heldout_seed':heldout_seed,'training_trials':null_trials,
                           'heldout_trials':null_trials,'training_95_percentile':threshold,'training_max_scores':training,'heldout_max_scores':heldout,
                           'decision':'rare_under_conditional_null' if p<=.05 and score>threshold else 'negative_or_inconclusive',
                           'false_discovery_control':'one preselected winning motif; empirical plus-one familywise maximum-statistic rank'},
            'known_template_compared_after_discovery':True,'benchmark':benchmark,'epoch_stability':stable,
            'quality_mask':{'source':'confirmed_factual','edges':'constructed','calibration':'conditional_model','traditional_shape_match':benchmark['traditional_shape_match']},
            'elapsed_ms':(time.perf_counter()-started)*1000,'display_projection_hash':None,
            'limitations':['Small HYG fixture, not Gaia discovery.','Conditional RA null does not model all Milky Way structure.','Partial source-star template agreement does not establish recovered traditional line geometry.']}


def discover(seed=42, null_trials=99, max_mag=3.8):
    """Mine first, freeze source-ID witness, calibrate heldout, benchmark last."""
    if not 9<=int(null_trials)<=499:
        raise ValueError('null_trials must be 9–499')
    if not 1<=float(max_mag)<=4.5:
        raise ValueError('max_mag must be 1–4.5 for bounded mining')
    # Return independent JSON objects so callers cannot mutate cached evidence.
    return json.loads(json.dumps(_discover_cached(int(seed),int(null_trials),float(max_mag))))
