import math
from enum import IntEnum


class Agent:
    def getAction(self, inputs):
        your_position = inputs["your_position"]
        opponent_position = inputs["opponent_position"]
        ball_position = inputs["ball_position"]
        ball_velocity = inputs["ball_velocity"]

        action = [0, 1]

        return action
