import math

class Agent():
    def getAction(self, inputs):
        you = inputs["you"]
        ball = inputs["ball"]
        
        goal_info = inputs["goals"]["blue" if you["team"]=="red" else "red"]
        post1 = goal_info["post1"]
        post2 = goal_info["post2"]
        goal_middle = (
            (post1[0] + post2[0]) / 2,
            (post1[1] + post2[1]) / 2
        )

        action = [0, 0, 0]

        you_pos = you["position"]
        ball_pos = ball["position"]

        # --- helper function ---
        def move_toward(target):
            dx = target[0] - you_pos[0]
            dy = target[1] - you_pos[1]

            # horizontal
            if abs(dx) > 5:
                action[0] = 1 if dx > 0 else -1
            else:
                action[0] = 0

            # vertical
            if abs(dy) > 5:
                action[1] = 1 if dy > 0 else -1
            else:
                action[1] = 0

        dist_to_ball = math.dist(you_pos, ball_pos)

        # -------------------------------------------------
        # 1. If far from ball → chase it
        # -------------------------------------------------
        if dist_to_ball > 50:
            move_toward(ball_pos)

        else:
            # -------------------------------------------------
            # 2. Close to ball → get behind it toward goal
            # -------------------------------------------------

            # Vector from ball to goal
            bgx = goal_middle[0] - ball_pos[0]
            bgy = goal_middle[1] - ball_pos[1]
            mag = math.hypot(bgx, bgy)

            if mag != 0:
                bgx /= mag
                bgy /= mag

            # Target spot slightly behind ball
            offset = 25
            target = (
                ball_pos[0] - bgx * offset,
                ball_pos[1] - bgy * offset
            )

            dist_to_target = math.dist(you_pos, target)

            # If not well positioned behind ball
            if dist_to_target > 15:
                move_toward(target)
            else:
                # -------------------------------------------------
                # 3. Good position → kick toward goal
                # -------------------------------------------------
                move_toward(ball_pos)

                if dist_to_ball < 40:
                    action[2] = 1  # kick

        return action