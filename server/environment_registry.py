import os
import json
import importlib
from functools import lru_cache

from markupsafe import Markup

import markdown as md

BASE_DIR = os.path.dirname(__file__)  # server/
DATA_DIR = os.path.join(BASE_DIR, "data")
ENVIRONMENTS_JSON = os.path.join(DATA_DIR, "environments.json")
ENV_DOCS_DIR = os.path.join(DATA_DIR, "descriptions")

ENV_REGISTRY = {}


@lru_cache(maxsize=1)
def load_environments():
    if not os.path.exists(ENVIRONMENTS_JSON):
        return []

    with open(ENVIRONMENTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return []

    # normalize slugs
    for e in data:
        if isinstance(e, dict) and isinstance(e.get("slug"), str):
            e["slug"] = e["slug"].strip().lower()

    return data


# keep this name so routes.py can keep using it
ENVIRONMENTS = load_environments()

def get_env(slug: str):
    s = (slug or "").strip().lower()
    for e in ENVIRONMENTS:
        if e.get("slug") == s:
            return e
    return None


def _doc_path(slug: str):
    s = (slug or "").strip().lower()
    print(os.path.join(ENV_DOCS_DIR, f"{s}.md"))
    return os.path.join(ENV_DOCS_DIR, f"{s}.md")


def load_env_doc_markdown(slug: str):
    path = _doc_path(slug)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def render_env_doc_html(slug: str):
    raw = load_env_doc_markdown(slug)
    if not raw:
        print('not raw')
        return Markup("")

    if md is None:
        print('not md')
        return Markup("")
    print('good')

    html = md.markdown(
        raw,
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            "sane_lists",
        ],
        output_format="html5",
    )

    return Markup(f'<div class="env-md">{html}</div>')


def _build_env_registry():
    environments_folder = os.path.join(BASE_DIR, "static", "environments")
    if not os.path.isdir(environments_folder):
        return {}

    reg = {}

    for file in os.listdir(environments_folder):
        if not file.endswith(".py"):
            continue
        if file.startswith("_"):
            continue

        env_name = file[:-3]  # module name (usually matches slug)
        env_info = get_env(env_name)
        if env_info is None:
            continue

        module_path = f"server.static.environments.{env_name}"
        module = importlib.import_module(module_path)

        class_name = (env_info.get("title", "").replace(" ", "") + "Env").strip()
        if not class_name:
            continue

        env_class = getattr(module, class_name, None)
        if env_class is None:
            continue

        reg[env_info["slug"]] = env_class

    return reg


ENV_REGISTRY = _build_env_registry()