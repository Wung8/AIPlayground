import pygame
import numpy as np
import random, math, os
from noise import pnoise2
import keyboard as k
import cv2

'''
-1 = bedrock
0 = water
1 = grass
2 = tree
3 = bush
4 = stone
5 = wall
6 = plank
7 = diamond
'''

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def open_png(file):
    return pygame.image.load(__location__ + f"\sprites\{file}.png")

nontraversable_mask = (0,0,1,1,0,1,0,1)
block_mask = (0,0,0,0,0,1,0,1)

cursor = open_png("cursor")

nums = [open_png(f"{i}") for i in range(10)]
info_bar = open_png("info_bar")
info_locs = [
    (13, 72), (29, 72), (45, 72), (60, 72),
    (29, 80), (45, 80), (60, 80),
]
wood_pickaxe = open_png("wood_pickaxe")
stone_pickaxe = open_png("stone_pickaxe")
wood_sword = open_png("wood_sword")
stone_sword = open_png("stone_sword")

player = open_png("player")
water = open_png("water")
grass = open_png("grass")
grass_shadow = open_png("grass_shadow")
stone = open_png("stone")
stone_shadow = open_png("stone_shadow")
stone_wall = open_png("stone_wall")
trees = [
    open_png("tree_0"),
    open_png("tree_1"),
    open_png("tree_2"),
    open_png("tree_3"),
    open_png("tree_4")
]
bushes = [open_png("bush"), open_png("berry_bush")]
plank = open_png("plank")
diamond = open_png("diamond")

bad_guy = [open_png("bad_guy"), open_png("bad_guy_attack"), open_png("bad_guy_attack_fin")]
big_bad_guy = [open_png("big_bad_guy"), open_png("big_bad_guy_attack"), open_png("big_bad_guy_attack_fin")]

score_bar = open_png("score_bar")
crafting_bar = open_png("crafting_bar")
stick_icon = open_png("stick_icon")
stone_icon = open_png("stone_icon")

SCALE = 10
COLORS = {
    'bg':(40,40,40),
    'water':(60, 60, 150),
    'grass':(100, 150, 50),
    'stone':(100, 100, 100)
}

def brighten_image(image, factor=0.5):
    """Returns a brightened version of a given Pygame surface."""
    arr = pygame.surfarray.pixels3d(image).astype(np.float32)  # Get RGB pixels
    alpha = pygame.surfarray.pixels_alpha(image)
    arr = (1-factor) * arr + 255 * factor

    bright_image = pygame.surfarray.make_surface(arr.astype(np.uint8))  # Convert back to surface
    bright_image = bright_image.convert_alpha()
    pygame.surfarray.pixels_alpha(bright_image)[:] = alpha  # Apply original alpha
    return bright_image

def dim_screen(surface, factor):
    rect_surf = pygame.Surface((72, 72), pygame.SRCALPHA)
    rect_surf.fill((0, 0, 0, factor))
    surface.blit(rect_surf, (0, 0))

def gen_square_mask(position, size=11):
    arr = np.zeros((80, 80), dtype=np.uint8)  # Create 80x80 array of zeros
    
    half = size // 2
    x, y = position
    
    # Define the bounds of the square, ensuring it stays within the array
    x_min, x_max = max(0, x - half), min(80, x + half + size%2)
    y_min, y_max = max(0, y - half), min(80, y + half + size%2)
    
    # Set the square region to 1
    arr[y_min:y_max, x_min:x_max] = 1
    
    return arr

