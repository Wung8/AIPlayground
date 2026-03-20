import math, time, random
import numpy as np
import cv2


'''
setGlobals
beginGame
convBoard
displayBoard
getNeighbors
randomMove

'''

def getVars():
    H,W = 6,8
    DIRLOOKUP,DIRS = [],{1,-1,7,-7,8,-8,9,-9}

    # top left is 0th index
    # 6x8 board, rightmost is going to be all 0's to make the math simpler
    for i in range(48):
        DIRLOOKUP.append(DIRS.copy())
        if i//8 == 0: DIRLOOKUP[i] ^= {-7,-8,-9}
        if i//8 == 5: DIRLOOKUP[i] ^= {7,8,9}
    DIRLOOKUP[0] ^= {-1}
    DIRLOOKUP[-1] ^= {1}

    ROWMASK = [int('1111111',2)<<(i*8) for i in range(7)]
    COLMASK = [int('01'*7,16)<<i for i in range(7)]

    WINMASK = []
    horz = int('1111',2)<<24
    for i in range(4): WINMASK.append(horz<<i)
    vert = int('01010101',16)<<3
    for i in range(4): WINMASK.append(vert<<(i*8))
    dia1 = int('000000001'*4,2)
    for i in range(4): WINMASK.append(dia1<<(i*9))
    dia2 = int('0000001'*4+'000000',2)
    for i in range(4): WINMASK.append(dia2<<(i*7))

    return H,W,DIRS,DIRLOOKUP,ROWMASK,COLMASK,WINMASK


