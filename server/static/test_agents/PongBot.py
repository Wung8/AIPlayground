import math
from enum import IntEnum


class Agent:
    def getAction(self, inputs):
        your_position = inputs["your_position"]
        opponent_position = inputs["opponent_position"]
        ball_position = inputs["ball_position"]
        ball_velocity = inputs["ball_velocity"]

        if abs(your_position[1] - ball_position[1]) < 6:
            action = [0]
        elif your_position[1] > ball_position[1]:
            action = [-1]
        else:
            action = [1]

        return action
