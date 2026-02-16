from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()

import time
from collections import defaultdict

# ---- IMPORT YOUR GAME CLASSES HERE ----
# SlimeVolleyball, Slime, Ball
# (Remove display(), keyboard stuff, cv2 usage)

from environments.soccer.Soccer import SoccerEnv  # assume you moved logic here

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store one game per client
games = {}

@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    games[request.sid] = SoccerEnv()
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
