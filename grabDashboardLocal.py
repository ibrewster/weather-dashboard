import http.server
import subprocess
import threading

from functools import cache

from datetime import datetime,timedelta
import requests
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

def setup_jinja2():
    env = Environment(
        loader=FileSystemLoader("HTML"),
    )
    def states(entity_id):
        obj_states=get_ha_states()
        return obj_states.get(entity_id,{}).get('state')

    def state_attr(entity_id,attr):
        obj_states=get_ha_states()
        return obj_states.get(entity_id,{}).get('attributes',{}).get(attr)

    env.globals["now"] = datetime.now
    env.globals["timedelta"] = timedelta
    env.globals["states"] = states
    env.globals["state_attr"] = state_attr
    return env

HA_URL = "http://conductor.brewstersoft.net"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MTU5Zjk0YTA2YTU0NmJjYmIyNGM5NGE4MjExODY1MyIsImlhdCI6MTc2MTY4NzcxNSwiZXhwIjoyMDc3MDQ3NzE1fQ.LavjahxRcnTuvnbYeRjQkDPNdY0QnT2GaRS_xWytI2k"
KINDLE_WIDTH = 600
KINDLE_HEIGHT = 939

IMG_PATH = "/tmp/dashboard.png"
KINDLE_HOST = "root@192.168.15.244"
KINDLE_IMG_PATH = "/mnt/us/dashboard.png"
KINDLE_SCRIPT = "/mnt/us/show_dashboard.sh"

@cache
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

def dashboard()->str:
    env = setup_jinja2()
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

def render_dashboard():
    server = start_static_server()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page(
                viewport={
                    "width": KINDLE_WIDTH,
                    "height": KINDLE_HEIGHT,
                },
                device_scale_factor=1,
            )

            page.goto(
                f"http://127.0.0.1:{server.server_port}/",
                wait_until="networkidle",
            )

            page.screenshot(
                path=IMG_PATH,
                full_page=False,
            )

            browser.close()

    finally:
        if server:
            server.shutdown()
            server.server_close()

if __name__ == "__main__":
    render_dashboard()
    # === PUSH TO KINDLE ===
    subprocess.run(["/usr/bin/convert", "/tmp/dashboard.png", "-colorspace", "Gray", "/tmp/dashboard-gray.png"])
    subprocess.run(["scp", "/tmp/dashboard-gray.png", f"kindle:{KINDLE_IMG_PATH}"])
    #subprocess.run(["ssh", "kindle", "eips -c"])
    subprocess.run(["ssh", "kindle", f"eips -g {KINDLE_IMG_PATH}"])

print("Dashboard updated and pushed to Kindle.")