## Overview

A single-player survival and crafting game. Explore a procedurally generated world, gather resources, craft tools, and survive against enemies. Your score increases by collecting resources and reaching goals.

## Actions

```
action = [move, attack, interact, sleep, place, craft]
```

action[0] (move):
```
0: no movement
1: move left
2: move right
3: move up
4: move down
```

action[1] (attack):
```
0: dont attack
1: attack tile in front of player
```

action[2] (interact):
```
0: dont interact
1: drink water / eat berries from tile in front
```

action[3] (sleep):
```
0: dont sleep
1: toggle sleep
```

action[4] (place):
```
0: dont place
1: place a block in front of player
```

action[5] (craft):
```
0: dont craft
1: toggle crafting menu
```

Example:
```python
action = [2, 0, 0, 0, 0, 0]  # move right
action = [0, 1, 0, 0, 0, 0]  # attack
```

## Inputs

```python
inputs = {
  "tiles": [[row], [row], ...],
  "player": {
    "dir": [dx, dy],
    "health": int
  },
  "inventory": {
    "wood": int,
    "stone": int,
    "planks": int
  },
  "enemies": [{"x": int, "y": int, "dir": [dx, dy], "health": int}, ...],
  "hunger": int,
  "thirst": int,
  "energy": float,
  "player_pickaxe": int,
  "player_sword": int,
  "crafting": int,
  "crafting_slots": [int, ...],
  "sleep": int,
  "score": int,
  "pre_tick": bool
}
```

`tiles` is a 9×9 2D array centered on the player. Each cell is an integer representing the tile type:

```
-1: out of bounds
 0: water
 1: grass
 2: tree
 3: bush (berries)
 4: stone
 5: wall
 6: plank
 7: diamond
```

`enemies` is a list of enemies visible within the 9×9 view. Positions are relative to the player.

## End Condition

The game ends when the player's health reaches zero.

## Additional Information
