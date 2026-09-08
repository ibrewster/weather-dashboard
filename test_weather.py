import http.server
import threading

from datetime import datetime,timedelta
import requests
from jinja2 import Environment, FileSystemLoader

def setup_jinja2():
    env = Environment(
        loader=FileSystemLoader("HTML"),
    )

    def states(entity_id):
        return obj_states.get(entity_id,{}).get('state')

    def state_attr(entity_id,attr):
        return obj_states.get(entity_id,{}).get('attributes',{}).get(attr)

    env.globals["now"] = datetime.now
    env.globals["timedelta"] = timedelta
    env.globals["states"] = states
    env.globals["state_attr"] = state_attr
    return env

env = setup_jinja2()

HA_URL = "http://conductor.brewstersoft.net"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MTU5Zjk0YTA2YTU0NmJjYmIyNGM5NGE4MjExODY1MyIsImlhdCI6MTc2MTY4NzcxNSwiZXhwIjoyMDc3MDQ3NzE1fQ.LavjahxRcnTuvnbYeRjQkDPNdY0QnT2GaRS_xWytI2k"

def get_ha_states():
    response = requests.get(
        f"{HA_URL}/api/states",
        headers={
            "Authorization": f"Bearer {HA_TOKEN}",
        },
        timeout=10,
    )
    response.raise_for_status()

    return {
        state["entity_id"]: state
        for state in response.json()
    }

obj_states=get_ha_states()

def dashboard()->str:
    template = env.get_template('dashboard.jinja2')
    return template.render()

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='HTML', **kwargs)

    def do_GET(self):
        if self.path == "/":
            content = dashboard().encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        # Everything else comes from static/
        super().do_GET()

def start_static_server(port:int=0, threaded:bool=True):
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", port),
        DashboardHandler,
    )

    if threaded:
        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )
        thread.start()
    else:
        server.serve_forever()

    return server

if __name__ == "__main__":
    start_static_server(8000,threaded=False)