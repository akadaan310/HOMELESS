"""Run from repository root: PYTHONPATH=portable python3 portable/verify_numerics.py."""
import csv
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile
from types import SimpleNamespace
import math
from dark.geo import ecef

def residual_for_rows(points, rows):
    if len(rows)!=len(points) or any(len(row)!=3 for row in rows): return None
    try:
        values=[list(map(float,row)) for row in rows]
        if not all(math.isfinite(x) for row in values for x in row): return None
        return max((math.dist(ecef(*point),row) for point,row in zip(points,values)),default=None)
    except (ValueError,TypeError): return None


def main():
    root=Path(__file__).resolve().parent
    rng=random.Random(20261021)
    points=[(-90,0,0),(90,180,0),(0,180,-430),(0,-180,8849),(0,0,0)]
    points += [(-90+180*(i+.5)/1000,rng.uniform(-180,180),rng.uniform(-430,12000)) for i in range(1000)]
    with tempfile.TemporaryDirectory(prefix='dark-wgs84-') as d:
        source=Path(d)/'input.csv'; target=Path(d)/'output.csv'
        with source.open('w') as f: csv.writer(f).writerows(points)
        try:
            run=subprocess.run(['octave','--no-gui','--quiet',str(root/'wgs84_reference.m'),str(source),str(target)],capture_output=True,text=True,timeout=30)
            version=subprocess.check_output(['octave','--no-gui','--version'],text=True,stderr=subprocess.STDOUT).splitlines()[0]
        except (OSError,subprocess.SubprocessError) as error:
            run=SimpleNamespace(returncode=127,stderr=str(error)); version=None
        rows=list(csv.reader(target.open())) if target.exists() else []
        residual=residual_for_rows(points,rows)
        result=dict(schema=1,clause_ids=['HD-016','HD-055','HD-087'],commission_revision='1.1',
                    commission_sha256='e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104',
                    method='WGS84 forward ECEF: Python math vs Octave vector arithmetic',seed=20261021,
                    units='meters',datum='WGS84 ellipsoid',samples=len(points),output_rows=len(rows),
                    input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None,
                    max_residual=residual,tolerance=1e-7,exit_code=run.returncode,
                    octave_version=version,
                    stderr=run.stderr,status='PASS' if run.returncode==0 and len(rows)==len(points) and residual is not None and residual<=1e-7 else 'FAIL')
        (root/'evidence'/'numerics.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(result,indent=2))
        raise SystemExit(0 if result['status']=='PASS' else 1)

if __name__=='__main__': main()
