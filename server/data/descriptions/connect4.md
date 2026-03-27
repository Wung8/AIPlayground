## Overview

A two-player strategy game played on a 6×7 grid. Players take turns dropping pieces into columns, and the pieces fall to the lowest available row. The goal is to be the first to connect four of your pieces in a row: horizontally, vertically, or diagonally.

## Actions

```
action = [move]
```

action[0]:
```
0: no action
1-7: select column (moves the pending drop indicator)
8: drop piece into the selected column
```

Example:
```python
action = [3]  # select column 3
action = [8]  # drop piece
```

## Inputs

Both players receive the same inputs.

```python
inputs = {
  "grid": [[row], [row], ...],
  "player": 'o' or 'x',
  "pending_move": 0-6
}
```

`grid` is a 6×7 2D array. Each cell is `'.'` (empty), `'x'`, or `'o'`. Row 0 is the top, row 5 is the bottom. P1 plays `'o'`, P2 plays `'x'`.

`player` is the piece type of whoever's turn it currently is (`'o'` = P1's turn, `'x'` = P2's turn).

`pending_move` is the currently selected column index (0–6).

Example:
```python
inputs = {
  "grid": [
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', 'o', '.', '.', '.'],
    ['.', '.', 'x', 'o', '.', '.', '.']
  ],
  "player": "o",
  "pending_move": 3
}
```

## End Condition

The game ends when a player connects four pieces in a row horizontally, vertically, or diagonally.

## Additional Information

During the opponent's turn, actions are ignored.