class BadGuy:
    def __init__(self, env, pos):
        self.env = env
        self.health = 8
        self.pos = pos

        self.max_tick = 2
        self.tick = random.randint(-1,1)
        self.damaged = 0
        self.attacking = 0
        self.dir = 1
        self.move = False

    def display(self, pos, pre_tick=False):
        x,y = pos
        img = bad_guy[self.attacking]
        if self.dir == -1:
            img = pygame.transform.flip(img, True, False)
        if self.move and pre_tick:
            x,y = x-self.move[0]/2, y-self.move[1]/2
        if self.damaged and pre_tick:
            self.env.surface.blit(brighten_image(img.copy()), (x*8, y*8-4))
        else: self.env.surface.blit(img, (x*8, y*8-4))

    def step(self):
        self.move = False
        self.damaged = 0
        self.tick += 1

        curr_tile = self.env.map[*self.pos[::-1]]
        if curr_tile[0] and not curr_tile[6]:
            self.env.score += 1_000
            return -1
                     
        if np.any(damage_tile := np.argwhere(self.env.damage_map==1)):
            damage_tile = damage_tile[0][::-1]
            if all(np.equal(damage_tile, self.pos)):
                self.health -= 2**self.env.player_sword
                new_tile = np.add(self.pos, np.subtract(self.pos, self.env.player_pos))
                self.damaged = 1
                self.attacking = 0
                self.tick = 0
                if self.env.check_move(new_tile, exception=(0,0,1,0,0,0,0,0)) != -1:
                    self.pos = new_tile
                    self.env.get_bad_guys()
                if self.health <= 0:
                    self.env.score += 1_000
                    return -1

        if self.tick != 2: return 0
        self.tick = 0

        if self.attacking:
            self.attacking = 2
            if math.dist(self.pos, self.env.player_pos) == 1:
                if self.env.player_invincibility == 0:
                    self.env.player_invincibility = 6
                    self.env.player_health -= 1
                    self.env.damaged = 1
            return 0
                
        if math.dist(self.pos, self.env.player_pos) >= 5:
            self.wander()
        elif math.dist(self.pos, self.env.player_pos) == 1:
            self.attacking = 1
        else:
            parseme = [tuple(self.pos)]
            seen = {tuple(self.pos):-1}
            while parseme:
                p = parseme.pop(0)
                for nbr in self.get_nbrs(p):
                    if math.dist(nbr, tuple(self.env.player_pos)) >= 5: continue
                    if nbr in seen: continue
                    seen[nbr] = p
                    parseme.append(nbr)
                if tuple(self.env.player_pos) in seen:
                    break

            if tuple(self.env.player_pos) not in seen:
                self.wander()
                return 0

            new_tile = seen[tuple(self.env.player_pos)]
            if seen[new_tile] == -1:
                move = tuple(np.subtract(tuple(self.env.player_pos), self.pos))
                return 0
            
            while seen[new_tile] != tuple(self.pos):
                new_tile = seen[new_tile]

            if new_tile != tuple(self.env.player_pos):
                move = tuple(np.subtract(new_tile, self.pos))
                self.pos = new_tile
                if move == (1,0): self.dir = 1
                if move == (-1,0): self.dir = -1
                self.move = move
            
        self.env.get_bad_guys()

    def wander(self):
        move = random.choice([
            (0,0),
            (0,0),
            (0,0),
            (0,0),
            (0,0),
            (0,0),
            (0,0),
            (0,0),
            (0,1),
            (0,-1),
            (1,0),
            (-1,0)
        ])
        new_tile = np.add(self.pos, move)
        if self.env.check_move(new_tile, exception=(0,0,1,0,0,0,0,0)) != -1:
            self.pos = new_tile
            if move == (1,0): self.dir = 1
            if move == (-1,0): self.dir = -1

    def get_nbrs(self, pos):
        target = tuple(self.env.player_pos)
        moves = [(0,1),
                 (0,-1),
                 (1,0),
                 (-1,0)]
        nbrs = []
        for m in moves:
            new_tile = np.add(pos, m)
            if self.env.check_move(new_tile, exception=(0,0,1,0,0,0,0,0)) != -1:
                nbrs.append((math.dist(target, new_tile), tuple(new_tile)))
        if not nbrs: return []
        nbrs = sorted(nbrs)
        return list(zip(*nbrs))[1]
        
        

