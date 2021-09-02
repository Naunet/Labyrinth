from random import random, randrange

IS_WALL = True


class Wall:
    def __init__(self, view, width, height, exits=None, wallrate=0.45):
        self.WALL_RATE = wallrate
        self.WIDTH = width
        self.HEIGHT = height
        self.EXITS = exits
        if not self.EXITS:
            self.EXITS = [[self.WIDTH//2, 0], [self.WIDTH//2 + 1, 0],
                          [self.WIDTH - 1, self.HEIGHT//2],
                          [self.WIDTH - 1, self.HEIGHT//2 + 1],
                          [0, self.HEIGHT//2], [0, self.HEIGHT//2 + 1],
                          [self.WIDTH//2, self.HEIGHT - 1],
                          [self.WIDTH//2 + 1, self.HEIGHT - 1]]
        self.START_X = self.WIDTH//2  # centre cleared by def
        self.START_Y = self.HEIGHT//2  # centre cleared by def
        self.pos_x = self.START_X
        self.pos_y = self.START_Y
        self.view = view
        self.maze = [[IS_WALL]*self.WIDTH for i in range(self.HEIGHT)]
        for i in range(1, self.WIDTH-1):
            for j in range(1, self.HEIGHT-1):
                self.maze[j][i] = (random() < self.WALL_RATE)
        # clear exits
        for x, y in self.EXITS:
            self.maze[y][x] = not IS_WALL
        # clear start
        self.maze[self.START_Y][self.START_X] = not IS_WALL

    def handle_shift(self):
        """from anywhere in any direction"""
        # chose orientation
        columns = (random() < 0.5)  # lines or columns
        uplim = self.WIDTH-1
        if not columns:
            uplim = self.HEIGHT-1

        # values
        start = 1
        stop = randrange(1, uplim)
        positives = 1

        # chose section
        above = (random() < 0.5)  # above or left
        if not above:
            start = stop
            stop = uplim-1

        # chose direction
        downwards = (random() < 0.5)  # downwards or right
        if downwards:
            tmp = start
            start = stop
            stop = tmp
            positives = -1

        """shift"""
        for i in range(start, stop, positives):
            if columns:
                for y in range(1, self.HEIGHT-1):
                    self.maze[y][i] = self.maze[y][i+positives]
            else:
                for x in range(1, self.WIDTH-1):
                    self.maze[i][x] = self.maze[i+positives][x]

        """create new walls"""
        if columns:
            for y in range(1, self.HEIGHT-1):
                self.maze[y][stop] = (random() < self.WALL_RATE)
        else:
            for x in range(1, self.WIDTH-1):
                self.maze[stop][x] = (random() < self.WALL_RATE)

        """clear center"""
        self.maze[self.START_Y][self.START_X] = not IS_WALL

        """move character"""
        if self.maze[self.pos_y][self.pos_x] == IS_WALL:
            if columns:
                if self.maze[self.pos_y][self.pos_x-positives] == IS_WALL:
                    self.pos_x = self.START_X
                    self.pos_y = self.START_Y
                else:
                    self.pos_x -= positives
            else:
                if self.maze[self.pos_y-positives][self.pos_x] == IS_WALL:
                    self.pos_x = self.START_X
                    self.pos_y = self.START_Y
                else:
                    self.pos_y -= positives

    def move(self, anim, paused):
        if not anim['move'] or paused:
            return (self.pos_x, self.pos_y)
        if anim['right'] and self.pos_x < self.WIDTH-1 and not(self.maze[self.pos_y][self.pos_x+1]):
            self.pos_x += 1
        if anim['left'] and self.pos_x > 0 and not(self.maze[self.pos_y][self.pos_x-1]):
            self.pos_x -= 1
        if anim['up'] and self.pos_y > 0 and not(self.maze[self.pos_y-1][self.pos_x]):
            self.pos_y -= 1
        if anim['down'] and self.pos_y < self.HEIGHT-1 and not(self.maze[self.pos_y+1][self.pos_x]):
            self.pos_y += 1
        return (self.pos_x, self.pos_y)

    def is_end_game(self):
        # print((self.pos_x, self.pos_y), self.EXITS)
        if [self.pos_x, self.pos_y] in self.EXITS:
            return True
        return False

    def draw(self):
        self.view.game(self.maze, self.pos_x, self.pos_y)
