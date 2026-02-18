from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()

from data.environments import ENVIRONMENTS, get_env

from slimevolleyball import SlimeVolleyballEnv  # assume you moved logic here
from soccer import SoccerEnv
from SlimeAgent import BaseAgent

app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

agent = BaseAgent()

BOTS = [
    {"name": "epicbot", "elo": 1400, "by": "someone"},
    {"name": "basicbot25", "elo": 1000, "by": "wung8"},
    {"name": "another_bot2000", "elo": 600, "by": "wung8"},
]

# store one game per client (later: one per env per client)
games = {}

# pages
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/environments")
def environments():
    selected_slug = request.args.get("slug") or (ENVIRONMENTS[0]["slug"] if ENVIRONMENTS else "")
    return render_template(
        "environments.html",
        environments=ENVIRONMENTS,
        selected_slug=selected_slug,
    )

@app.route("/doc/<slug>")
def env_doc(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    if not env:
        return "missing env", 404
    return render_template("env_doc.html", env=env, environments=ENVIRONMENTS)

@app.route("/play/<slug>")
def play(slug):
    env = get_env(slug) or (ENVIRONMENTS[0] if ENVIRONMENTS else None)
    if not env:
        return "missing env", 404
    return render_template("play.html", env=env, bots=BOTS)

@app.route("/profile")
def profile():
    return render_template("profile.html")

# placeholders for navbar links you already show
@app.route("/acm")
def acm():
    return "acm page placeholder"

@app.route("/login")
def login():
    return "login page placeholder"

@app.route("/github")
def github():
    return "github placeholder"

@app.route("/discord")
def discord():
    return "discord placeholder"

@app.route("/contact")
def contact():
    return "contact placeholder"



@socketio.on("join_env")
def handle_connect(data):
    slug = data.get("env_slug")

    if slug == "soccer":
        games[request.sid] = SoccerEnv()
    elif slug == "slimevolleyball":
        games[request.sid] = SlimeVolleyballEnv()
    else:
        print("Unknown environment:", slug)
        return

    games[request.sid].reset()
    print(f"{request.sid} joined {slug}")


@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in games:
        del games[request.sid]
    print("Client disconnected")


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
