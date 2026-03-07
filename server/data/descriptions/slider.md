## Overview

The Sliding Puzzle is a classic logic game/puzzle made up of a 5x5 grid containing 24 numbered tiles and one empty space, with other sized variants. The goal is to arrange the tiles such that they are in order, with the blank in the bottom right. Tiles cannot move freely and can only be moved into the blank. 

The Slider Puzzle is a challenging problem for graph-based pathfinding algorithms, especially the 5x5. With 25\!/2 (or about 7.8 × 10²⁴) possible states, potentially long paths to the solution, and non-obvious heuristics, this problem is too complicated for a basic implementation of A-Star. For those interested in the solution, refer to [https://stackoverflow.com/a/60801614](https://stackoverflow.com/a/60801614). 

## Actions

\[ up/down/left/right \]

action\[0\] (up/down/left/right)

* 0: /  
* 1: up  
* 2: down  
* 3: left  
* 4: right

## Inputs

\[ “grid” \]

inputs\[“grid”\]

* \[0\]: value at row 0 column 0  
* \[1\]: value at row 0 column 1  
* . . .  
* \[24\]: value at row 4 column 4 (in the case of a 5x5)

## End Condition

The game ends when the puzzle is solved with all the tiles in order and the hole at the bottom right. 

## Additional Information

The grid is represented by a list of integers, flattened row-first.
