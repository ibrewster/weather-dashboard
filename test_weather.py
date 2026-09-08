from flask import Flask
from datetime import datetime,timedelta
import requests
from jinja2 import Environment, FileSystemLoader


app = Flask(__name__)

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

@app.route("/")
def dashboard():
    template = env.get_template('dashboard.jinja2')
    return template.render()


if __name__ == "__main__":
    app.run(debug=True, port=8000)