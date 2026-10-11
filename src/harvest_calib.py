#!/usr/bin/env python3
"""Shim: canonical copy is scripts/harvest_calib.py."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts' / 'harvest_calib.py'), run_name='__main__')
