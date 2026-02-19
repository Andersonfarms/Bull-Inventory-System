import sys
try:
    import imghdr
except ImportError:
    import types
    sys.modules['imghdr'] = types.ModuleType('imghdr')
    sys.modules['imghdr'].what = lambda filename, h=None: None

import subprocess
subprocess.run(["streamlit", "run", "app.py"])
