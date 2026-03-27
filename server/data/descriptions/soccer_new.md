## Overview

A 2v2 physics-based soccer game. Players must coordinate with their teammate to move the ball down the field, score on the opponent's goal, and defend their own goal from incoming attacks.

Based on the soccer gamemode in the physics-based browser game [Bonk.io](http://Bonk.io).

## Coding

When coding your soccer agent, you can use the `action` list for movement and the `inputs` dictionary for getting current positions and game state.

Note: the coordinate system has (0, 0) at the top-left corner, with y increasing downward.

## Actions

The `action` list has three elements: horizontal movement, vertical movement, and kick.

```
action = [left/right, up/down, kick]
```

For the first element (left/right):
```
-1: move left
 0: no left/right movement
 1: move right
```

For the second element (up/down):
```
-1: move up
 0: no up/down movement
 1: move down
```

For the third element (kick):
```
 1: kick
 0: dont kick
```

Examples:
```
action = [-1, 0, 0] // move straight left
action = [0, 0, 1]  // kick in place
```

## Inputs

The `inputs` dictionary contains your player info, your teammate's info, both opponents' info, the ball, and both goals.

```python
inputs = {
  "you": {
    "team": "blue" or "red",
    "position": [x, y],
    "velocity": [x, y],
    "kicking": 0 or 1
  },
  "teammate": {
    "team": "blue" or "red",
    "position": [x, y],
    "velocity": [x, y],
    "kicking": 0 or 1
  },
  "opponent1": {
    "team": "blue" or "red",
    "position": [x, y],
    "velocity": [x, y],
    "kicking": 0 or 1
  },
  "opponent2": {
    "team": "blue" or "red",
    "position": [x, y],
    "velocity": [x, y],
    "kicking": 0 or 1
  },
  "ball": {
    "position": [x, y],
    "velocity": [x, y]
  },
  "goals": {
    "blue": {
      "post1": [x, y],
      "post2": [x, y]
    },
    "red": {
      "post1": [x, y],
      "post2": [x, y]
    }
  }
}
```

Positions use a 900×600 coordinate space. The playable field runs from roughly x=46 to x=854 and y=96 to y=504, with the center at (450, 300). The blue goal posts are at x=50, y=225 and y=375. The red goal posts are at x=850, y=225 and y=375.

## Teams

P1 and P2 are on the **blue** team and start on the left side. P3 and P4 are on the **red** team and start on the right side. The blue goal is on the left and the red goal is on the right — score by getting the ball into the opponent's goal.

## Additional Information
