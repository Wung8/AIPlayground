## Overview

Mazes are a great introduction to graph-based pathfinding algorithms, as the entire graph is visualized and the state space is relatively small.

## Actions

```
action = [left/right, up/down]
```

action[0] (left/right):
```
-1: left
 0: no movement
 1: right
```

action[1] (up/down):
```
-1: up
 0: no movement
 1: down
```

Example:
```python
action = [1, 0]  # move right
```

## Inputs

```python
inputs = {
  "grid": [[row], [row], ...],
  "your_position": [x, y]
}
```

The grid is a 2D array of size `(2*width+1) x (2*height+1)`. Easy: width=16, height=8. Medium: width=32, height=16. Hard: width=64, height=32. The border of the grid is always walls, so you never need to check for out-of-bounds.

Example:
```python
inputs = {
  "grid": [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1]
  ],  # (actual grid is much larger)
  "your_position": [1, 1]
}
```

The starting position is always [1, 1]. The goal position is [31, 15] (easy), [63, 31] (medium), or [127, 63] (hard).

## End Condition

The game ends when the player reaches the goal at the bottom-right corner of the maze.

## Additional Information

The easy maze is 33x17, the normal maze is 65x33, and the hard maze is 129x65. The starting position is always at the top left and the goal is always at the bottom right. There are no loops in any maze.
