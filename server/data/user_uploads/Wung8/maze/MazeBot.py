import numpy as np
import heapq
import random

class Agent:
    def __init__(self):
        self.path = None
        self.sequence = None

        self.dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def manhattanDistance(self, p1, p2):
        return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

    def pathFind(self, pos, goal, grid):
        frontier = []
        came_from = {}
        cost_so_far = {}

        w, h = len(grid), len(grid[0])

        pos = tuple(pos)
        heapq.heappush(frontier, (0, pos))
        came_from[pos] = None
        cost_so_far[pos] = 0

        while frontier:
            _, curr = heapq.heappop(frontier)

            if curr == goal:
                break

            neighbors = []
            for dx, dy in self.dirs:
                nbr = curr[0] + dx, curr[1] + dy
                if 0 <= nbr[0] < w and 0 <= nbr[1] < h:
                    neighbors.append(nbr)
                else:
                    neighbors.append(None)
            
            for n, nbr in enumerate(neighbors):
                if not nbr:
                    continue
                nbr = tuple(nbr)
                cost = cost_so_far[tuple(curr)] + 999*grid[nbr[0]][nbr[1]] + 1
                if nbr not in cost_so_far or cost < cost_so_far[nbr]:
                    cost_so_far[nbr] = cost
                    priority = cost + self.manhattanDistance(nbr, goal)
                    heapq.heappush(frontier, (priority, nbr))
                    came_from[nbr] = (curr, n)
        else:
            return None

        path = []
        curr = tuple(goal)
        while came_from[curr] is not None:
            prev, move = came_from[curr]
            path.append((move, prev))
            curr = prev

        path = path[::-1]
        return path

    def getAction(self, inputs):

        grid = inputs["grid"]
        position = inputs["your_position"]
        position = tuple(position)

        if not self.path or self.path[0][1] != position:
            w, h = len(grid), len(grid[0])
            goal = w - 2, h - 2

            self.grid = grid
            self.path = self.pathFind(position, goal, grid)

        if self.path:
            move, _ = self.path.pop(0)
            return [*self.dirs[move]]
        else:
            return [0,0]





        



