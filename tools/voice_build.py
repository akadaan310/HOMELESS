#!/usr/bin/env python3
"""Explicit offline generation: never called on application startup."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from worldloom.voice import prepare_voice_catalog
import json
if __name__=='__main__':
    c=prepare_voice_catalog(force='--force' in sys.argv)
    print(json.dumps({'clips':len(c['clips']),'voices':c['voices'],'loads':c['model_loads']},indent=2))
