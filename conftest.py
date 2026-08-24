# Ensures the repository root is importable so `import evaluation`, `import models`,
# and `import experiments` resolve when pytest is run from the repo root.
# (Root has no __init__.py, so pytest's default import mode already inserts it on
#  sys.path; this file just makes that guarantee explicit and stable.)
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
