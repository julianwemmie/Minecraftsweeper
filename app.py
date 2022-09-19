import pygame
from minesweeper import Minesweeper

class Scene:
    '''abstract class that scene instances are derived from'''
    screen = None
    render_stack = []
    clock = None

    def __init__(self):
        # scenes are automatically added to the render stack when initialized. 
        # need to call super().__init__()
        self.render_stack.append(self)

    def clearScene(self):
        # clear scenes so that render stack begins with next return.
        # useful for sections of game that don't depend on prev scene
        self.render_stack = []

    def replacePrevScene(self):
        # pop top of render stack so that next scene can replace it. 
        # useful for transitions
        self.render_stack.pop()

    def drawPrevScene(self):
        '''renders previous scene in the stack. helpful for menus that need to overlay'''
        self.render_stack[-2].draw()

    def getPrevScene(self):
        '''returns previous scene in the render stack'''
        return self.render_stack[-2]

    def returnToPrev(self):
        self.render_stack.pop()
        return self.render_stack[-1]

    def handle(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass

class MainMenu(Scene):
    def __init__(self):
        super().__init__()

        # set main menu resolution
        self.WIDTH = 720
        self.HEIGHT = 480
        Scene.screen = pygame.display.set_mode((720, 480))
        pygame.display.set_caption('Minecraftsweeper')
        pygame.display.set_icon(pygame.image.load('resources/graphics/global/minecraftsweeper.png'))

        # load background
        self.bg = pygame.image.load('resources/graphics/main_menu/menu_background.png').convert()
        self.bg_rect = self.bg.get_rect(topleft = (0,0))

        self.init_buttons()

    def init_buttons(self):
        button_texts = ['Easy',
                        'Normal',
                        'Hard',
                        'Custom']

        self.button = pygame.image.load('resources/graphics/global/menu_button_unselected.png').convert()
        self.button_rect = self.button.get_rect(midtop = (self.WIDTH // 2, 200))

        self.button_selected = pygame.image.load('resources/graphics/global/menu_button_selected.png').convert()

        # list of four required buttons and their rects
        self.buttons = [[self.button.copy(), self.button_rect.copy()] for i in range(len(button_texts))]

        # space the buttons
        for i, button in enumerate(self.buttons):
            button[1].top += 60 * i

        # load font
        font = pygame.font.Font('resources/fonts/MinecraftBold-nMK1.otf', 24)

        # create text renders
        button_texts_surfs = [font.render(text, False, 'white') for text in button_texts]
        button_texts_rects = [surf.get_rect() for surf in button_texts_surfs]

        # center text to according button rects
        for i, rect in enumerate(button_texts_rects):
            rect.center = self.buttons[i][1].center
            rect.centery -= 2 # needed to offset a little

        self.button_texts = list(zip(button_texts_surfs, button_texts_rects))

        # button dictionary where key is its text / for easy object lookup
        self.button_dict = {}
        for i, text in enumerate(button_texts):
            self.button_dict[text] = self.buttons[i]

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                xy = pygame.mouse.get_pos()
                if self.buttons[0][1].collidepoint(xy):
                    self.clearScene()
                    return Game(10, 10, 10)
                if self.buttons[1][1].collidepoint(xy):
                    self.clearScene()
                    return Game(16, 16, 40)
                if self.buttons[2][1].collidepoint(xy):
                    self.clearScene()
                    return Game(30, 16, 99)
                if self.buttons[3][1].collidepoint(xy):
                    pass
                    # self.clearScene()
                    # return Game()

    def update(self):
        # button selection highlighting
        for button in self.buttons:
            if button[1].collidepoint(pygame.mouse.get_pos()):
                button[0] = self.button_selected.copy()
            else:
                button[0] = self.button.copy()

    def draw(self):
        Scene.screen.blit(self.bg, self.bg_rect)
        Scene.screen.blits(blit_sequence = self.buttons)
        Scene.screen.blits(blit_sequence = self.button_texts)

class CustomGame(MainMenu):
    pass

class Game(Scene):
    def __init__(self, dim_x = 10, dim_y = 10, num_mines = 10):
        super().__init__()

        self.dim_x = dim_x
        self.dim_y = dim_y
        self.num_mines = num_mines
        self.ppg = 30 # pixels per (tile) grid
        self.top_border_px = 120
        self.vertical_border_px = 30
        self.bottom_border_px = 60

        self.HEIGHT = self.ppg * self.dim_y + self.bottom_border_px + self.top_border_px
        self.WIDTH = self.ppg * self.dim_x + self.ppg * 2

        self.game_running = False
        self.in_game_time = 0
        self.play_music = True

        # pygame settings
        Scene.screen = pygame.display.set_mode(size = (self.WIDTH, self.HEIGHT))
        pygame.time.set_timer(pygame.USEREVENT + 0, 1000)

        # initialize background and sprite elements
        self.init_bg()
        self.init_sprites()
        self.font = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 24)

        # initialize game
        self.game = Minesweeper(dim_x, dim_y, num_mines)

    def init_bg(self):
        # borders
        top_border = pygame.image.load('resources/graphics/game/top_border.png').convert()
        bottom_border = pygame.image.load('resources/graphics/game/bottom_border.png').convert()
        vertical_border = pygame.image.load('resources/graphics/game/vertical_border.png').convert()

        top_border_rect = top_border.get_rect()
        bottom_border_rect = bottom_border.get_rect()
        left_border_rect = vertical_border.get_rect()
        right_border_rect = vertical_border.get_rect()

        top_border_rect.topleft = (0, 0)
        bottom_border_rect.bottom = self.HEIGHT
        left_border_rect.topleft = (0, 0)
        left_border_rect.topright = (self.WIDTH, 0)

        # title
        title_text = pygame.image.load('resources/graphics/game/title.png').convert_alpha()
        title_text_rect = title_text.get_rect()
        title_text_rect.midtop = (self.WIDTH//2, self.top_border_px - 100)

        info_bar = pygame.image.load('resources/graphics/game/info_bar.png').convert_alpha()
        info_bar_rect = info_bar.get_rect()
        info_bar_rect.center = (self.WIDTH//2, self.HEIGHT - self.ppg)

        menu_icon = pygame.image.load('resources/graphics/game/menu_icon.png').convert_alpha()
        disc = pygame.image.load('resources/graphics/game/disc.png').convert_alpha()

        # save infobar rects to class so later we can handle collisions
        self.menu_icon_rect = menu_icon.get_rect()
        self.disc_rect = disc.get_rect() 

        self.menu_icon_rect.midbottom = info_bar_rect.midbottom
        self.menu_icon_rect.bottom -= 5
        self.menu_icon_rect.right += 139

        self.disc_rect.midbottom = info_bar_rect.midbottom
        self.disc_rect.bottom -= 5
        self.disc_rect.right += 99

        self.bg = [(bottom_border, bottom_border_rect),
                    (vertical_border, left_border_rect),
                    (vertical_border, right_border_rect),
                    (top_border, top_border_rect),
                    (title_text, title_text_rect),
                    (info_bar, info_bar_rect),
                    (menu_icon, self.menu_icon_rect),
                    (disc, self.disc_rect)]

    def init_sprites(self):
        mine = pygame.image.load('resources/graphics/game/mine.png').convert_alpha()
        tile = pygame.image.load('resources/graphics/game/tile.png').convert()
        flag = pygame.image.load('resources/graphics/game/flag.png').convert_alpha()

        mine = pygame.transform.scale(mine, (self.ppg, self.ppg))
        tile = pygame.transform.scale(tile, (self.ppg, self.ppg))
        flag = pygame.transform.scale(flag, (self.ppg, self.ppg))

        self.mine_rect = pygame.Surface.get_rect(mine)
        self.tile_rect = pygame.Surface.get_rect(tile)
        self.flag_rect = pygame.Surface.get_rect(flag)

        self.mine = mine
        self.tile = tile
        self.flag = flag

        self.no_music = pygame.image.load('resources/graphics/game/no_music.png').convert_alpha()
        self.no_music_rect = self.no_music.get_rect()
        self.no_music_rect.center = self.disc_rect.center

    def handle(self, event):
        if event.type == pygame.USEREVENT + 0 and self.game_running:
            self.in_game_time += 1

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # left click interactions
            mouse_pos = event.pos

            # tile collision
            for xy in self.game.getTilesXY():
                # temporarily sets tile rect to existing tile
                self.tile_rect.topleft = self.getPXY(xy)

                if self.tile_rect.collidepoint(mouse_pos) and xy not in self.game.getFlagsXY():
                    while xy in self.game.getMinesXY() and not self.game_running: # new board if first move is a mine
                        self.game = Minesweeper(self.dim_x, self.dim_y, self.num_mines)
                    self.game_running = True
                    x,y = xy
                    self.game.removeAdjacentTiles(x, y) # removes blank spaces
                    try: # removes single tile that covers a number square
                        self.game.removeTile(x, y) 
                    except ValueError:
                        pass

            # music toggle
            if self.disc_rect.collidepoint(mouse_pos):
                if self.play_music:
                    self.play_music = False
                else:
                    self.play_music = True

            # in-game menu
            if self.menu_icon_rect.collidepoint(mouse_pos):
                return Game_menu()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # right click interactions
            mouse_pos = event.pos

            # flag placement
            for xy in self.game.getTilesXY():
                self.tile_rect.topleft = self.getPXY(xy)

                if self.tile_rect.collidepoint(mouse_pos) and self.game_running:
                    x,y = xy
                    if xy in self.game.getFlagsXY():
                        self.game.removeFlag(x, y)
                    else:
                        self.game.addFlag(x, y)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return Game_menu()

    def update(self):
        if self.game.isWin():
            return Game_isWin()
        if self.game.isLoss():
            return Game_isLoss_transition()

    def draw(self):
        self.screen.fill(pygame.Color(50,50,50))
        self.screen.blits(self.bg)

        if not self.play_music:
            self.screen.blit(self.no_music, self.no_music_rect)

        # draws number of mines in adjacent cells
        for i, row in enumerate(self.game.getNeighbors_field()):
            for j, val in enumerate(row):
                if val == 0:
                    continue

                neighbor_text = self.font.render(str(val), False, 'white')

                xy = (j, i)
                xy = self.getPXY(xy) # convert grid coordinates to pixel
                x, y = xy

                font_rect = neighbor_text.get_rect()
                font_rect.center = x + self.ppg//2, y + self.ppg//2

                self.screen.blit(neighbor_text, font_rect)

        # draws corresponding game elements
        for xy in self.game.getMinesXY():
            self.mine_rect.topleft = self.getPXY(xy)
            self.screen.blit(self.mine, self.mine_rect)

        for xy in self.game.getTilesXY():
            self.tile_rect.topleft = self.getPXY(xy)
            self.screen.blit(self.tile, self.tile_rect)

        for xy in self.game.getFlagsXY():
            if xy not in self.game.getTilesXY():
                continue
            self.flag_rect.topleft = self.getPXY(xy)
            self.screen.blit(self.flag, self.flag_rect)

        self.render_info_bar_texts()
        self.screen.blits(self.info_texts)

    # draw() helper functions
    def getPXY(self, coordinates: tuple):
        '''draw helper function to convert from minesweeper grid to pixel coordinates'''
        x, y = coordinates
        x = x * self.ppg + self.vertical_border_px
        y = y * self.ppg + self.top_border_px

        return (x, y)
    
    def render_info_bar_texts(self):
        texts_to_render = [self.game.getFlagsRemaining(),
                            self.game.getEmptyTiles(),
                            self.game.getMines(),
                            self.in_game_time]

        rendered_texts = []
        for text in texts_to_render:
            render = self.font.render(str(text), False, 'white')
            rendered_texts.append(render)

        rendered_texts = list(map(lambda text: pygame.transform.rotozoom(text, 0, 0.8),
                                 rendered_texts))

        rendered_texts_rects = [text.get_rect() for text in rendered_texts]

        x, y = self.bg[5][1].midbottom # get position of info_bar from bg group

        # set position of elements
        rendered_texts_rects[0].bottomright = (x - 35 * 2 - 12.5, y - 3)
        rendered_texts_rects[1].bottomright = (x - 35 * 1 - 7.5, y - 3)
        rendered_texts_rects[2].bottomright = (x - 35 * 0 - 2.5, y - 3)
        rendered_texts_rects[3].bottomright = (x - 35 * -1 + 2.5, y - 3)

        self.info_texts = list(zip(rendered_texts, rendered_texts_rects))

class Game_menu(Scene):
    def __init__(self):
        super().__init__()

        self.WIDTH = self.getPrevScene().WIDTH
        self.HEIGHT = self.getPrevScene().HEIGHT

        self.init_bg()
        self.init_buttons()

    def init_bg(self):
        self.bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.bg.fill('black')
        self.bg.set_alpha(75) # transparency

        self.font_small = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 16)
        self.font_large = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 32)

        self.death_text = self.font_large.render('Game Paused', False, 'white')
        self.death_text_rect = self.death_text.get_rect()

        time_elapsed = self.getPrevScene().in_game_time
        self.score_text = self.font_small.render(f'Time: {time_elapsed}', False, 'white')
        self.score_text_rect = self.score_text.get_rect()

    def init_buttons(self):
        button_texts = ['Resume',
                        'New Game',
                        'Title Screen']

        # load and scale button according to window width
        self.button = pygame.image.load('resources/graphics/global/menu_button_unselected.png').convert()
        vertical_border_px = self.getPrevScene().vertical_border_px
        button_width = min(400, self.WIDTH - 2 * vertical_border_px)
        self.button = pygame.transform.smoothscale(self.button, (button_width, 47))
        self.button_rect = self.button.get_rect(midtop = (self.WIDTH // 2, 200))

        self.button_selected = pygame.image.load('resources/graphics/global/menu_button_selected.png').convert()
        self.button_selected = pygame.transform.smoothscale(self.button_selected, (button_width, 47))

        # list of buttons and their rects
        self.buttons = [[self.button.copy(), self.button_rect.copy()] for i in range(len(button_texts))]

        # load font
        font = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 24)

        # space the buttons
        for i, button in enumerate(self.buttons):
            button[1].top += 60 * i

        # create text renders
        button_texts_surfs = [font.render(text, False, 'white') for text in button_texts]
        button_texts_rects = [surf.get_rect() for surf in button_texts_surfs]

        # center text to according button rects
        for i, rect in enumerate(button_texts_rects):
            rect.center = self.buttons[i][1].center
            rect.centery -= 2 # needed to offset a little

        self.button_texts = list(zip(button_texts_surfs, button_texts_rects))

        # button dictionary where key is its text / for easy object lookup
        self.button_dict = {}
        for i, text in enumerate(button_texts):
            self.button_dict[text] = self.buttons[i]

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                xy = pygame.mouse.get_pos()
                if self.buttons[0][1].collidepoint(xy):
                    return self.returnToPrev()

                if self.buttons[1][1].collidepoint(xy):
                    # get parameters of previous game
                    dim_x = self.getPrevScene().dim_x
                    dim_y = self.getPrevScene().dim_y
                    num_mines = self.getPrevScene().num_mines

                    self.clearScene()
                    return Game(dim_x, dim_y, num_mines)

                if self.buttons[2][1].collidepoint(xy):
                    self.clearScene()
                    return MainMenu()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return self.returnToPrev()

    def update(self):
        # button selection highlighting
        for button in self.buttons:
            if button[1].collidepoint(pygame.mouse.get_pos()):
                button[0] = self.button_selected.copy()
            else:
                button[0] = self.button.copy()

    def draw(self):
        self.drawPrevScene()
        self.screen.blit(self.bg, (0,0))

        # position text
        self.death_text_rect.midtop = (self.WIDTH//2, 85)
        self.score_text_rect.midtop = (self.WIDTH//2, 125)
        self.screen.blit(self.death_text, self.death_text_rect)
        self.screen.blit(self.score_text, self.score_text_rect)

        self.screen.blits(blit_sequence = self.buttons)
        self.screen.blits(blit_sequence = self.button_texts)

class Game_isWin(Scene):
    def __init__(self):
        super().__init__()

        self.WIDTH = self.getPrevScene().WIDTH
        self.HEIGHT = self.getPrevScene().HEIGHT

        self.init_bg()
        self.init_buttons()

    def init_bg(self):
        self.bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.bg.fill('black')
        self.bg.set_alpha(75) # transparency

        self.font_small = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 16)
        self.font_large = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 32)

        self.death_text = self.font_large.render('You Won!', False, 'white')
        self.death_text_rect = self.death_text.get_rect()

        time_elapsed = self.getPrevScene().in_game_time
        self.score_text = self.font_small.render(f'Time: {time_elapsed}', False, 'white')
        self.score_text_rect = self.score_text.get_rect()

    def init_buttons(self):
        button_texts = ['New Game',
                        'Title Screen']

        # load and scale button according to window width
        self.button = pygame.image.load('resources/graphics/global/menu_button_unselected.png').convert()
        vertical_border_px = self.getPrevScene().vertical_border_px
        button_width = min(400, self.WIDTH - 2 * vertical_border_px)
        self.button = pygame.transform.smoothscale(self.button, (button_width, 47))
        self.button_rect = self.button.get_rect(midtop = (self.WIDTH // 2, 200))

        self.button_selected = pygame.image.load('resources/graphics/global/menu_button_selected.png').convert()
        self.button_selected = pygame.transform.smoothscale(self.button_selected, (button_width, 47))

        # list of buttons and their rects
        self.buttons = [[self.button.copy(), self.button_rect.copy()] for i in range(len(button_texts))]

        # load font
        font = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 24)

        # space the buttons
        for i, button in enumerate(self.buttons):
            button[1].top += 60 * i

        # create text renders
        button_texts_surfs = [font.render(text, False, 'white') for text in button_texts]
        button_texts_rects = [surf.get_rect() for surf in button_texts_surfs]

        # center text to according button rects
        for i, rect in enumerate(button_texts_rects):
            rect.center = self.buttons[i][1].center
            rect.centery -= 2 # needed to offset a little

        self.button_texts = list(zip(button_texts_surfs, button_texts_rects))

        # button dictionary where key is its text / for easy object lookup
        self.button_dict = {}
        for i, text in enumerate(button_texts):
            self.button_dict[text] = self.buttons[i]

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                xy = pygame.mouse.get_pos()
                if self.buttons[0][1].collidepoint(xy):
                    # get parameters of previous game
                    dim_x = self.getPrevScene().dim_x
                    dim_y = self.getPrevScene().dim_y
                    num_mines = self.getPrevScene().num_mines

                    self.clearScene()
                    return Game(dim_x, dim_y, num_mines)

                if self.buttons[1][1].collidepoint(xy):
                    self.clearScene()
                    return MainMenu()

    def update(self):
        # button selection highlighting
        for button in self.buttons:
            if button[1].collidepoint(pygame.mouse.get_pos()):
                button[0] = self.button_selected.copy()
            else:
                button[0] = self.button.copy()

    def draw(self):
        self.drawPrevScene()
        self.screen.blit(self.bg, (0,0))

        # position text
        self.death_text_rect.midtop = (self.WIDTH//2, 85)
        self.score_text_rect.midtop = (self.WIDTH//2, 125)
        self.screen.blit(self.death_text, self.death_text_rect)
        self.screen.blit(self.score_text, self.score_text_rect)

        self.screen.blits(blit_sequence = self.buttons)
        self.screen.blits(blit_sequence = self.button_texts)

class Game_isLoss_transition(Scene):
    def __init__(self):
        super().__init__()

        self.game = self.getPrevScene().game
        self.minesXY = self.game.getMinesXY()[:]
        self.ticks = 0

        # set animation proportional to number of mines
        self.num_mines = self.game.getMines()
        self.max_tick = 1500 // self.num_mines

    def update(self):
        if not self.minesXY:
            self.replacePrevScene()
            return Game_isLoss()
            
        # timer for revealing mines
        self.ticks += self.clock.get_time()

    def draw(self):
        self.drawPrevScene()
        pygame.display.flip()

        if self.ticks > self.max_tick:
            mineXY = self.minesXY.pop()
            x,y = mineXY
            try:
                self.game.removeTile(x,y)
            except ValueError:
                pass
            self.drawPrevScene()
            pygame.display.flip()
            self.ticks = 0
            
class Game_isLoss(Scene):
    def __init__(self):
        super().__init__()

        self.WIDTH = self.getPrevScene().WIDTH
        self.HEIGHT = self.getPrevScene().HEIGHT

        self.init_bg()
        self.init_buttons()

    def init_bg(self):
        self.bg = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.bg.fill(pygame.Color(255,0,0))
        self.bg.set_alpha(75) # transparency

        self.font_small = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 16)
        self.font_large = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 32)

        self.death_text = self.font_large.render('You Died!', False, 'white')
        self.death_text_rect = self.death_text.get_rect()

        flags_correct = self.getPrevScene().game.getFlagsCorrect()
        self.score_text = self.font_small.render(f'Score: {flags_correct}', False, 'white')
        self.score_text_rect = self.score_text.get_rect()

    def init_buttons(self):
        button_texts = ['Respawn',
                        'Title Screen']

        # load and scale button according to window width
        self.button = pygame.image.load('resources/graphics/global/menu_button_unselected.png').convert()
        vertical_border_px = self.getPrevScene().vertical_border_px
        button_width = min(400, self.WIDTH - 2 * vertical_border_px)
        self.button = pygame.transform.smoothscale(self.button, (button_width, 47))
        self.button_rect = self.button.get_rect(midtop = (self.WIDTH // 2, 200))

        self.button_selected = pygame.image.load('resources/graphics/global/menu_button_selected.png').convert()
        self.button_selected = pygame.transform.smoothscale(self.button_selected, (button_width, 47))

        # list of buttons and their rects
        self.buttons = [[self.button.copy(), self.button_rect.copy()] for i in range(len(button_texts))]

        # load font
        font = pygame.font.Font('resources/fonts/MinecraftRegular-Bmg3.otf', 24)

        # space the buttons
        for i, button in enumerate(self.buttons):
            button[1].top += 60 * i

        # create text renders
        button_texts_surfs = [font.render(text, False, 'white') for text in button_texts]
        button_texts_rects = [surf.get_rect() for surf in button_texts_surfs]

        # center text to according button rects
        for i, rect in enumerate(button_texts_rects):
            rect.center = self.buttons[i][1].center
            rect.centery -= 2 # needed to offset a little

        self.button_texts = list(zip(button_texts_surfs, button_texts_rects))

        # button dictionary where key is its text / for easy object lookup
        self.button_dict = {}
        for i, text in enumerate(button_texts):
            self.button_dict[text] = self.buttons[i]

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                xy = pygame.mouse.get_pos()
                if self.buttons[0][1].collidepoint(xy):
                    # get parameters of previous game
                    dim_x = self.getPrevScene().dim_x
                    dim_y = self.getPrevScene().dim_y
                    num_mines = self.getPrevScene().num_mines

                    self.clearScene()
                    return Game(dim_x, dim_y, num_mines)

                if self.buttons[1][1].collidepoint(xy):
                    self.clearScene()
                    return MainMenu()

    def update(self):
        # button selection highlighting
        for button in self.buttons:
            if button[1].collidepoint(pygame.mouse.get_pos()):
                button[0] = self.button_selected.copy()
            else:
                button[0] = self.button.copy()

    def draw(self):
        self.drawPrevScene()
        self.screen.blit(self.bg, (0,0))

        # position text
        self.death_text_rect.midtop = (self.WIDTH//2, 85)
        self.score_text_rect.midtop = (self.WIDTH//2, 125)
        self.screen.blit(self.death_text, self.death_text_rect)
        self.screen.blit(self.score_text, self.score_text_rect)

        self.screen.blits(blit_sequence = self.buttons)
        self.screen.blits(blit_sequence = self.button_texts)

def main():
    pygame.init()
    Scene.clock = pygame.time.Clock()
    scene = MainMenu()

    while True:
        if pygame.event.get(pygame.QUIT):
            pygame.quit()
            quit()
        for event in pygame.event.get():
            scene = scene.handle(event) or scene
        scene = scene.update() or scene
        scene.draw()
        pygame.display.flip()
        scene.clock.tick(60)

if __name__ == '__main__':
    main()