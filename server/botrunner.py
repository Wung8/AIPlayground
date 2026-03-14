import importlib.util
import subprocess
import json
import os
import threading
import queue
import sys
import time

from server import app


class BotRunner:
    default_action = [0 for i in range(10)]

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
                "--tmpfs", "/tmp:size=16m",
                "--tmpfs", "/run:size=16m",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--user", "1000:1000",
                "-i",
                "-v", f"{path}:/bot/bot.py:ro",
                "bot_runner"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True 
        )

        def read_stdout(q):
            while True:
                try:
                    line = self.proc.stdout.readline()
                    if not line and self.proc.poll() is not None:
                        break
                    q.put(line)
                except Exception as e:
                    q.put(None)

        self.read_queue = queue.Queue()
        self.read_thread = threading.Thread(target=read_stdout, args=(self.read_queue,), daemon=True)
        self.read_thread.start()
        '''
        def read_stderr(q):
            while True:
                line = self.proc.stderr.readline()
                if not line and self.proc.poll() is not None:
                    break
                q.put(line)

        self.err_queue = queue.Queue()
        threading.Thread(target=read_stderr, args=(self.err_queue,), daemon=True).start()
        '''

        self.buffer = [0 for i in range(20)]
        self.buffer_idx = 0

        self.timed_out_save = False

    def getAction(self, inputs):
        if 999 in self.buffer or self.proc.poll() is not None:
            if not self.timed_out_save:
                if self.proc.poll() is not None:
                    err = self.proc.stderr.read()
                    if err:
                        print("BOT STDERR:", err)
                else:
                    print("bot timed out")
            self.timed_out_save = True
            return self.default_action
        timeout = max(0.1, 0.1 * len(self.buffer) - sum(self.buffer))

        try:
            self.proc.stdin.write(json.dumps(inputs) + "\n")
            self.proc.stdin.flush()
            curr_time = time.time()

            try:
                line = self.read_queue.get(timeout=timeout)
            except queue.Empty:
                print("bot timed out")
                try:
                    self.proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.proc.kill()

                self.buffer[self.buffer_idx] = 999
                return self.default_action
            
            time_used = time.time() - curr_time
            self.buffer[self.buffer_idx] = time_used
            self.buffer_idx = self.buffer_idx + 1 if self.buffer_idx < len(self.buffer) - 1 else 0

            if not line:
                return self.default_action
            
            return json.loads(line)

        except Exception as e:
            print("botrunner.py error:", e)

        return self.default_action


    def close(self):
        if self.proc:
            self.proc.kill()