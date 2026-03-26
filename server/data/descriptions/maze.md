## Overview

Navigate through the maze to get to the goal.

Mazes are a great introduction to graph-based pathfinding algorithms, as the entire graph is visualized and the number of possible states is relatively small. 

## Actions

The `action` list has two elements: horizontal movement (left/right) and vertical movement (up/down).

```python
action = [left/right, up/down]
```

Examples:

```python
action = [0, 1] # move down
action = [1, 0] # move right
action = [0, 0] # stay in place
```

## Input

The `inputs` dictionary contains three values: `your_position`, `goal_position`, and `grid`. 

`your_position` and `goal_position` correspond to lists representing `[x, y]` coordinates. 

`grid` corresponds to a list of lists representing tiles in the maze, with `0`s representing empty spaces while `1`s represent walls. Values can be indexed from grid using `grid[x][y]`

Each value corresponds to a list of two elements: `[x, y]`.  

```python
inputs = {
  "your_position": [x, y],
  "goal_position": [x, y],
  "grid": grid
}
```

## End Condition

The game ends when the player reaches the goal, which is always located in the bottom right corner of the maze.

## Additional Information

The easy maze is 33x17, the normal maze is 65x33, and the hard maze is 129x65. The starting position is always at the top left and the goal is always at the bottom right. There are no loops in any maze.