class Connect4Env:

    H,W,DIRS,DIRLOOKUP,ROWMASK,COLMASK,WINMASK = getVars()

    def __init__(self, **kwargs):
        self.keys = {}
        pass

    def reset(self):
        self.board = self.beginGame()
        self.player = True
        self.pending_move = 0

    def getState(self):
        rows = self.convBoard(self.board)

        # Convert to 2D array (top row first)
        grid = []
        for r in range(6):
            grid.append([c for c in rows[r]])

        return {
            "grid": grid,                 # 6x7 array of '.', 'x', 'o'
            "player": 'o' if self.player else 'x',
            "pending_move": self.pending_move  # 0–6
        }

    def getInputs(self):
        rows = self.convBoard(self.board)

        # Convert to 2D array (top row first)
        grid = []
        for r in range(6):
            grid.append([c for c in rows[r]])

        return {
            "p1": {
                "grid": grid,                 # 6x7 array of '.', 'x', 'o'
                "player": 'o' if self.player else 'x',
                "pending_move": self.pending_move  # 0–6
            },
            "p2": {
                "grid": grid,                 # 6x7 array of '.', 'x', 'o'
                "player": 'o' if self.player else 'x',
                "pending_move": self.pending_move  # 0–6
            }
        }

    def step(self, actions, keyboard={}, display=False):
        board = self.board
        player = self.player

        if player:
            action = actions["p1"]
        else:
            action = actions["p2"]

        if action == "keyboard":
            action = [0]
            for i in range(1, 8):
                if keyboard.get(f"{i}"): action[0] = i
            if keyboard.get(" ") and not self.keys.get(" "): action[0] = 8
            if keyboard.get("ArrowLeft") and not self.keys.get("ArrowLeft"): action[0] = max(1, self.pending_move + 1 - 1)
            if keyboard.get("ArrowRight") and not self.keys.get("ArrowRight"): action[0] = min(7, self.pending_move + 1 + 1)
            if keyboard.get("ArrowDown") and not self.keys.get("ArrowDown"): action[0] = 8

        self.keys = keyboard
        
        action = action[0]

        done = False
        if action == 8:
            usr = self.pending_move
            nbrs = self.getNeighbors(player,board,indexed=True)
            if nbrs[usr] != -1:
                move = board[2]^nbrs[usr][2]
                board = nbrs[usr]

                if self.checkWin(player,move,board=board): done = True

                self.board = board
                self.player = not player
        elif action != 0:
            self.pending_move = action - 1
        else:
            pass

        return board, 0, done

    def ffs(self, i):
        return i&-i

    def beginGame(self, ):
        return (0,0,0)

    def getRows(self, board):
        return [(board & self.ROWMASK[i])>>(i*8) for i in range(7)]

    def getCols(self, board):
        return [(board & self.COLMASK[i]) for i in range(7)]

    def convBoard(self, board=None, player=True):
        if board is None: board = self.board
        players = {('0','0'):'.',('1','0'):'x',('0','1'):'o',('1','1'):'!'}
        toreturn = []
        for row in range(6):
            zipped = zip(('0'*90+bin(board[0])[2:])[::-1][row*8:row*8+7],('0'*90+bin(board[1])[2:])[::-1][row*8:row*8+7])
            toreturn.append("".join([players[z] for z in zipped]))
        return toreturn

    def displayBoard(self, board=None, player=None, return_only=False):
        if board is None: board = self.board
        players = {('0','0'):'.',('1','0'):'x',('0','1'):'o',('1','1'):'!'}
        disp = '-------'
        for row in range(6):
            zipped = zip(('0'*90+bin(board[0])[2:])[::-1][row*8:row*8+7],('0'*90+bin(board[1])[2:])[::-1][row*8:row*8+7])
            disp += '\n'+' '.join([players[z] for z in zipped])
        disp += '\n-------'
        if not return_only:
            print()
            print(disp)
            print('1 2 3 4 5 6 7')
            print(board,',',player)
        return disp.strip()
    
    def display(self):
        def blend(c1, c2):
            return tuple((c1[i] + c2[i]) / 2 for i in range(3))

        board = self.board
        player = self.player
        pending_move = self.pending_move

        # Convert board to readable rows
        rows = self.convBoard(board)

        # Create blank image (800x400)
        img = np.zeros((400, 800, 3), dtype=np.uint8)

        # Colors (BGR)
        board_color = (92, 66, 61)    # softer yellow board
        empty_color = (55, 45, 45)
        x_color = (255, 200, 120)        # deeper blue
        o_color = (120, 200, 255)        # softer yellow-ish (BGR!)

        # Board layout
        cols = 7
        rows_n = 6
        cell_w = 66
        cell_h = 66
        offset = (800 - cols * cell_w) // 2

        # Draw board background
        img[:] = board_color

        # Draw cells
        for r in range(rows_n):
            for c in range(cols):
                # Flip row so bottom is bottom visually
                val = rows[r][c]

                center = (
                    c * cell_w + cell_w // 2 + offset,
                    r * cell_h + cell_h // 2
                )

                radius = min(cell_w, cell_h) // 3

                # Draw empty slot
                cv2.circle(img, center, radius, empty_color, -1)

                # Draw pieces
                if val == 'x':
                    cv2.circle(img, center, radius, x_color, -1)
                elif val == 'o':
                    cv2.circle(img, center, radius, o_color, -1)
        
        r = 0
        for r in range(rows_n):
            if rows[r][pending_move] != ".":
                break
        else:
            r = rows_n
        
        if r != 0:
            r = r - 1
            c = pending_move

            center = (
                c * cell_w + cell_w // 2 + offset,
                r * cell_h + cell_h // 2
            )

            radius = min(cell_w, cell_h) // 3

            color = o_color if player else x_color
            color = blend(color, empty_color)

            cv2.circle(img, center, radius, color, -1)


        # Display current player
        '''
        text = f"Player: {'o' if player else 'x'}"
        cv2.putText(img, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)
        '''

        # Show image
        cv2.imshow("Connect4", img)
        cv2.waitKey(1)

        
    # if indexed==True will return list of possible boards with invalid moves as -1
    def getNeighbors(self, player, board=None, indexed=False, return_move=False):
        if board is None: board = self.board
        toreturn = []
        for n,col in enumerate(self.getCols(board[2])):
            if col & self.ROWMASK[0]:
                if indexed: toreturn.append(-1)
                continue
            i = self.ffs(col)>>8
            if not i: i = 1<<(40+n)
            newboard = (board[0]|(i*(not player)), board[1]|(i*player), board[2]|i)
            if return_move: toreturn.append((newboard,i))
            else: toreturn.append(newboard)

        return toreturn
        
    def checkWin(self, player, move, board=None):
        if board is None: board = self.board
        check = board[player]
        shift = 27-int(math.log(move,2))
        if shift < 0: check>>=abs(shift)
        if shift > 0: check<<=abs(shift)
            
        for mask in self.WINMASK:
            if check & mask == mask:
                return True

        return False



# player == True if o player == False if x
# board = [x tokens, o tokens, x+o tokens] in bits
if __name__ == '__main__':
  import keyboard as k
  import time
  env = Connect4Env()
  env.reset()
  done = False
  while 1:
    keys = {}

    for key in "1234567":
        if k.is_pressed(key): keys[key] = True
    if k.is_pressed("space"): keys[" "] = True
    if k.is_pressed("left"): keys["ArrowLeft"] = True
    if k.is_pressed("right"): keys["ArrowRight"] = True
    if k.is_pressed("down"): keys["ArrowDown"] = True

    _,_,done = env.step(actions={"p1": "keyboard", "p2": "keyboard"}, keyboard=keys)
    env.display()

    time.sleep(1/10)

  #print(['x','o'][env.player],'wins')
  #env.displayBoard()






    