# based on https://github.com/minrk/nbstencilaproxy/blob/master/nbstencilaproxy/__init__.py
from nbo2rproxy.handlers import setup_handlers

# Jupyter Extension points
def _jupyter_server_extension_paths():
    return [{
        'module': 'nbo2rproxy',
    }]

def _jupyter_nbextension_paths():
    return [{
        "section": "tree",
        "dest": "nbo2rproxy",
        "src": "static",
        "require": "nbo2rproxy/tree"
    }]

def load_jupyter_server_extension(nbapp):
    setup_handlers(nbapp)
