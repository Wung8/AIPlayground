import numpy as np
import heapq
import random

class SliderPuzzleFunctionality:

    def __init__(self, difficulty="medium", **kwargs):
        self.grid = None

        match difficulty:
            case "easy":
                self.N = 3
                self.solved_grid = [ 1,  2,  3,
                                     4,  5,  6,
                                     7,  8,  0 ]
            case "medium":
                self.N = 4
                self.solved_grid = [ 1,  2,  3,  4,
                                     5,  6,  7,  8,
                                     9,  10, 11, 12,
                                     13, 14, 15, 0 ]
            case "hard":
                self.N = 5
                self.solved_grid = [ 1,  2,  3,  4,  5,
                                     6,  7,  8,  9, 10,
                                     11, 12, 13, 14, 15,
                                     16, 17, 18, 19, 20,
                                     21, 22, 23, 24,  0 ]
        
        self.move_mapping = ["up", "down", "left", "right"]

    def is_solved(self, grid):
        return grid == self.solved_grid

    def get_neighbors(self, grid):
        neighbors = [None for i in range(4)] # up down left right
        dirs = ((1,0), (-1,0), (0,1), (0,-1))
        hole = grid.index(0)
        r, c = divmod(hole, self.N)

        for n, (dr, dc) in enumerate(dirs):
            nr, nc = r + dr, c + dc

            if 0 <= nr < self.N and 0 <= nc < self.N:
                swap_idx = nr * self.N + nc
                new_grid = grid[:]
                new_grid[hole], new_grid[swap_idx] = new_grid[swap_idx], new_grid[hole]
                neighbors[n] = new_grid

        return neighbors


class Agent:
    def __init__(self):
        self.path = None

    def manhattanDistance(self, p1, p2):
        return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

    def heuristic(self, grid):
        h = 0
        for n, val in enumerate(grid):
            m = self.func.solved_grid.index(val)
            curr = n % 5, n // 5
            target = m % 5, m // 5
            h += self.manhattanDistance(curr, target)
        return h

    def pathFind(self, grid):
        frontier = []
        came_from = {}
        cost_so_far = {}

        grid = tuple(grid)
        heapq.heappush(frontier, (0, grid))
        came_from[grid] = None
        cost_so_far[grid] = 0

        while frontier:
            _, curr = heapq.heappop(frontier)

            if self.func.is_solved(list(curr)):
                break
            
            for n, nbr in enumerate(self.func.get_neighbors(list(curr))):
                if not nbr:
                    continue
                nbr = tuple(nbr)
                cost = cost_so_far[tuple(curr)] + 1
                if nbr not in cost_so_far or cost < cost_so_far[nbr]:
                    cost_so_far[nbr] = cost + 1
                    priority = cost + self.heuristic(nbr)
                    heapq.heappush(frontier, (priority, nbr))
                    came_from[nbr] = (curr, self.func.move_mapping[n])
        else:
            return None

        path = []
        curr = tuple(self.func.solved_grid)
        while came_from[curr] is not None:
            prev, move = came_from[curr]
            path.append((move, prev))
            curr = prev

        path = path[::-1]
        return path


    def getAction(self, inputs):
        grid = inputs["grid"]
        grid = tuple(grid)

        if not self.path or self.path[0][1] != grid:
            difficulty_mapping = {
                9: "easy", 16: "medium", 25: "hard"
            }
            self.func = SliderPuzzleFunctionality(difficulty=difficulty_mapping[len(grid)])
            self.grid = grid[:]
            self.path = self.pathFind(grid)

        if self.path:
            move, _ = self.path.pop(0)
            return [self.func.move_mapping.index(move) + 1]
        else:
            return [0]
        

        



