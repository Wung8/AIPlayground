import os
import importlib
import inspect

from server.data.environments import get_env

environments_folder = "server/static/environments"
ENV_REGISTRY = {}

for file in os.listdir(environments_folder):
    if not file.endswith(".py"):
        continue
    env_name = file[:-3]
    env_info = get_env(env_name)
    if env_info is None:
        continue    
    module_path = f"server.static.environments.{env_name}"
    module = importlib.import_module(module_path)
    env_class = getattr(module, env_info["title"].replace(" ","")+"Env")
    ENV_REGISTRY[env_info["slug"]] = env_class

