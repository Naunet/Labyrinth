import pygame


class View:
    def __init__(self, width, height):
        # values
        self.GRID_WIDTH = width
        self.GRID_HEIGHT = height
        self.RES_X = 510  # swap to dynamic
        self.RES_Y = 610  # swap to dynamic
        self.HEADER = 50
        self.SIZE = min(self.RES_X//width, (self.RES_Y-self.HEADER)//height)
        self.BORDER_X = (self.RES_X-self.SIZE*width)//2
        self.BORDER_Y = self.HEADER + \
            (self.RES_Y-self.SIZE*height-self.HEADER)//2
        self.C_WALL = (0, 153, 0, 255)
        self.C_PATH = (250, 210, 140, 255)
        # functions
        pygame.display.init()
        pygame.font.init()
        self.window = pygame.display.set_mode((self.RES_X, self.RES_Y))
        pygame.display.set_caption("Moving labyrinth")
        self.font = pygame.font.Font(pygame.font.get_default_font(), 32)


    def _top_corner(self, x, y):
        """coordinates to pixels"""
        x = self.SIZE*x+self.BORDER_X
        y = self.SIZE*y+self.BORDER_Y
        return (x, y)


    def background(self, color, level):
        self.window.fill(color)
        self.word("Level "+str(level),
                       (self.RES_X//2, self.HEADER//2),
                       pygame.Color('black'))


    def clock(self, paused, paused_time, is_level_end, end_time):
        text = self.font.render("Pause", True, (0, 0, 0), (255, 255, 255))
        if is_level_end:
            time = end_time//1000
            string = "{0:02}:{1:02}".format(time//60, time % 60)
            text = self.font.render(string, True, (255, 0, 0), (255, 255, 255))
        if not paused:
            time = (pygame.time.get_ticks() - paused_time)//1000  # in seconds
            string = "{0:02}:{1:02}".format(time//60, time % 60)
            text = self.font.render(string, True, (0, 0, 0), (255, 255, 255))
        textRect = text.get_rect()
        offset = (self.HEADER-textRect.height)//2
        textRect.topright = (self.RES_X-offset, offset)
        self.window.blit(text, textRect)


    def rectangle(self, topCorner, width, height, color):
        Rect = pygame.Rect(topCorner[0], topCorner[1], width, height)
        pygame.draw.rect(self.window, color, Rect)


    def maze(self, maze, size, color):
        for j in range(self.GRID_HEIGHT):
            for i in range(self.GRID_WIDTH):
                if maze[j][i]:
                    self.rectangle(self._top_corner(i, j), 25, 25, color)


    def char(self, x, y):
        # To be improved
        x, y = self._top_corner(x, y)
        scale = 0.7
        x += (1-scale)/2*self.SIZE
        y += (1-scale)/2*self.SIZE
        self.rectangle((x, y), self.SIZE*scale,
                            self.SIZE*scale, (0, 0, 0, 255))


    def header(self, level, paused, paused_time, is_level_end, end_time):
        self.background(self.C_PATH, level)
        self.clock(paused, paused_time, is_level_end, end_time)


    def game(self, maze, pos_x, pos_y):
        self.maze(maze, self.SIZE, self.C_WALL)
        self.char(pos_x, pos_y)


    def word(self, text, pos, color, background=None):
        word_surface = self.font.render(text, True, color, background)
        rect = word_surface.get_rect()
        rect.center = pos
        self.window.blit(word_surface, rect)
        return rect.width, rect.height


    def text(self, surface, height, text):
        words = [word.split(' ') for word in text.splitlines()]
        max_width, _ = surface.get_size()
        space = self.font.size(' ')[0]  # width of a space
        while words:
            while words and not words[0]:
                words.pop(0)
            if not words:
                break
            line = ""
            size = 0
            word = words[0].pop(0)
            text = self.font.render(word, True, (0, 0, 0), (255, 255, 255))
            width, tmp = text.get_size()
            middle = tmp
            while size + space + width < max_width:
                line += " " + word
                size += space + width
                if not words[0]:
                    break
                word = words[0].pop()
                text = self.font.render(word, True, (0, 0, 0), (255, 255, 255))
                width, tmp = text.get_size()
                if tmp < middle:
                    tmp = middle
            height += middle//2
            _, tmp = self.word(line, (max_width//2, height),
                                    pygame.Color('black'), pygame.Color('white'))
            height += tmp//2


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
        if end_time//1000 <= highscore:
            string += "New "
        string += "Highscore:\n{0:02}:{1:02}s".format(highscore//60, highscore % 60)
        self.text(self.window, self.RES_Y//3, string)
