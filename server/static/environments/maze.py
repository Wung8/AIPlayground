import numpy as np
import cv2, math, time, random
import keyboard as k

class MazeEnv:
    num_players = 1
    framerate=20
    resolution = 800, 400
    colors = {
        "bg": (50, 50, 50),
        "wall": (100, 100, 100),
        "player": (200, 200, 200),
        "goal": (100, 200, 100),
        "complete": (230, 230, 100)
    }

    def __init__(self, size=(32, 16)):
        self.size = size
        self.grid = None
        self.player = None
        self.goal = None
    
    def reset(self):

        self.grid = np.ones((2*self.size[0]+1, 2*self.size[1]+1))
        stack = [(random.randint(0, self.size[0]-1), random.randint(0, self.size[1]-1))]
        while stack:
            curr = stack[-1]
            nbrs = [nbr for nbr in self.getNeighbors(curr) if self.grid[self.posToGrid(nbr)]==1]
            
            if not nbrs:
                stack.pop()
                continue
            nbr = random.choice(nbrs)
            grid_pos_curr = self.posToGrid(curr)
            grid_pos_nbr = self.posToGrid(nbr)
            grid_pos_mid = self.posToGrid(np.mean((curr, nbr), axis=0))
            self.grid[grid_pos_curr] = 0
            self.grid[grid_pos_nbr] = 0
            self.grid[grid_pos_mid] = 0
            stack.append(nbr)
        
        self.player = [1,1]
        self.goal = (2*self.size[0]-1, 2*self.size[1]-1)

        self.last_frame = time.time()

    def step(self, action):
        new_pos = self.player[:]
        new_pos[0] += action[0]
        if self.grid[*new_pos] == 0:
            self.player = new_pos
        new_pos = self.player[:]
        new_pos[1] += action[1]
        if self.grid[*new_pos] == 0:
            self.player = new_pos
    
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

    def display(self):
        img = np.array([[self.colors['bg']]], dtype=np.uint8)
        img = img.repeat(self.size[0]*2+1,axis=0).repeat(self.size[1]*2+1,axis=1)
        img[self.grid==1] = self.colors['wall']
        img[*self.player] = self.colors['player']
        img[*self.goal] = self.colors['goal']
        if tuple(self.player) == tuple(self.goal):
            img[*self.player] = self.colors['complete']
        img = img.transpose(1,0,2)

        '''
        mapping = {
            0: "  ",
            1: "XX",
        }
        for row in self.grid:
            s = "".join(mapping[int(tile)] for tile in row)
            print(s)
        '''

        scale = 10
        img = img.repeat(scale,axis=0).repeat(scale,axis=1)
        
        cv2.imshow('img', img)
        
        this_frame = time.time()
        cv2.waitKey(max(int(1000/self.framerate-(this_frame-self.last_frame)), 20))
        self.last_frame = this_frame
            
env = MazeEnv()
env.reset()
while True:
    actions = [0,0]
    if k.is_pressed('w'): actions[1] -= 1
    if k.is_pressed('a'): actions[0] -= 1
    if k.is_pressed('s'): actions[1] += 1
    if k.is_pressed('d'): actions[0] += 1
    env.step(actions)
    env.display()
