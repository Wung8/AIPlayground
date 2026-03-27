## Overview

A simple two-player strategy game played on a 3x3 grid, where players take turns marking an empty tile on the grid. The goal is to be the first to place three of your marks in a row: horizontally, vertically, or diagonally. If all nine squares are filled and no one has three marks in a row, the game ends in a draw.

Tic Tac Toe can be considered as the "Hello World" of minimax and similar zero-sum algorithms. It has a simple and visualizable state space, with only 5,478 reachable states and a maximum depth of 9.

## Actions

```
action = [up/down, left/right, mark]
```

action[0] (up/down):
```
-1: move cursor up
 0: no movement
 1: move cursor down
```

action[1] (left/right):
```
-1: move cursor left
 0: no movement
 1: move cursor right
```

action[2] (mark):
```
0: dont mark
1: mark current tile
```

Example:
```python
action = [0, 1, 0]  # move cursor right
action = [0, 0, 1]  # mark current tile
```

## Inputs

```python
inputs = {
  "grid": ".........",
  "your_position": [row, col],
  "your_turn": True or False
}
```

`grid` is a string of 9 characters representing the board in row-major order. `.` is an empty tile, `x` is P1, `o` is P2. Index 0 is row 0 column 0, index 8 is row 2 column 2.

Example:
```python
inputs = {
  "grid": "x.o......",
  "your_position": [1, 2],
  "your_turn": True
}
```

## End Condition

The game ends when a player makes three in a row. If all nine squares are filled and no one has three in a row the game ends in a draw.

## Additional Information

During the opponent's turn, the player's actions are ignored, including cursor movement.
