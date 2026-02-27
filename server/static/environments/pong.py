import numpy as np
import cv2, math, time, random
import keyboard as k
from colorsys import hsv_to_rgb

class PongEnv:
    num_players = 2
    framerate=20
    resolution = 800, 400

    buffer = 30
    size = 300, 150
    scale = resolution[0] / size[0]
    scale = 3

    paddle_offset = 50
    paddle_width = 3
    paddle_height = 25
    paddle_speed = 5
    ball_size = 3

    numbers = '''
XXX  XXXXXXXX XXXXXXXXXXXXXXXX
X X  X  X  XX XX  X    XX XX X
X X  XXXXXXXXXXXXXXXX  XXXXXXX
X X  XX    X  X  XX X  XX X  X
XXX  XXXXXXX  XXXXXXX  XXXX  X
'''.strip().split('\n')

    colors = {
        "player": (255,255,255),
        "ball": (255,255,255),
        "bg": (0,0,0),
        "details": (255,255,255)
    }

    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.ball = None
        self.ball_vel = None
        self.score = [0,0]
    
    def reset(self):
        self.player1 = [self.paddle_offset, self.size[1]//2]
        self.player2 = [self.size[0]-self.paddle_offset-1, self.size[1]//2]
        self.ball = [self.size[0]//2, self.size[1]//2]
        self.ball_vel = [[-1, 0], [1, 0]][random.random() < 0.5]
        self.ball_speed = 5
        self.counter = self.buffer

        self.last_frame = time.time()

    def getInputs(self):
        return {
            "p1": {
                "grid": self.grid,
                "your_position": self.player
            }
        }

    def step(self, actions, keyboard={}):
        if self.counter: 
            self.counter -= 1
            return

        for i in range(2):
            action = actions[f"p{i+1}"]
            player = [self.player1, self.player2][i]
            player[1] += action[0] * self.paddle_speed
            if player[1] < 0 + self.paddle_height//2:
                player[1] = self.paddle_height//2
            if player[1] > self.size[1] - self.paddle_height//2 - 1:
                player[1] = self.size[1] - self.paddle_height//2 - 1
        
        for i in range(int(self.ball_speed)):
            self.ball[0] += self.ball_vel[0]
            self.ball[1] += self.ball_vel[1]
            
            dx = self.ball[0] - self.player1[0] - self.ball_size//2
            if 0 >= dx > -self.paddle_width:
                dy = self.ball[1] - self.player1[1]
                if abs(dy) <= self.paddle_height//2+1:
                    self.ball_vel[1] = dy / self.paddle_height
                    self.ball_vel[0] = (1-self.ball_vel[1]**2)**0.5
                    self.ball_speed += 0.25
            
            dx = self.player2[0] - self.ball[0] - self.ball_size//2
            if 0 >= dx > -self.paddle_width:
                dy = self.ball[1] - self.player2[1]
                if abs(dy) <= self.paddle_height//2+1:
                    self.ball_vel[1] = dy / self.paddle_height
                    self.ball_vel[0] = -(1-self.ball_vel[1]**2)**0.5
                    self.ball_speed += 0.25
            
            if self.ball[1] <= self.ball_size//2 + 2:
                self.ball_vel[1] = abs(self.ball_vel[1])
                if self.ball[1] == -1:
                    self.ball[1] = 1
            
            if self.ball[1] >= self.size[1]-self.ball_size//2 - 2:
                self.ball_vel[1] = -abs(self.ball_vel[1])
                if self.ball[1] == self.size[1]:
                    self.ball[1] = self.size[1]-2
        
        if self.ball[0] <= 0:
            self.score[1] += 1
            self.reset()
        
        if self.ball[0] >= self.size[0]-1:
            self.score[0] += 1
            self.reset()
            
    def posToGrid(self, pos):
        return int(2*pos[0]+1), int(2*pos[1]+1)

    def getNeighbors(self, pos):
        nbrs = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if dx * dy != 0:
                    continue
                new_pos = (pos[0] + dx, pos[1] + dy)
                if self.outOfBounds(new_pos):
                    continue
                nbrs.append(new_pos)
        return nbrs
        
    def outOfBounds(self, pos):
        if not(0 <= pos[0] < self.size[0]):
            return True
        if not(0 <= pos[1] < self.size[1]):
            return True
        return False

    def drawDigit(self, img, digit, top_left_x, top_left_y, scale=1):
        digit = int(digit)
        digit_width = 3
        digit_height = 5
        spacing = 0
        
        start_col = digit * (digit_width + spacing)

        for row in range(digit_height):
            for col in range(digit_width):
                if self.numbers[row][start_col + col] == "X":
                    for dx in range(scale):
                        for dy in range(scale):
                            x = top_left_x + col*scale + dx
                            y = top_left_y + row*scale + dy
                            if 0 <= x < self.size[0] and 0 <= y < self.size[1]:
                                img[x, y] = self.colors["details"]

    def display(self):
        img = np.array([[self.colors['bg']]], dtype=np.uint8)
        img = img.repeat(self.size[0],axis=0).repeat(self.size[1],axis=1)

        for player in (self.player1, self.player2):
            for i in range(-self.paddle_height//2+3, self.paddle_height//2+1-3):
                for j in range(self.paddle_width):
                    img[int(player[0]-j), int(player[1]+i)] = self.colors['player']

        for i in range(-self.ball_size//2, self.ball_size//2+1):
            for j in range(-self.ball_size//2, self.ball_size//2+1):
                img[int(self.ball[0]+i), int(self.ball[1]+j)] = self.colors['ball']

        for i in range(0, self.size[1], 5):
            for j in range(3):
                img[self.size[0]//2, i+j] = self.colors['details']
        
        # display scores

        score_y = 10  # distance from top
        center_x = self.size[0] // 2

        digit_width = 3
        gap_from_center = 10

        # P1 score (left of center)
        self.drawDigit(
            img,
            self.score[0],
            center_x - gap_from_center - digit_width,
            score_y,
            scale=2
        )

        # P2 score (right of center)
        self.drawDigit(
            img,
            self.score[1],
            center_x + gap_from_center,
            score_y,
            scale=2
        )

        img = img.transpose(1,0,2)
        img = img.repeat(self.scale,axis=0).repeat(self.scale,axis=1)
        
        cv2.imshow('img', img)
        
        this_frame = time.time()
        cv2.waitKey(max(int(1000/self.framerate-(this_frame-self.last_frame)), 20))
        self.last_frame = this_frame
            
env = PongEnv()
env.reset()
while True:
    actions1, actions2 = [0], [0]
    if k.is_pressed('w'): actions1[0] -= 1
    if k.is_pressed('s'): actions1[0] += 1
    if k.is_pressed('o'): actions2[0] -= 1
    if k.is_pressed('l'): actions2[0] += 1
    if k.is_pressed('r'): env.reset()
    env.step({"p1":actions1, "p2":actions2})
    env.display()

    #if done:
    #    env.reset()
