# backend/data/environments.py

ENVIRONMENTS = [
    {
        "slug": "slimevolleyball",
        "title": "Slime Volleyball",
        "num_players": 2,
        "difficulty": 3,
        "description": "Classic slime volleyball environment.",
        "docSections": [
            {"title": "Observation Space", "items": ["slime positions", "ball position", "ball velocity"]},
            {"title": "Action Space", "items": ["left/right movement", "jump"]},
        ],
        "image": {"kind": "placeholder", "value": "slime"},
    },
    {
        "slug": "soccer",
        "title": "Soccer",
        "num_players": 4,
        "difficulty": 4,
        "description": "Play 2v2 soccer.",
        "docSections": [
            {"title": "Goal", "items": ["reach the exit", "avoid traps"]},
        ],
        "image": {"kind": "placeholder", "value": "soccer"},
    },
    {
        "slug": "maze",
        "title": "Maze",
        "num_players": 1,
        "difficulty": 2,
        "description": "Navigate a maze to reach the goal.",
        "docSections": [
            {"title": "Goal", "items": ["reach the exit", "avoid traps"]},
        ],
        "image": {"kind": "placeholder", "value": "maze"},
    },
    {
        "slug": "pong",
        "title": "Pong",
        "num_players": 2,
        "difficulty": 1,
        "description": "Pong decsription.",
        "docSections": [
            {"title": "Goal", "items": ["reach the exit", "avoid traps"]},
        ],
        "image": {"kind": "placeholder", "value": "maze"},
    },
    {
        "slug": "sliderpuzzle",
        "title": "Slider Puzzle",
        "num_players": 1,
        "difficulty": 3,
        "description": "Slider Puzzle decsription.",
        "docSections": [
            {"title": "Goal", "items": ["reach the exit", "avoid traps"]},
        ],
        "image": {"kind": "placeholder", "value": "maze"},
    },
    {
        "slug": "sudoku",
        "title": "Sudoku",
        "num_players": 1,
        "difficulty": 4,
        "description": "Sudoku decsription.",
        "docSections": [
            {"title": "Goal", "items": ["reach the exit", "avoid traps"]},
        ],
        "image": {"kind": "placeholder", "value": "maze"},
    },
    
]

def get_env(slug: str):
    slug = (slug or "").strip().lower()
    for e in ENVIRONMENTS:
        if e["slug"] == slug:
            return e
    return None
