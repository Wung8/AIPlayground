import math

class Agent():
    def __init__(self):
        self.state = "ATTACK"

    def getAction(self, inputs):
        you = inputs["you"]
        ball = inputs["ball"]

        you_pos = you["position"]
        ball_pos = ball["position"]

        # --- Compute goal centers ---
        red_mid = (
            (inputs["goals"]["red"]["post1"][0] + inputs["goals"]["red"]["post2"][0]) / 2,
            (inputs["goals"]["red"]["post1"][1] + inputs["goals"]["red"]["post2"][1]) / 2
        )

        blue_mid = (
            (inputs["goals"]["blue"]["post1"][0] + inputs["goals"]["blue"]["post2"][0]) / 2,
            (inputs["goals"]["blue"]["post1"][1] + inputs["goals"]["blue"]["post2"][1]) / 2
        )

        if you["team"] == "red":
            own_goal = red_mid
            opponent_goal = blue_mid
        else:
            own_goal = blue_mid
            opponent_goal = red_mid

        action = [0, 0, 0]

        # --- Helper ---
        def move_toward(target):
            dx = target[0] - you_pos[0]
            dy = target[1] - you_pos[1]

            # Distance to target
            dist = math.hypot(dx, dy)

            # Dead zone (don't jitter when very close)
            if dist < 10:
                action[0] = 0
                action[1] = 0
                return

            # Slowdown radius
            slow_radius = 60

            # Reduce responsiveness when close
            scale = min(1, dist / slow_radius)

            # Only move axis if meaningful
            if abs(dx) > 5:
                action[0] = 1 if dx > 0 else -1
            else:
                action[0] = 0

            if abs(dy) > 5:
                action[1] = 1 if dy > 0 else -1
            else:
                action[1] = 0

            # If inside slowdown radius, randomly drop one axis
            if dist < slow_radius:
                if abs(dx) < abs(dy):
                    action[0] = 0
                else:
                    action[1] = 0

        dist_to_ball = math.dist(you_pos, ball_pos)

        # Vector helpers
        def dot(a, b):
            return a[0]*b[0] + a[1]*b[1]

        # Ball relative to own goal
        to_own_goal = (own_goal[0] - you_pos[0], own_goal[1] - you_pos[1])
        to_ball = (ball_pos[0] - you_pos[0], ball_pos[1] - you_pos[1])

        ball_between_us_and_goal = dot(to_own_goal, to_ball) > 0

        # --------------------------------------------------
        # STATE TRANSITIONS
        # --------------------------------------------------

        if ball_between_us_and_goal and dist_to_ball < 120:
            self.state = "RECOVER"
        elif dist_to_ball < 35:
            self.state = "SHOOT"
        elif dist_to_ball < 120:
            self.state = "POSITION"
        else:
            self.state = "ATTACK"

        # --------------------------------------------------
        # STATE BEHAVIOR
        # --------------------------------------------------

        if self.state == "RECOVER":
            # Normalize ball direction
            bx = ball_pos[0] - you_pos[0]
            by = ball_pos[1] - you_pos[1]
            mag = math.hypot(bx, by)

            if mag != 0:
                bx /= mag
                by /= mag

            # Perpendicular direction (small sidestep)
            perp = (-by, bx)

            # Blend forward and sideways
            blend_forward = 0.6
            blend_side = 0.4

            tx = bx * blend_forward + perp[0] * blend_side
            ty = by * blend_forward + perp[1] * blend_side

            target = (you_pos[0] + tx * 40, you_pos[1] + ty * 40)
            move_toward(target)

        elif self.state == "ATTACK":
            move_toward(ball_pos)

        elif self.state == "POSITION":
            # Get behind ball relative to opponent goal
            bgx = opponent_goal[0] - ball_pos[0]
            bgy = opponent_goal[1] - ball_pos[1]
            mag = math.hypot(bgx, bgy)

            if mag != 0:
                bgx /= mag
                bgy /= mag

            offset = 30
            target = (
                ball_pos[0] - bgx * offset,
                ball_pos[1] - bgy * offset
            )
            move_toward(target)

        elif self.state == "SHOOT":
            move_toward(ball_pos)

            # Check alignment before kicking
            to_goal = (
                opponent_goal[0] - ball_pos[0],
                opponent_goal[1] - ball_pos[1]
            )
            alignment = dot(to_goal, to_ball)

            if alignment > 0:
                action[2] = 1  # kick

        return action