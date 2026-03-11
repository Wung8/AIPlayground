import sys
import json
import traceback
import importlib.util

BOT_PATH = "/bot/bot.py"


def load_agent():
    try:
        #print("attempting to load agent")
        spec = importlib.util.spec_from_file_location("agent_module", BOT_PATH)
        #print(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module.Agent()
    except Exception as e:
        error("Failed to load bot", e)
        sys.exit(1)


def error(msg, e=None):
    out = {"error": msg}
    if e:
        out["trace"] = traceback.format_exc()
    print(json.dumps(out), file=sys.stderr)
    sys.stderr.flush()


def main():
    agent = load_agent()
    c = 0
    while True:
        c += 1
        line = sys.stdin.readline()

        if not line:
            break

        try:
            inputs = json.loads(line)
        except:
            error("Invalid JSON input")
            continue

        try:
            action = agent.getAction(inputs)

            print(json.dumps(action+[c]))
            sys.stdout.flush()

        except Exception as e:
            error("Bot crashed", e)


if __name__ == "__main__":
    main()