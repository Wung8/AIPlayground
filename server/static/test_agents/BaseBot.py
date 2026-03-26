import math, random, numpy, enum, heapq, time # allowed imports

class Agent:

    move_mapping = { # format moves
        "stay": [0, 0],
        "up": [0, -1],
        "down": [0, 1],
        "left": [-1, 0],
        "right": [1, 0],
    }

    def pathfind(self, start, goal, grid):
        # figure out the series of moves to get from the start to 
        # the goal, also called a "path"
        path = ["left", "up", "down"] # for example
        return path
    
    def getAction(self, inputs):
        grid = inputs["grid"]
        position = inputs["your_position"]
        goal = None # figure out what the goal should be

        path = self.pathfind(position, grid) # is there a way to avoid calculating this every step?
        action = self.move_mapping[path[0]]
        
        return action
