# based on https://github.com/minrk/nbstencilaproxy/blob/master/nbstencilaproxy/handlers.py
import os

from tornado import web
from urllib.parse import urlunparse, urlparse
from notebook.base.handlers import IPythonHandler
from nbserverproxy.handlers import SuperviseAndProxyHandler

here = os.path.dirname(os.path.abspath(__file__))

class AddSlashHandler(IPythonHandler):
    """Handler for adding trailing slash to URLs that need them"""

    @web.authenticated
    def get(self, *args):
        src = urlparse(self.request.uri)
        dest = src._replace(path=src.path + "/")
        self.redirect(urlunparse(dest))

def _find_o2r_js(name):
    """Find a .js file in the bundled npm package"""
    return os.path.join(here, "node_modules", "nbo2rproxy", name)


# define our proxy handler for proxying the application
class O2rUiProxyHandler(SuperviseAndProxyHandler):

    name = "o2r-ui"

    def get_env(self):
        return {"O2R_UI_PORT": str(self.port), "BASE_URL": self.state["base_url"]}

    def get_cmd(self):
        return ["node", _find_o2r_js("ui.js")]

class O2rApiProxyHandler(SuperviseAndProxyHandler):

    name = "o2r-api"

    def get_env(self):
        return {"O2R_API_PORT": str(self.port)}

    def get_cmd(self):
        return ["node", _find_o2r_js("api.js")]

    def proxy_request_options(self):
        """Increase the request timeout"""
        options = super().proxy_request_options()
        options.update(dict(
            request_timeout=3600
        ))
        return options

def setup_handlers(app):
    app.log.info("Enabling o2r proxy")
    app.web_app.add_handlers(
        ".*",
        [
            (
                app.base_url + "o2r-ui/(.*)",
                O2rUiProxyHandler,
                dict(state=dict(base_url=app.base_url, notebook_dir=app.notebook_dir)),
            ),
            (
                app.base_url + "o2r-api/(.*)",
                O2rApiProxyHandler,
                dict(state=dict(base_url=app.base_url, notebook_dir=app.notebook_dir)),
            ),
            (app.base_url + "o2r-ui", AddSlashHandler),
            (app.base_url + "o2r-api", AddSlashHandler),
        ],
    )
