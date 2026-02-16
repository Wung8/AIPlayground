from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()

import time
from collections import defaultdict

# ---- IMPORT YOUR GAME CLASSES HERE ----
# SlimeVolleyball, Slime, Ball
# (Remove display(), keyboard stuff, cv2 usage)

from environments.slimevolleyball.SlimeVolleyball import SlimeVolleyball  # assume you moved logic here

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
    games[request.sid] = SlimeVolleyball()
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
    obs, reward, done = game.step({"p1":"keyboard", "p2":"keyboard"}, keyboard=data['action'], display=False)

    state = {
        "left": {
            "x": game.slime_left.pos[0],
            "y": game.slime_left.pos[1]
        },
        "right": {
            "x": game.slime_right.pos[0],
            "y": game.slime_right.pos[1]
        },
        "ball": {
            "x": game.ball.pos[0],
            "y": game.ball.pos[1]
        },
        "score": game.score
    }

    emit("state", state)

    if done:
        game.reset()


if __name__ == "__main__":
    socketio.run(app, debug=True)
