from server import app, socketio, games

if __name__ == "__main__":
    print("starting up website")
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        async_mode='threading',
        debug=False,
        use_reloader=False
    )
