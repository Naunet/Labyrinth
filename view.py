import pygame
from pygame.locals import *
from os import path


class View:
    def __init__(self):
        # values
        self.GRID_WIDTH = None
        self.GRID_HEIGHT = None
        self.SIZE = None
        self.RES_X = 510  # check against device
        self.RES_Y = 610
        self.HEADER = 50
        self.BORDER_X = None
        self.BORDER_Y = None
        self.C_WALL = (0, 153, 0, 255)
        self.C_PATH = (250, 210, 140, 255)
        # functions
        pygame.display.init()
        pygame.font.init()
        self.display = pygame.display.set_mode(
            (self.RES_X, self.RES_Y), HWSURFACE | DOUBLEBUF | RESIZABLE)
        pygame.display.set_caption("Moving labyrinth")
        self.fonts = dict()
        self.fonts['standard'] = pygame.font.Font(
            pygame.font.get_default_font(), 32)
        self.fonts['large'] = pygame.font.Font(
            pygame.font.get_default_font(), 54)
        self.images = dict()
        self.load()

    def set_dimensions(self, width, height):
        self.GRID_WIDTH = width
        self.GRID_HEIGHT = height
        self._recalculate()

    def _recalculate(self):
        if self.GRID_WIDTH and self.GRID_HEIGHT:
            self.SIZE = min(self.RES_X//self.GRID_WIDTH,
                            (self.RES_Y-self.HEADER)//self.GRID_HEIGHT)
            self.BORDER_X = (self.RES_X-self.SIZE*self.GRID_WIDTH)//2
            self.BORDER_Y = self.HEADER + \
                (self.RES_Y-self.SIZE*self.GRID_HEIGHT-self.HEADER)//2

    def resize(self, width, height):
        self.RES_X = max(410, width)
        self.RES_Y = max(615, height)
        self.display = pygame.display.set_mode(
            (self.RES_X, self.RES_Y), HWSURFACE | DOUBLEBUF | RESIZABLE)
        self._recalculate()

    def _top_corner(self, x, y):
        """coordinates to pixels"""
        x = self.SIZE*x+self.BORDER_X
        y = self.SIZE*y+self.BORDER_Y
        return (x, y)

    def background(self, color, level):
        self.display.fill(color)
        self.word("Level "+str(level),
                  (self.RES_X//2, self.HEADER//2))
        text = self.fonts['standard'].render(
                "< Levels", True,
                pygame.Color('white'), pygame.Color('dodgerblue'))
        textRect = text.get_rect()
        offset = (self.HEADER-textRect.height)//2
        textRect.topleft = (offset, offset)
        self.display.blit(text, textRect)
        return textRect

    def clock(self, paused, dead_time, is_level_end, end_time):
        text = self.fonts['standard'].render(
            "Pause", True, pygame.Color('black'), pygame.Color('white'))
        if is_level_end:
            time = end_time//1000
            string = "{0:02}:{1:02}".format(time//60, time % 60)
            text = self.fonts['standard'].render(
                string, True, pygame.Color('red'), pygame.Color('white'))
        if not paused:
            time = (pygame.time.get_ticks() - dead_time)//1000  # in seconds
            string = "{0:02}:{1:02}".format(time//60, time % 60)
            text = self.fonts['standard'].render(
                string, True, pygame.Color('black'), pygame.Color('white'))
        textRect = text.get_rect()
        offset = (self.HEADER-textRect.height)//2
        textRect.topright = (self.RES_X-offset, offset)
        self.display.blit(text, textRect)

    def rectangle(self, topCorner, width, height, color):
        rect = pygame.Rect(topCorner[0], topCorner[1], width, height)
        pygame.draw.rect(self.display, color, rect)
        return rect

    def maze(self, maze, size, color):
        for j in range(self.GRID_HEIGHT):
            for i in range(self.GRID_WIDTH):
                if maze[j][i]:
                    self.rectangle(self._top_corner(i, j),
                                   self.SIZE, self.SIZE, color)

    def char(self, x, y):
        # To be improved
        x, y = self._top_corner(x, y)
        scale = 0.7
        x += (1-scale)/2*self.SIZE
        y += (1-scale)/2*self.SIZE
        self.rectangle((x, y), self.SIZE*scale,
                       self.SIZE*scale, (0, 0, 0, 255))

    def header(self, level, paused, paused_time, is_level_end, end_time):
        box = self.background(self.C_PATH, level)
        self.clock(paused, paused_time, is_level_end, end_time)
        return box

    def game(self, maze, pos_x, pos_y):
        self.maze(maze, self.SIZE, self.C_WALL)
        self.char(pos_x, pos_y)

    def word(self, text, pos, color=pygame.Color('black'), background=None, font='standard'):
        word_surface = self.fonts[font].render(text, True, color, background)
        rect = word_surface.get_rect()
        rect.center = pos
        self.display.blit(word_surface, rect)
        return rect

    def text(self, surface, height, text, color=pygame.Color('black'), background=pygame.Color('white')):
        words = [word.split(' ') for word in text.splitlines()]
        max_width, _ = surface.get_size()
        space = self.fonts['standard'].size(' ')[0]  # width of a space
        while words:
            while words and not words[0]:
                words.pop(0)
            if not words:
                break
            word = words[0].pop(0)
            line = word
            text = self.fonts['standard'].render(
                word, True, color, background)
            width, middle = text.get_size()
            size = width
            while words[0]:
                word = words[0].pop(0)
                text = self.fonts['standard'].render(
                    word, True, color, background)
                width, tmp = text.get_size()
                size += space + width
                if size >= max_width:
                    words[0].insert(0, word)
                    break
                line += " " + word
                if tmp < middle:
                    tmp = middle
            height += middle//2
            rect = self.word(line, (max_width//2, height),
                             color=color, background=background)
            height += rect.height//2

    def end(self, current_level, end_time):
        # read highscores
        scorefile = open('highscores.txt', 'r+')
        scorelist = scorefile.readlines()
        scorefile.close()
        # check if level already in scores
        highscore = None
        for score in scorelist:
            level, time = score.split(': ')
            if level == str(current_level):
                highscore = int(time)//1000
        # display highscore
        string = "Level Complete!\n"
        color = pygame.Color('black')
        if end_time//1000 <= highscore:
            string += "New "
            color = pygame.Color('red')
        string += "Highscore:\n{0:02}:{1:02}s".format(
            highscore//60, highscore % 60)
        self.text(self.display, self.RES_Y//3, string, color=color)
        # display instructions
        string = "Click anywhere to continue"
        self.text(self.display, 2*self.RES_Y//3, string)

    def load(self):
        background = pygame.image.load(path.join('img', 'tree.png'))
        # 80 = header + fraction of vine
        scale = min(self.RES_X/background.get_width(),
                    (self.RES_Y-80)/background.get_height())
        background = pygame.transform.scale(background,
                                            (int(background.get_width()*scale), int(background.get_height()*scale)))
        self.images['background'] = background
        vine = pygame.image.load(path.join('img', '2.png'))
        factor = self.RES_X/vine.get_width()
        vine = pygame.transform.scale(
            vine, (self.RES_X, int(vine.get_height()*factor)))
        self.images['vine'] = vine

    def buttons(self, values, pos, background, color=pygame.Color('black')):
        # find variables
        width, height = self.fonts['standard'].size(values[0])
        for text in values:
            width = max(width, self.fonts['standard'].size(text)[0])
        width += 30
        height += 20
        x, y = pos
        left = x-width//2
        # draw buttons
        boxes = list()
        for text in values:
            box = self.rectangle((left, y-height//2),
                                 width, height, background)
            boxes.append(box)  # (left,left+size,y-height//2,y+height//2)
            self.word(text, (x, y),
                      color)
            y += 80
        return boxes  # (x1, x2, y1, y2)

    def menu(self):
        self.display.fill((255, 231, 122))  # (153, 221, 255)
        rect = self.images['background'].get_rect()
        rect.center = (self.RES_X//2, self.RES_Y//2+80//2)
        self.display.blit(self.images['background'], rect)
        self.display.blit(self.images['vine'], (0, 20))
        self.word("Labyrinth", (self.RES_X//2, 70), font='large')
        C_LEAF = (111, 133, 97)  # (44,95,45)
        boxes = self.buttons(["Level select", "Sandbox", "Settings"],
                             (self.RES_X//2, 180), C_LEAF)
        return boxes

    def levels(self):
        self.display.fill((255, 231, 122))  # (153, 221, 255)
        rect = self.images['background'].get_rect()
        rect.center = (self.RES_X//2, self.RES_Y//2+80//2)
        self.display.blit(self.images['background'], rect)
        self.display.blit(self.images['vine'], (0, 20))
        self.word("Level Select", (self.RES_X//2, 70), font='large')
        C_LEAF = (111, 133, 97)  # (44,95,45)
        boxes = self.buttons(["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
                             (self.RES_X//4, 180), C_LEAF)
        boxes += self.buttons(["Level 6", "Level 7", "Level 8", "Level 9", "Level 10"],
                              (3*self.RES_X//4, 180), C_LEAF)
        y = boxes[-1].bottom+(self.RES_Y-boxes[-1].bottom)//2
        menu = self.word("Main menu", (self.RES_X//2, y),
                         color=pygame.Color('white'),
                         background=pygame.Color('dodgerblue'))
        return [menu]+boxes
