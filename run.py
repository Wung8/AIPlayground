from server import app, socketio
# import app, socketio

if __name__ == "__main__":
    try:
        print("starting up website")
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt: # auto close docker containers
        for sid, (game, agents) in app.routes.games.items():
            for agent in agents:
                if hasattr(agent, "close"):
                    agent.close()
