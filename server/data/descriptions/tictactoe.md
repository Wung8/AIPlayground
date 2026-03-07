## Overview

A simple two-player strategy game played on a 3x3 grid, where players take turns marking an empty tile on the grid. The goal is to be the first to place three of your marks in a row: horizontally, vertically, or diagonally. If all nine squares are filled and no one has three marks in a row, the game ends in a draw.

Tic Tac Toe can be considered as the “Hello World” of minimax and similar zero-sum algorithms. It has a simple and visualizable state space, with only 5,478 reachable states and a maximum depth of 9\.

## Actions

\[ up/down, left/right, mark \]

action\[0\] (up/down)

* \-1: up  
* 0: /  
* 1: down

action\[1\] (left/right)

* \-1: left  
* 0: /  
* 1: right

action\[2\] (mark)

* 0: /  
* 1: mark

## Inputs

{ “grid”, “cursor\_position” }

inputs\[“grid”\]

* \[0\]: value at row 0 column 0  
* \[1\]: value at row 0 column 1  
* . . .   
* \[8\]: value at row 2 column 2

inputs\[“cursor\_position”\]

* \[0\]: cursor x position  
* \[1\]: cursor y position

## End Condition

The game ends when a player makes three in a row. If all nine squares are filled and no one has three in a row the game ends in a draw.

## Additional Information

During the opponent's turn, the player’s actions are ignored, including cursor movement.