import numpy as np
import heapq
import random

class SliderPuzzleFunctionality:
    move_mapping = ["up", "down", "left", "right"]

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
        self.sequence = None

        self.difficulty_mapping = {
            9: "easy", 16: "medium", 25: "hard"
        }
        self.orders = {i:self.generateOrder(i) for i in (3,4,5)}
        self.func = SliderPuzzleFunctionality(difficulty="medium")

    def generateOrder(self, N):
        order = []
        for m in range(N-2):
            for c in range(m, N):
                order.append(m*N + c)
            if m != N-3:
                for r in range(m+1, N):
                    order.append(r*N + m)
        return order

    def manhattanDistance(self, p1, p2):
        return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])


    def heuristic(self, grid):
        h = 0
        for n, val in enumerate(grid):
            m = self.func.solved_grid.index(val)
            curr = n % self.N, n // self.N
            target = m % self.N, m // self.N
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
                penalty = (nbr.index(0) in self.orders[self.N]) * 9999
                cost = cost_so_far[tuple(curr)] + 1
                if nbr not in cost_so_far or cost < cost_so_far[nbr]:
                    cost_so_far[nbr] = cost + 1 + penalty
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
    
    def pathFind2(self, pos, goal, walls):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        frontier = []
        came_from = {}
        cost_so_far = {}

        pos = tuple(pos)
        heapq.heappush(frontier, (0, pos))
        came_from[pos] = None
        cost_so_far[pos] = 0

        while frontier:
            _, curr = heapq.heappop(frontier)

            if curr == goal:
                break

            neighbors = []
            for dy, dx in dirs:
                nbr = curr[0] + dy, curr[1] + dx
                if 0 <= nbr[0] < self.N and 0 <= nbr[1] < self.N:
                    neighbors.append(nbr)
                else:
                    neighbors.append(None)
            
            for n, nbr in enumerate(neighbors):
                if not nbr:
                    continue
                nbr = tuple(nbr)
                cost = cost_so_far[tuple(curr)] + (walls.get(nbr) or 1)
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
        grid = tuple(grid)

        if len(grid) != len(self.func.solved_grid):
            self.func = SliderPuzzleFunctionality(difficulty=self.difficulty_mapping[len(grid)])

        N = int(len(grid) ** 0.5)
        self.N = N
        i = -1
        walls = {}
        for i in self.orders[N]:
            if i+1 != grid[i]: break
            walls[divmod(i, N)] = 999
        else:
            # first N-2 rows solved -> A-Star
            if not self.path or self.path[0][1] != grid:
                self.func = SliderPuzzleFunctionality(difficulty=self.difficulty_mapping[len(grid)])
                self.grid = grid[:]
                self.path = self.pathFind(grid)

            if self.path:
                move, _ = self.path.pop(0)
                return [self.func.move_mapping.index(move) + 1]
            else:
                return [0]
        
        # not first N-2 rows solved -> Algorithm
        curr_val = i+1
        curr = divmod(grid.index(curr_val), N)
        hole = divmod(grid.index(0), N)
        target = divmod(curr_val-1, N)

        walls[curr] = 100
        
        if target[0] <= target[1]:
            if not self.sequence and target[1] == N-1 \
                and curr[1] == target[1] \
                and curr[0] == target[0]+1 \
                and hole[1] == curr[1] \
                and hole[0] == curr[0]+1: # special case
                    self.sequence = ["down", "down", "right", "up", "left", "up", "right", "down", "down", "left", "up"]
            elif not self.sequence and target[1] == N-1 \
                and curr[1] == target[1] \
                and curr[0] == target[0]+1 \
                and hole[1] == curr[1]-1 \
                and hole[0] == curr[0]: # special case
                    self.sequence = ["up", "left", "down", "down", "right", "up", "left", "up", "right", "down", "down", "left", "up"]
            elif curr[1] != target[1]: # wrong row, do first
                if curr[1] > target[1]: # target to left
                    hole_target = curr[0], curr[1]-1
                else: # target to right
                    hole_target = curr[0], curr[1]+1
            elif curr[0] != target[0]:
                if curr[0] > target[0]: # target above
                    hole_target = curr[0]-1, curr[1]
                else: # target below 
                    hole_target = curr[0]+1, curr[1]
            else:
                print("clearly my code went wrong")
        else:
            if not self.sequence and target[0] == N-1 \
                and curr[0] == target[0] \
                and curr[1] == target[1]+1 \
                and hole[0] == curr[0] \
                and hole[1] == curr[1]+1: # special case
                    self.sequence = ["right", "right", "down", "left", "up", "left", "down", "right", "right", "up", "left"]
            elif not self.sequence and target[0] == N-1 \
                and curr[0] == target[0] \
                and curr[1] == target[1]+1 \
                and hole[0] == curr[0]-1 \
                and hole[1] == curr[1]: # special case
                    self.sequence = ["left", "up", "right", "right", "down", "left", "up", "left", "down", "right", "right", "up", "left"]
            elif curr[0] != target[0]:
                if curr[0] > target[0]: # target above
                    hole_target = curr[0]-1, curr[1]
                else: # target below 
                    hole_target = curr[0]+1, curr[1]
            elif curr[1] != target[1]: 
                if curr[1] > target[1]: # target to left
                    hole_target = curr[0], curr[1]-1
                else: # target to right
                    hole_target = curr[0], curr[1]+1
            else:
                print("clearly my code went wrong")
        
        if self.sequence:
            move = self.sequence.pop(0)
            move = SliderPuzzleFunctionality.move_mapping.index(move)
            return [move+1]

        if hole == hole_target:
            # move curr into hole
            dy = hole[0] - curr[0]
            dx = hole[1] - curr[1]
            move = {
                (-1, 0): 1,
                (1, 0): 2,
                (0, -1): 3,
                (0, 1): 4,
            }[(dy, dx)]
            return [move]
        else:
            # get the hole to target -> A-Star
            pos = hole
            goal = hole_target
            path = self.pathFind2(pos, goal, walls)
            move = path[0][0] + 1
            return [move]





        



