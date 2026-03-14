import time
from server.environment_registry import ENV_REGISTRY
from server.botrunner import BotRunner
from server.models import Bot
from server import games, socketio
import sys

class GameRunner:
    def __init__(self, sid, data):
        slug = data.get("env_slug")
        difficulty = data.get("difficulty")
        player_names = data.get("players", [])

        if slug not in ENV_REGISTRY:
            print("Unknown environment:", slug)
            return

        # register this game
        games[sid] = self

        self.game = ENV_REGISTRY[slug](difficulty=difficulty)
        self.agents = []

        for i, name in enumerate(player_names):
            if name and name.lower() != "human":
                bot = Bot.query.filter_by(name=name).first()
                if bot:
                    runner = BotRunner(bot, slug)
                    self.agents.append(runner)
                else:
                    socketio.emit(
                        "bot_error",
                        {"message": f"P{i+1} bot '{name}' not found"},
                        to=sid
                    )
                    self.agents.append("human")
            else:
                self.agents.append("human")

        self.client_data = None
        self.stop_event = False

        # reset game
        self.game.reset()

        # start the game loop as a greenlet
        self.bg_task = socketio.start_background_task(self.gameloop, sid)

        print(f"{sid} joined {slug}")

    def set_client_data(self, data):
        self.client_data = data

    def close(self):
        self.stop_event = True

        if self.bg_task:
            self.bg_task.join()
        
        for agent in self.agents:
            if hasattr(agent, "close"):
                agent.close()

    def gameloop(self, sid):
        while not self.stop_event:
            socketio.sleep(1 / 20)  # 20 FPS

            if self.client_data is None:
                continue

            if sid not in games:
                break

            game = self.game
            agents = self.agents
            data = self.client_data

            actions = {}
            inputs = game.getInputs()

            for n, agent in enumerate(agents):
                pnum = f"p{n+1}"
                if pnum not in inputs:
                    continue
                if agent == "human":
                    actions[pnum] = "keyboard"
                else:
                    inp = inputs.get(pnum)
                    actions[pnum] = agent.getAction(inp)
                    if not isinstance(actions[pnum], (list, tuple)):
                        print("ERROR WITH BOT ACTION:", actions[pnum])
                        actions[pnum] = [0]*20

            _, _, done = game.step(
                actions=actions,
                keyboard=data.get("action", {}),
                display=False
            )
            state = game.getState()

            socketio.emit("state", state, to=sid)

            if done:
                game.reset()