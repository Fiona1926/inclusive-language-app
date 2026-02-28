#!/usr/bin/env python3
"""One-off debug: log Python and SQLAlchemy version, then attempt sqlalchemy import."""
import sys
LOG_PATH = "/Users/fionaleong/HTEbackend/.cursor/debug-f3ed7e.log"

def log(obj):
    import json
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(obj) + "\n")

# #region agent log
log({"hypothesisId": "H1", "message": "env_versions", "data": {"python": sys.version, "executable": sys.executable}, "runId": "debug_import"})
try:
    import sqlalchemy as sa
    log({"hypothesisId": "H1", "message": "sqlalchemy_ok", "data": {"version": getattr(sa, "__version__", "?")}, "runId": "debug_import"})
except Exception as e:
    log({"hypothesisId": "H1", "message": "sqlalchemy_import_failed", "data": {"type": type(e).__name__, "str": str(e)}, "runId": "debug_import"})
# #endregion
