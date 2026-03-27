A bot is a Python file with an `Agent` class. The platform loads it and calls `getAction` every frame.

## File Structure

Create a new `.py` file with the following:

```python
class Agent:
    def __init__(self):
        pass  # set up any state here

    def getAction(self, inputs):
        action = [0]  # replace with your logic
        return action
```

## Example: Pong Bot

```python
class Agent:
    def __init__(self):
        pass

    def getAction(self, inputs):
        ball_y = inputs["ball_position"][1]
        my_y = inputs["your_position"][1]

        if ball_y < my_y:
            return [-1]  # move up
        elif ball_y > my_y:
            return [1]   # move down
        return [0]
```

See the Documentation page for each environment to learn what `inputs` contains and what `action` values are valid.
