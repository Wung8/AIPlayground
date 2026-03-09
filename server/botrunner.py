import subprocess
import json
import os
import select

from server import app

class BotRunner:

    def __init__(self, bot, slug):
        path = os.path.join(
            app.root_path,
            "data",
            "user_uploads",
            bot.creator.username,
            slug,
            bot.name + ".py"
        )

        self.proc = subprocess.Popen(
            [
                "docker", "run",
                "--rm",
                "--network=none",
                "--memory=128m",
                "--cpus=0.25",
                "--pids-limit=64",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "-i",
                "-v", f"{path}:/bot/bot.py:ro",
                "bot_runner"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

    def getAction(self, inputs, timeout=0.5):
        try:
            self.proc.stdin.write(json.dumps(inputs) + "\n")
            self.proc.stdin.flush()

            line = self.proc.stdout.readline()

            if not line:
                return None

            return json.loads(line)

        except Exception as e:
            print("botrunner.py error:", e)

        return None

    def close(self):
        if self.proc:
            self.proc.kill()