class CrafterEnv:
    def __init__(self, render_mode="None", **kwargs):
        self.render_mode = render_mode
        self.screen_size = 72, 96
        self.num_unique_tiles = 8
        self.map_size = 80, 80
        self.display_prev = False

        self.tick = 0
        self.max_tick = 200

        self.display_prev = False
        self.surface = pygame.Surface(self.screen_size, pygame.SRCALPHA) 
        self.screen = pygame.display.set_mode(np.multiply(self.screen_size, SCALE), flags=[pygame.HIDDEN, pygame.SHOWN][render_mode=="human"])
        self.clock = pygame.time.Clock()

    def reset(self):
        self.score = 0
        self.prev_score = 0
        self.tick = 0
        self.pre_tick = False
        
        self.generate_map()
        self.grow_stack = []
        self.tree_stack = []
        self.spawn_locs = np.argwhere(
            (self.map[:,:,1] == 1) * (self.map[:,:,5] == 0) * (self.map[:,:,2] == 0) * (self.map[:,:,3] == 0)
        )
        self.player_pos = self.spawn_locs[np.random.choice(len(self.spawn_locs))][::-1]
        self.player_dir = (1,0)
        
        self.player_health = 7
        self.player_hunger = 7
        self.player_thirst = 7
        self.player_energy = 7
        self.damaged = 0
        self.dir = (1,0)

        self.player_pickaxe = 0
        self.player_sword = 0
        self.player_invincibility = 0

        self.block_health = 8
        self.old_target = -1,-1

        self.sticks = 0
        self.stone = 0
        self.planks = 5

        self.sleeping = 0
        self.sleep_amount = 0
        self.crafting = 0
        self.crafting_slots = []

        self.badguys = []

        self.bad_guys_map = self.get_bad_guys()
        self.damage_map = np.zeros((80,80), dtype=np.uint8)

        return self.display(disp=False), {}  

    def getState(self):
        px, py = map(int, self.player_pos)

        view = 9
        half = view // 2

        tiles = []
        for y in range(py - half, py + half + 1):
            row = []
            for x in range(px - half, px + half + 1):
                if self.out_of_bounds((x, y)):
                    row.append(None)
                    continue

                tile = self.map[y][x]

                row.append({
                    "water": int(tile[0]),
                    "grass": int(tile[1]),
                    "tree": int(tile[2]),
                    "bush": int(tile[3]),
                    "stone": int(tile[4]),
                    "wall": int(tile[5]),
                    "plank": int(tile[6]),
                    "diamond": int(tile[7]),
                    "tree_id": int(self.tree_map[y][x]),
                    "berry": int(self.berry_map[y][x]),
                    "damage": int(self.damage_map[y][x])
                })
            tiles.append(row)

        enemies = []
        for bg in self.badguys:
            ex, ey = map(int, bg.pos)
            if abs(ex - px) <= half and abs(ey - py) <= half:
                enemies.append({
                    "x": int(ex - px + half),
                    "y": int(ey - py + half),
                    "hp": int(bg.health),
                    "attacking": int(bg.attacking),
                    "dir": int(bg.dir),
                    "damaged": int(bg.damaged),
                    "move": (int(bg.move[0]),int(bg.move[1])) if bg.move else None
                })

        return {
            "tiles": tiles,
            "player": {
                "x": half,
                "y": half,
                "dir": list(map(int, self.player_dir)),
                "disp_dir": list(map(int, self.dir)),
                "health": float(self.player_health),
                "damaged": int(self.damaged)
            },
            "enemies": enemies,
            "pre_tick": self.pre_tick,
            "sleep": self.sleep_amount,
            "score": int(self.score),
            
            "inventory": {
                "wood": int(self.sticks),
                "stone": int(self.stone),
                "planks": int(self.planks)
            },
            "hunger": int(self.player_hunger),
            "thirst": int(self.player_thirst),
            "energy": float(self.player_energy),

            "player_pickaxe": int(self.player_pickaxe),
            "player_sword": int(self.player_sword),

            "crafting": int(self.crafting),
            "crafting_slots": list(map(int, self.crafting_slots)),
        }   
    
    def getInputs(self):
        px, py = self.player_pos

        view = 9  
        half = view // 2

        tiles = []
        for y in range(py - half, py + half + 1):
            row = []
            for x in range(px - half, px + half + 1):
                if self.out_of_bounds((x, y)):
                    row.append(-1)
                    continue

                tile = self.map[y][x]

                if tile[7]: val = 7
                elif tile[5]: val = 5
                elif tile[6]: val = 6
                elif tile[4]: val = 4
                elif tile[2]: val = 2
                elif tile[3]: val = 3
                elif tile[1]: val = 1
                elif tile[0]: val = 0
                else: val = -1

                row.append(val)
            tiles.append(row)

        # bad guys in view
        enemies = []
        for bg in self.badguys:
            ex, ey = bg.pos
            if abs(ex - px) <= half and abs(ey - py) <= half:
                enemies.append({
                    "x": ex - px,
                    "y": ey - py,
                    "dir": bg.dir,
                    "health": bg.health
                })

        state = {
            "tiles": tiles,
            "player": {
                "dir": self.player_dir,
                "health": self.player_health,
            },
            "inventory": {
                "wood": self.sticks,
                "stone": self.stone,
                "planks": self.planks
            },
            "enemies": enemies,
            "pre_tick": self.pre_tick,
            "sleep": self.sleep_amount,
            "score": int(self.score),
            
            "inventory": {
                "wood": int(self.sticks),
                "stone": int(self.stone),
                "planks": int(self.planks)
            },
            "hunger": int(self.player_hunger),
            "thirst": int(self.player_thirst),
            "energy": float(self.player_energy),

            "player_pickaxe": int(self.player_pickaxe),
            "player_sword": int(self.player_sword),

            "crafting": int(self.crafting),
            "crafting_slots": list(map(int, self.crafting_slots)),
        }

        return {"p1": state}  
        
        
    def step(self, actions, keyboard={}, display=False):
        action = actions[f"p1"]
        if action == "keyboard":
            action = [0,0,0,0,0,0]

            if keyboard.get('ArrowUp'): action[0] = 3
            if keyboard.get('ArrowLeft'): action[0] = 1
            if keyboard.get('ArrowDown'): action[0] = 4
            if keyboard.get('ArrowRight'): action[0] = 2

            if keyboard.get('z'): action[1] = 1
            if keyboard.get('x'): action[2] = 1
            if keyboard.get('s'): action[3] = 1
            if keyboard.get('a'): action[4] = 1
            if keyboard.get('c'): action[5] = 1
            
        self.pre_tick = not self.pre_tick
        if not self.pre_tick: 
            if self.render_mode=="human": self.display(pre_tick=False)

            obs = self.display(disp=False)
            reward = self.score - self.prev_score
            self.prev_score = self.score
            done = (self.player_health <= 0) or (self.score >= 9999999)

            for e in self.badguys:
                if e.attacking == 2:
                    e.attacking = 0

            return obs, reward, done
        self.damaged = 0
        self.tick += 1
        if self.tick % 5 == 0: self.score += 5
        self.player_invincibility = max(0, self.player_invincibility-1)
        if self.tick == self.max_tick:
            self.tick = 0

        if self.tick % 100 == 0:
            self.player_hunger = max(self.player_hunger-1, 0)
        if self.tick % 50 == 0:
            self.player_thirst = max(self.player_thirst-1, 0)
        if self.tick % 200 == 0:
            self.player_energy = max(self.player_energy-1, 0)
        if self.tick % 50 == 0:
            if self.player_hunger==0 or self.player_thirst==0 or self.player_energy==0:
                self.player_health = max(self.player_health-1, 0)
                self.damaged = 1
                
        self.player_hunger = max(self.player_hunger, 0)
        self.player_thirst = max(self.player_thirst, 0)
        self.player_energy = max(self.player_energy, 0)
        self.player_health = max(self.player_health, 0)
        
        if self.player_hunger>=5 and self.player_thirst>=5 and self.player_energy>=5:
            self.player_health = min(self.player_health+1/25, 7)

        if self.crafting:
            self.sleeping = 0
            action[3] = 0
            if len(self.crafting_slots) == 3:
                if all(np.equal(self.crafting_slots, (0,0,0))) and self.planks<7:
                    self.planks += 1
                    self.crafting_slots = []
                elif all(np.equal(sorted(self.crafting_slots), (0,0,1))) and not self.player_pickaxe:
                    self.player_pickaxe = 1
                    self.crafting_slots = []
                    self.score += 750
                elif all(np.equal(sorted(self.crafting_slots), (0,1,1))) and not self.player_sword:
                    self.player_sword = 1
                    self.crafting_slots = []
                    self.score += 750
                self.crafting = False
            if action[1] and self.sticks > 0:
                self.crafting_slots.append(0)
                self.sticks -= 1
            elif action[2] and self.stone > 0:
                self.crafting_slots.append(1)
                self.stone -= 1

        if not self.crafting:
            if self.crafting_slots:
                for i in self.crafting_slots:
                    if i == 0: self.sticks += 1
                    if i == 1: self.stone += 1
            self.crafting_slots = []

        if action[5] == 1:
            self.crafting = 1-self.crafting

        if self.sleeping == 1 or self.crafting == 1:
            action[0] = 0
            action[1] = 0
            action[2] = 0
            action[4] = 0

        self.bad_guys_map = self.get_bad_guys()
        self.damage_map = np.zeros((80,80), dtype=np.uint8)
        self.player_move(action[0])
        
        target = np.add(self.player_pos, self.player_dir)
        if not self.out_of_bounds(target):
            target_tile = self.map[target[1]][target[0]]
        else: target_tile = [0]*8
        
        if not np.all(self.old_target==target) or self.block_health<=0:
            if target_tile[2] == 1: self.block_health = 4
            if target_tile[5] == 1: self.block_health = 8
            if target_tile[6] == 1 and target_tile[5] == 0: self.block_health = 4
            if target_tile[7] == 1: self.block_health = 24
        
        if action[1]:
            if not self.out_of_bounds(target):
                self.damage_map[target[1]][target[0]] = 1
            self.block_health -= 4**self.player_pickaxe
            if self.block_health == 0:
                if target_tile[2] == 1:
                    self.score += 50
                    self.sticks = min(self.sticks+1, 7)
                    target_tile[2] = 0
                    self.tree_stack.append([2000,target])
                    self.player_energy -= 1/10
                if target_tile[5] == 1:
                    self.score += 100
                    self.stone = min(self.stone+1, 7)
                    target_tile[5] = 0
                    self.player_energy -= 1/10
                if target_tile[6] == 1 and target_tile[5] == 0:
                    self.planks = min(self.planks+1, 7)
                    target_tile[6] = 0
                    self.player_energy -= 1/10
                if target_tile[7] == 1:
                    self.score += 10_000
                    target_tile[7] = 0
                    self.player_energy -= 1/10
        
        if action[2]:
            if target_tile[0] and not target_tile[6]:
                self.player_thirst = min(self.player_thirst+1, 7)
            elif target_tile[3]:
                if self.player_hunger < 7 and self.berry_map[target[1]][target[0]] == 1:
                    self.player_hunger = min(self.player_hunger+1, 7)
                    self.berry_map[target[1]][target[0]] = 0
                    self.grow_stack.append([1000, target])

        if action[4]:
            if (target_tile[1] or target_tile[6]) and not any(np.multiply(target_tile, nontraversable_mask)):
                if self.stone > 0:
                    self.stone -= 1
                    target_tile[5] = 1
            if target_tile[0] and not target_tile[6]:
                if self.planks > 0:
                    self.planks -= 1
                    target_tile[6] = 1

        if action[3]:
            self.sleeping = 1-self.sleeping

        if self.sleeping == 1:
            self.sleep_amount = min(self.sleep_amount+1, 10)
            if self.player_energy == 7:
                self.sleeping = 0
                self.sleep_amount = 0
            if self.sleep_amount == 10 and self.tick%3 == 0:
                self.player_energy = min(self.player_energy+1, 7)
        else:
            self.sleep_amount = 0

        self.old_target = target
            

        for item in self.grow_stack:
            item[0] -= 1
            if item[0] == 0:
                self.berry_map[item[1][1]][item[1][0]] = 1
            del item

        for item in self.tree_stack:
            item[0] -= 1
            if item[0] == 0:
                if not any(self.map[item[1][1]][item[1][0]] * block_mask == 1) and not all(np.equal(item[1],self.player_pos)):
                    self.map[item[1][1]][item[1][0]][2] = 1
                else:
                    self.tree_stack.append([2000, (item[1][0],item[1][1])])
                    del item

        for n,bg in list(enumerate(self.badguys))[::-1]:
            result = bg.step()
            if result == -1:
                del self.badguys[n]

        if random.random() < 1/1:
            bad_guys_map = self.get_bad_guys()
            pos = np.argwhere(self.map[:,:,3] * (1-gen_square_mask(self.player_pos)))
            if len(pos) != 0:
                pos = pos[np.random.choice(len(pos))]
                if not np.any(bad_guys_map * gen_square_mask(pos[::-1], 5) == 1):
                    spawn_idxs = gen_square_mask(pos, 3) * (np.random.rand(80,80) < 1/5)
                    spawn_idxs = np.argwhere(spawn_idxs == 1)
                    for idx in spawn_idxs:
                        if not any(self.map[*idx[::-1]] * (1,0,0,1,0,1,1,1) == 1) and not bad_guys_map[*idx[::-1]]:
                            self.badguys.append(BadGuy(self, idx))
        

        if self.render_mode=="human": self.display(pre_tick=True)
        obs = self.display(disp=False)
        reward = self.score - self.prev_score
        self.prev_score = self.score
        done = (self.player_health <= 0) or (self.score >= 9999999)

        return obs, reward, done
        
    
    def display(self, pre_tick=False, disp=True):
        pygame.event.pump()
        self.surface.fill(COLORS['bg'])
        to_display = []
        for x in range(9):
            for y in range(10):
                map_coords = (x + self.player_pos[0] - 4, y + self.player_pos[1] - 4)
                if self.out_of_bounds(map_coords):
                    continue
                tile = self.map[map_coords[1]][map_coords[0]]
                brighten = self.damage_map[map_coords[1]][map_coords[0]]
                
                color = COLORS['bg']
                add_shadow = False
                for bg in self.badguys:
                    if all(np.equal(bg.pos, map_coords)):
                        add_shadow = True
                        if bg.move and pre_tick:
                            to_display.append((bg, (x,y)))
                        break
                        
                if tile[0] == 1: self.surface.blit(water, (x*8, y*8))
                if tile[1] == 1:
                    if any(tile[2:]) or (x,y)==(4,4) or add_shadow: self.surface.blit(grass_shadow, (x*8, y*8))
                    else: self.surface.blit(grass, (x*8, y*8))
                if tile[4] == 1:
                    if any(tile[5:]) or (x,y)==(4,4) or add_shadow: self.surface.blit(stone_shadow, (x*8, y*8))
                    else: self.surface.blit(stone, (x*8, y*8))
                if tile[6] == 1:
                    self.surface.blit(plank, (x*8, y*8))
                    if pre_tick and brighten:
                        self.surface.blit(brighten_image(plank.copy()), (x*8, y*8))
                if tile[5] == 1:
                    self.surface.blit(stone_wall, (x*8, y*8 - 4))
                    if pre_tick and brighten:
                        self.surface.blit(brighten_image(stone_wall.copy()), (x*8, y*8 - 4))
                if tile[7] == 1:
                    self.surface.blit(diamond, (x*8, y*8 - 4))
                    if pre_tick and brighten:
                        self.surface.blit(brighten_image(diamond.copy()), (x*8, y*8 - 4))
                if tile[2] == 1:
                    tree_id = self.tree_map[y + self.player_pos[1] - 4][x + self.player_pos[0] - 4]
                    self.surface.blit(trees[tree_id], (x*8, y*8-4))
                    if pre_tick and brighten:
                        self.surface.blit(brighten_image(trees[tree_id]), (x*8, y*8 - 4))
                if tile[3] == 1:
                    bush_id = self.berry_map[y + self.player_pos[1] - 4][x + self.player_pos[0] - 4]
                    self.surface.blit(bushes[bush_id], (x*8, y*8))
                    if pre_tick and brighten:
                        self.surface.blit(brighten_image(bushes[bush_id]), (x*8, y*8))
                if add_shadow == True:
                    bg.display((x,y), pre_tick)
                if (x,y) == (4,4):
                    img = player
                    if self.dir == (-1,0): img = pygame.transform.flip(img, True, False)
                    self.surface.blit(img, (4*8, 4*8))
                    if pre_tick and self.damaged: self.surface.blit(brighten_image(img), (4*8, 4*8))
        for item in to_display:
            item[0].display(item[1], True)
        self.surface.blit(info_bar, (0,72))

        self.surface.blit(nums[math.ceil(self.player_health)], info_locs[0])
        self.surface.blit(nums[self.player_hunger], info_locs[1])
        self.surface.blit(nums[self.player_thirst], info_locs[2])
        self.surface.blit(nums[math.ceil(self.player_energy)], info_locs[3])
        self.surface.blit(nums[self.sticks], info_locs[4])
        self.surface.blit(nums[self.stone], info_locs[5])
        self.surface.blit(nums[self.planks], info_locs[6])
        
        if self.player_pickaxe:
            self.surface.blit(stone_pickaxe, (4,79))
        if self.player_sword:
            self.surface.blit(stone_sword, (11,79))
            
        if self.crafting == 1:
            dim_screen(self.surface, 80)
            self.surface.blit(crafting_bar, (23,58))
            for n,item in enumerate(self.crafting_slots):
                if item == 0: self.surface.blit(stick_icon, (26+9*n,61))
                if item == 1: self.surface.blit(stone_icon, (26+9*n,61))
        else:
            cursor_loc = np.add((4,4), self.player_dir) * 8
            target = np.add(self.player_pos, self.player_dir)
            if not self.out_of_bounds(target):
                target_tile = self.map[target[1]][target[0]]
            else: target_tile = [0]*8
            if any(np.multiply(target_tile, block_mask)):
                self.surface.blit(cursor, np.subtract(cursor_loc, (0,3)))
            else:
                self.surface.blit(cursor, cursor_loc)
            dim_screen(self.surface, self.sleep_amount * 10)

        self.surface.blit(self.surface, (0,8))
        self.surface.blit(score_bar, (0,0))
        score_str = ('00000000' + str(self.score))[-7:]
        for i in range(7):
            self.surface.blit(nums[int(score_str[i])], (33+4*i,0))

        if disp == False:
            obs = pygame.surfarray.array3d(self.surface)
            #obs = np.transpose(pygame.surfarray.array3d(self.surface), (2,0,1))
            obs = cv2.resize(obs, (64,64), interpolation = cv2.INTER_AREA)
            return obs
        
        pygame.transform.scale(self.surface, (np.multiply(self.screen_size, SCALE)), self.screen)
        pygame.display.flip()
        self.clock.tick(10)

    def out_of_bounds(self, pos):
        return pos[0] < 0 or pos[0] >= 80 or pos[1] < 0 or pos[1] >= 80
        
    def generate_noise(self):
        xpix, ypix = self.map_size
        shift_x, shift_y = random.randint(0,10000), random.randint(0,10000)
        return np.array([[pnoise2((i+shift_x)/xpix*6, (j+shift_y)/ypix*6, octaves=12)
                          for j in range(xpix)] for i in range(ypix)])

    def generate_map(self):
        self.map = np.zeros((self.num_unique_tiles, *self.map_size), dtype=np.uint8)
        xpix, ypix = self.map_size
        shift_x, shift_y = random.randint(0,10000), random.randint(0,10000)
        noise = self.generate_noise()

        self.map[0] = noise < np.mean(noise)-0.04
        self.map[1] = noise >= np.mean(noise)-0.04
        self.map[4] = noise >= np.mean(noise)+0.12
        self.map[5] = noise >= np.mean(noise)+0.2

        self.map[3] = (np.random.rand(80,80) < 1/40) * self.map[1] * (1-self.map[4])
        self.map[7] = (noise >= np.mean(noise)+0.24) * (np.random.rand(80,80) < 0.05)
        self.map[5] *= (1-self.map[7])
        
        noise = self.generate_noise()
        self.map[2] = (noise > np.mean(noise)+0.08) * self.map[1] * (1-self.map[3]) *\
                        (1-self.map[4]) * (np.random.rand(80,80) < 0.5)
        
        self.map = self.map.transpose(1,2,0)
        self.tree_map = np.random.choice([0, 1, 2, 3, 4], size=(80, 80))
        self.berry_map = np.zeros((80,80), dtype=np.uint8) + 1
        return self.map

    def player_move(self, action):
        if action == 0: return
        if action == 1:
            move_dir = (-1,0)
            self.dir = move_dir
        if action == 2:
            move_dir = (1,0)
            self.dir = move_dir
        if action == 3: move_dir = (0,-1)
        if action == 4: move_dir = (0,1)

        if self.player_dir != move_dir:
            self.player_dir = move_dir
            return

        self.player_dir = move_dir
        new_pos = np.add(self.player_pos, move_dir)
        if self.check_move(new_pos) == -1: return

        self.player_pos = new_pos
        self.player_energy -= 1/20

    def check_move(self, new_pos, exception=(0,0,0,0,0,0,0,0)):
        if self.out_of_bounds(new_pos): return -1
        new_tile = self.map[new_pos[1]][new_pos[0]]
        if any(np.multiply(new_tile, np.multiply(nontraversable_mask, np.subtract(1,exception)))): return -1
        if self.bad_guys_map[*new_pos[::-1]] == 1: return -1
        if new_tile[0] == 1 and new_tile[6] == 0: return -1
        return 0

    def get_bad_guys(self):
        toreturn = np.zeros((80,80), dtype=np.uint8)
        for bg in self.badguys:
            pos = bg.pos
            toreturn[pos[1]][pos[0]] = 1
        self.bad_guys_map = toreturn
        return toreturn

        
        

def get_user_actions():
    # _:0 left:1 right:2, up:3, down:4

    actions = [0,0,0,0,0,0]
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]: actions[0] = 1
    if keys[pygame.K_RIGHT]: actions[0] = 2
    if keys[pygame.K_UP]: actions[0] = 3
    if keys[pygame.K_DOWN]: actions[0] = 4
    
    if keys[pygame.K_z]: actions[1] = 1
    if keys[pygame.K_x]: actions[2] = 1
    if keys[pygame.K_s]: actions[3] = 1
    if keys[pygame.K_a]: actions[4] = 1
    if keys[pygame.K_c]: actions[5] = 1

    return actions

if __name__ == '__main__':
    pygame.init()
    env = CrafterEnv(render_mode="human")
    env.reset()
    
    while True:
        actions = get_user_actions()
        obs, reward, done = env.step({"p1":actions}, display=True)
        #input(obs)
        if done:
            env.reset()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()


