import sys
# This is the trick: we tell Python that 'imghdr' exists even though it's gone
try:
    import imghdr
except ImportError:
    import types
    sys.modules['imghdr'] = types.ModuleType('imghdr')
    sys.modules['imghdr'].what = lambda filename, h=None: None

# Now run your actual app
import subprocess
subprocess.run(["streamlit", "run", "app.py"])
