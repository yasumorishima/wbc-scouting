#!/usr/bin/env python3
"""Run every app*.py once with Streamlit's AppTest, each in its own process
(apps share module names and caches, so one process gives false failures).
Exit 1 if any app raises."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ONE = """
import logging, sys
logging.disable(logging.CRITICAL)
from streamlit.testing.v1 import AppTest
at = AppTest.from_file(sys.argv[1], default_timeout=180).run()
exc = [str(getattr(e, "value", e))[:200] for e in at.exception]
print(exc if exc else "OK")
sys.exit(1 if exc else 0)
"""

bad = []
apps = sorted(ROOT.glob("app*.py"))
for app in apps:
    r = subprocess.run([sys.executable, "-c", ONE, str(app)], capture_output=True, text=True, cwd=ROOT)
    out = (r.stdout.strip().splitlines() or [r.stderr.strip()[-300:]])[-1]
    print(f"{'OK ' if r.returncode == 0 else 'NG '} {app.name}  {'' if r.returncode == 0 else out}")
    if r.returncode != 0:
        bad.append(app.name)
print(f"{len(apps) - len(bad)} OK, {len(bad)} NG")
sys.exit(1 if bad else 0)
