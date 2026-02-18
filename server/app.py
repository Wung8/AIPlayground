from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

import json

from SlimeVolleyball import SlimeVolleyballEnv  # assume you moved logic here
from SlimeAgent import BaseAgent

app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

agent = BaseAgent()

BOTS = [
    {"name": "epicbot", "elo": 1400, "by": "someone"},
    {"name": "basicbot25", "elo": 1000, "by": "wung8"},
    {"name": "another_bot2000", "elo": 600, "by": "wung8"},
]

env_list = json.load(open('data/environments.json', 'r'))
env_by_slug = {env["slug"]: env for env in env_list}

# store one game per client (later: one per env per client)
games = {}

# pages
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/environments")
def environments():
    slug = request.args.get("slug")
    return render_template("environments.html", environments=env_list, selected_slug=slug)

@app.route("/doc/<slug>")
def env_doc(slug):
    env = env_by_slug[slug]
    if not env:
        return "missing env", 404
    return render_template("env_doc.html", env=env, environments=env_list)

@app.route("/play/<slug>")
def play(slug):
    env = env_by_slug[slug]
    if not env:
        return "missing env", 404
    return render_template("play.html", env=env, bots=BOTS)

@app.route("/profile")
def profile():
    return render_template("profile.html")



@socketio.on("connect")
def handle_connect():
    print("Client connected")
    games[request.sid] = SlimeVolleyballEnv()
    games[request.sid].reset()


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")
    games.pop(request.sid, None)


@socketio.on("input")
def handle_input(data):
    """
    data = {
        "action": 0/1/2/3
    }
    """
    game = games.get(request.sid)
    if not game:
        return

    obs = game.getInputs()
    obs, reward, done = game.step(
        actions={"p1":"keyboard", "p2":"keyboard", "p3":"keyboard", "p4":"keyboard"}, 
        keyboard=data['action'], 
        display=False
    )
    state = game.getState()

    emit("state", state)

    if done:
        game.reset()


if __name__ == "__main__":
    socketio.run(app, debug=True)
