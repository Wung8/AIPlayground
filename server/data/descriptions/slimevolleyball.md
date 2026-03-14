## Overview

A competitive two-player physics-based game. Players must hit the ball over the net so it lands on the opponents side, and prevent the opponent from doing the same to them. Keep the ball on your side for too long and you lose the point\! The first player to reach six points is the winner.

Slime Volleyball is a popular game for AI research as it’s easy to learn and has simple rules, but has emergent gameplay and requires adapting to opponents.

Based on the classic browser game Slime Volleyball from [OneSlime.net](http://OneSlime.net), now with even dodgier physics. While seemingly simple, Slime Volleyball has a surprising amount of mechanical and strategic depth, see “The Slimes” section of [https://oneslime.net/kb/One\_Slime\_FAQ.html](https://oneslime.net/kb/One_Slime_FAQ.html). 

## Coding

When coding your slime volleyball agent, you can use the `action` list for movement and the `inputs` dictionary for getting the current positions.

## Actions

The `action` list has two elements: horizontal movement (left/right) and jump.

```
action = [left/right, jump]
```

For the first element (left/right):

```
-1: move left  
 0: no left/right movement
 1: move right
```

For the second element (jump):
```
 1: jump
 0: dont jump  
```

Examples:

```
action = [-1, 0] // move straight left
action = [0, 1] // jump in place
```


## Inputs

The `inputs` dictionary contains three subdictionaries: `you`, `opponent`, and `ball`. 

Each sub-dictionary contains two keys: "position" and "velocity". 

Each key (position and velocity) corresponds to a list of two elements: `[x, y]`.  

```python
inputs = {
  you: {
    "position": [x, y],
    "velocity": [x, y]
  },
  opponent: {
    "position": [x, y],
    "velocity": [x, y]
  }, 
  ball: {
    "position": [x, y],
    "velocity": [x, y]
  }
}
```


## End Condition

The game ends either when a player reaches 6 points or the game has lasted 3 minutes, where the player with the most points will be declared the winner. If both players have the same amount of points, the game ends in a draw.

## Additional Information
