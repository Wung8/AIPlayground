import math
from enum import IntEnum


class Agent:
    def __init__(self):
        self.current_dir = 1

    def getAction(self, inputs):
        my_pos = inputs["your_position"][0]
        opponent_position = inputs["opponent_position"]
        ball_position = inputs["ball_position"]
        ball_velocity = inputs["ball_velocity"]

        # right side
        if my_pos > 400:
            if my_pos < 500:
                self.current_dir = 1
            elif my_pos > 700:
                self.current_dir = -1
        # left side
        else:
            if my_pos < -300:
                self.current_dir = 1
            elif my_pos > -100:
                self.current_dir = -1

        print(self.current_dir, my_pos)
        action = [self.current_dir, 0]
        return action
