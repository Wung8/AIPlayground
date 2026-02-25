import math
from enum import IntEnum


class Agent:
    def getAction(self, inputs):
        your_position = inputs["your_position"]
        opponent_position = inputs["opponent_position"]
        ball_position = inputs["ball_position"]
        ball_velocity = inputs["ball_velocity"]

        action = [0, 0]

        #print(your_position, enemy_position, ball_position, ball_velocity)
        x, y = ball_position
        vx, vy = ball_velocity
        g = 10
        dh = 20 - y
        t = (vy + math.sqrt(vy**2 - 4*0.5*g*dh)) / (2*g)

        goal_x = x + vx * t
        sign = [-1, 1][your_position[0] > 0]

        flag = False
        if abs(goal_x - sign*200) > 200:
            goal_x = sign*200
            flag = True
        
        offset = 20
        e = 5 + flag * 20
        dx = your_position[0] - (goal_x + offset * sign)
        if abs(dx) < e:
            action[0] = 0
        elif dx < 0:
            action[0] = 1
        else:
            action[0] = -1

        jump_threshold = 20
        if not flag and your_position[0] - ball_position[0] < jump_threshold:
            action[1] = 1
        
        return action
