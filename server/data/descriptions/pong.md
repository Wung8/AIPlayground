## Overview

One of the first computer games ever made, players control their paddle by moving it up and down across the screen to hit a ball back and forth. If you get the ball past the opponent's paddle, you score a point. The first player to reach 9 points wins.

Pong is great for learning and developing AI with its simple inputs and actions. Pong can also be used for harder problems, such as processing visual inputs or reinforcement learning.

## Actions

The `action` list has one element: vertical movement (up/down).

```
action = [up/down, jump]
```

For the first element (up/down):

```
-1: move up 
 0: no up/down movement
 1: move down
```

Examples:

```
action = [-1, 0] // move up
action = [0] // stay in place
```


## Inputs

The `inputs` dictionary contains three values: `your_position`, `opponent_position`, `ball_position`, and `ball_velocity`. 

Each value corresponds to a list of two elements: `[x, y]`.  

```python
inputs = {
  "your_position": [x, y],
  "opponent_position": [x, y],
  "ball_position": [x, y],
  "ball_velocity": [x, y]
}
```

## End Condition

The game ends either when a player reaches 9 points or the game has lasted 3 minutes, where the player with the most points will be declared the winner. If both players have the same amount of points, the game ends in a draw.
