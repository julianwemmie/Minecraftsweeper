import pygame, random

random.seed(0)

def mainMenu():
    # init pygame

    # load images/sprites

    # pygame loop
    while True:
        
        # event loop

        # draw

        # logic
        if selection == 'normal':
            gameloop()

def gameloop(dim_x = 10, dim_y = 10, num_mines = 10):
    # game variables
    ppg = 30 # pixels per (tile) grid
    info_bar_px = 30
    HEIGHT = ppg * dim_y + ppg * 2 + info_bar_px
    WIDTH = ppg * dim_x + ppg * 2
    clicked = False

    pygame.init()
    screen = pygame.display.set_mode(size = (WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # load background
    top_border = pygame.image.load('graphics/top_border.png').convert()
    bottom_border = pygame.image.load('graphics/bottom_border.png').convert()
    vertical_border = pygame.image.load('graphics/vertical_border.png').convert()

    top_border_rect = top_border.get_rect()
    bottom_border_rect = bottom_border.get_rect()
    vertical_border_rect = vertical_border.get_rect()

    top_border_rect.topleft = (0, 0)
    bottom_border_rect.bottomleft = (0, HEIGHT)
    vertical_border_rect.topleft = (0, 0)

    # loading and configuring sprite/images
    mine = pygame.image.load('graphics/mine.png').convert_alpha()
    tile = pygame.image.load('graphics/tile.png').convert()
    flag = pygame.image.load('graphics/flag.png').convert_alpha()

    mine = pygame.transform.scale(mine, (ppg, ppg))
    tile = pygame.transform.scale(tile, (ppg, ppg))
    flag = pygame.transform.scale(flag, (ppg, ppg))

    mine_rect = pygame.Surface.get_rect(mine)
    tile_rect = pygame.Surface.get_rect(tile)
    flag_rect = pygame.Surface.get_rect(flag)

    minecraft_font = pygame.font.Font('font/MinecraftRegular-Bmg3.otf', 24)

    info_bar = pygame.image.load('graphics/info_bar.png').convert_alpha()
    info_bar_rect = info_bar.get_rect()
    info_bar_rect.center = (WIDTH//2, HEIGHT - ppg)

    # intitalize minesweeper game
    game = minesweeper(dim_x, dim_y, num_mines)

    # pygame loop
    while True:

        if game.isWin():
            winScreen()
            break

        if game.isLoss():
            lossScreen()
            break

        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = False

        # interactions
        mouse_pos = pygame.mouse.get_pos()
        
        # tile collisions and flag detection
        if not clicked:
            for xy in game.getTilesXY():
                tile_rect.topleft = getPXY(xy, ppg)

                # checks for clicking on tile and flag not placed
                if tile_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0] and xy not in game.getFlagsXY():
                    x,y = xy
                    game.removeAdjacentTiles(x, y) # removes blank spaces
                    try: # removes single tile that covers a number
                        game.removeTile(x, y) 
                    except ValueError:
                        pass
                    clicked = True

                if tile_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[2]:
                    x,y = xy
                    if xy in game.getFlagsXY():
                        game.removeFlag(x, y)
                    else:
                        game.addFlag(x, y)
                    clicked = True

         # draw background
        screen.fill(pygame.Color(50,50,50))

        vertical_border_rect.topleft = (0, 0)
        screen.blit(vertical_border, vertical_border_rect)
        vertical_border_rect.topright = (WIDTH, 0)
        screen.blit(vertical_border, vertical_border_rect)

        bottom_border_rect.bottom = HEIGHT - ppg
        screen.blit(bottom_border, bottom_border_rect)
        bottom_border_rect.bottom = HEIGHT
        screen.blit(bottom_border, bottom_border_rect)

        screen.blit(top_border, top_border_rect)

        # draw all entities: tiles, mines, flags, timer, and bomb remaining
        for i, row in enumerate(game.getNeighbors_field()):
            for j, val in enumerate(row):
                if val == 0:
                    continue
                neighbor_text = minecraft_font.render(str(val), False, 'white')

                xy = (j, i)
                xy = getPXY(xy, ppg) # convert grid coordinates to pixel
                x, y = xy

                font_rect = neighbor_text.get_rect()

                font_rect.center = x + ppg//2, y + ppg//2

                screen.blit(neighbor_text, font_rect)


        for xy in game.getMinesXY():
            mine_rect.topleft = getPXY(xy, ppg)
            screen.blit(mine, mine_rect)

        for xy in game.getTilesXY():
            tile_rect.topleft = getPXY(xy, ppg)
            screen.blit(tile, tile_rect)
        
        for xy in game.getFlagsXY():
            flag_rect.topleft = getPXY(xy, ppg)
            screen.blit(flag, flag_rect)

        # flag_count = minecraft_font.render(str(game.getFlagsRemaining()), False, 'black')
        # flag_count_rect = flag_count.get_rect()
        # flag_count_rect.center = (WIDTH//2, HEIGHT - 25)
        # screen.blit(flag_count, flag_count_rect)

        screen.blit(info_bar, info_bar_rect)

        pygame.display.flip()
        clock.tick(60)

def getPXY(coordinates: tuple, ppg):
    '''helper function to convert from minesweeper grid to pixel coordinates'''
    return tuple(map(lambda x: x*ppg + ppg, coordinates))

def winScreen():
    pass

def lossScreen():
    pass

class minesweeper:
    '''game logic'''

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

    def addFlag(self, x, y):
        self.flags.append((x,y))
        self.num_flags += 1

    def removeFlag(self, x, y):
        self.flags.remove((x,y))
        self.num_flags -= 1

    def getTilesXY(self):
        return self.tiles

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

def printBoard(board):
    for line in board:
        print(line)

# game = minesweeper()
# game.removeAdjacentTiles(9,9)
# printBoard(game.getNeighbors_field())
# print()
# printBoard(game.getTilesXY())

gameloop(10, 10, 10)