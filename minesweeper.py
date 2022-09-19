import random

class Minesweeper:
    '''minesweeper game object. contains mechanics and game states'''

    def __init__(self, dim_x = 10, dim_y = 10, num_mines = 10):
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.num_mines = num_mines
        self.num_flags = 0

        self.mines = self.random_mines(num_mines)

        self.flags = []
        self.tiles = [(x, y) for x in range(self.dim_x) for y in range(self.dim_y)]
        self.neighbors_field = [[0 for i in range(self.dim_x)] for j in range(self.dim_y)]

        self.calcNeighbors_field()

    def random_mines(self, num_mines):
        mines = []
        for i in range(num_mines):
            x = random.randint(0, self.dim_x - 1)
            y = random.randint(0, self.dim_y - 1)

            while (x,y) in mines:
                x = random.randint(0, self.dim_x - 1)
                y = random.randint(0, self.dim_y - 1)

            mines.append((x,y))

        return mines

    def getMines(self):
        return self.num_mines

    def getMinesXY(self):
        return self.mines

    def isMine(self, x, y):
        if (x, y) in self.getMinesXY():
            return True
        return False

    def getFlags(self):
        return self.num_flags

    def getFlagsXY(self):
        return self.flags

    def getFlagsRemaining(self):
        return self.getMines() - self.getFlags()

    def getFlagsCorrect(self):
        acc = 0
        for flag in self.getFlagsXY():
            if flag in self.getMinesXY():
                acc += 1
        return acc

    def addFlag(self, x, y):
        self.flags.append((x,y))
        self.num_flags += 1

    def removeFlag(self, x, y):
        self.flags.remove((x,y))
        self.num_flags -= 1

    def getTilesXY(self):
        return self.tiles

    def getEmptyTiles(self):
        return (self.dim_x * self.dim_y) - len(self.getTilesXY())

    def addTile(self, x, y):
        self.tiles.append((x,y))

    def removeTile(self, x, y):
        self.tiles.remove((x,y))

    def removeAdjacentTiles(self, x, y):
        # base cases
        if not self.validIndex(x, y):
            return

        if (x, y) not in self.getTilesXY():
            return

        if (x,y) in self.getMinesXY():
            return

        self.removeTile(x, y)

        # TODO: There's probably a better way to write this
        adjacent = []
        for i in [-1, 1]:
            x_temp = x + i
            if not self.validIndex(x_temp, y):
                continue
            if self.getNeighbors_field()[y][x_temp] in [0,1]:
                adjacent.append((x_temp, y))

        for i in [-1, 1]:
            y_temp = y + i
            if not self.validIndex(x, y_temp):
                continue
            if self.getNeighbors_field()[y_temp][x] in [0,1]:
                adjacent.append((x, y_temp))

        for x,y in adjacent:
            self.removeAdjacentTiles(x, y)


    def resetTiles(self):
        self.tiles = [(x, y) for x in range(self.dim_x) for y in range(self.dim_y)]

    def getNeighbors_field(self):
        return self.neighbors_field

    def calcNeighbors_field(self):
        for xy in self.mines:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0: 
                        continue

                    row_index = xy[0] + i
                    col_index = xy[1] + j

                    # check for invalid incices
                    if not self.validIndex(row_index, col_index):
                        continue
                    
                    self.neighbors_field[col_index][row_index] += 1

    def validIndex(self, x, y):
        if (x < 0 or x >= self.dim_x) or (y < 0 or y >= self.dim_y):
            return False
        return True

    def isWin(self):
        if set(self.getMinesXY()) == set(self.getTilesXY()):
            return True
        return False

    def isLoss(self):
        for mine in self.getMinesXY():
            if mine not in self.getTilesXY():
                return True
        return False