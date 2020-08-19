# libraries
import pygame
from pygame.constants import *
import time
from enum import Enum
# local
import view
import wall
import score

# screen flag


class Screen(Enum):
    MENU = 1
    SETTINGS = 2
    LEVELS = 3
    GAME = 4
    SANDBOX = 5


class Game():
    def __init__(self):
        self.LOOP_SHIFT = USEREVENT+1
        self.LOOP_KEY = USEREVENT+2
        self.LOOP_CLOCK = USEREVENT+3

        self.screen = Screen.MENU
        self.setup()
        self.run()

    def initialize(self, level=1, size=(20, 22), shift_time=1000):
        self.key_flags = list()
        self.current_level = level
        self.width, self.height = size
        self.draw.set_dimensions(self.width, self.height)
        if self.width < 5 or self.height < 5:
            raise Exception("Maze dimensions too small! \
                ({}, {})".format(self.width, self.height))
        self.maze = wall.Wall(self.draw, self.width, self.height)
        self.timer = shift_time
        pygame.time.set_timer(self.LOOP_SHIFT, self.timer)  # loop for shift
        self.level_end = False
        self.paused = False
        self.paused_time = 0
        self.pause_start = None
        self.start_time = pygame.time.get_ticks()
        self.end_time = None
        pygame.time.set_timer(self.LOOP_CLOCK, 500)  # update clock

    def setup(self):
        self.read_levels()
        self.draw = view.View()
        self.close_game = False

    def run(self):
        while not self.close_game:
            for event in [pygame.event.wait()] + pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_game = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        self.close_game = True
                elif event.type == pygame.VIDEORESIZE:
                    self.draw.resize(*event.dict['size'])

                if self.screen == Screen.GAME:
                    self.play(event)
                elif self.screen == Screen.LEVELS:
                    self.level_select(event)
                elif self.screen == Screen.MENU:
                    self.menu_select(event)
                pygame.display.update()
        quit()

    def menu_select(self, event):
        boxes = self.draw.menu()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            clicked = [index for index,
                       b in enumerate(boxes) if b.collidepoint(pos)]
            if clicked:
                if clicked[0] == 0:
                    self.screen = Screen.LEVELS
                if clicked[0] == 1:
                    self.screen = Screen.SANDBOX
                if clicked[0] == 2:
                    self.screen = Screen.SETTINGS

    def level_select(self, event):
        boxes = self.draw.levels()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            clicked = [index for index,
                       b in enumerate(boxes) if b.collidepoint(pos)]
            if clicked:
                if clicked[0] == 0:
                    self.screen = Screen.MENU
                else:
                    self.setup_level(clicked[0])
                    self.screen = Screen.GAME

    def setup_level(self, level):
        params = self.levels.get(level)
        if not params:
            self.initialize(level=level)
        else:
            self.initialize(level=level, size=(
                params['width'], params['height']), shift_time=params['timer'])
            # , wallrate=params.get('wallrate'), exits=params.get('exits')

    def read_levels(self):
        # read levels
        levelfile = open('levels.txt', 'r+')
        lines = levelfile.readlines()
        levelfile.close()
        # creat dictionary
        self.levels = dict()
        while lines:
            while lines[0] == '\n':
                lines.pop(0)
            number = int(lines.pop(0))
            timer = int(lines.pop(0))
            width = int(lines.pop(0))
            height = int(lines.pop(0))
            level = dict(timer=timer, width=width, height=height)
            tmp = lines.pop(0)
            if tmp != '\n':
                level["wallrate"] = float(tmp)
                tmp = lines.pop(0)
            if tmp != '\n':
                exits = eval(tmp)
                level["exits"] = exits
            self.levels[number] = level

    def play(self, event):
        back = self.draw.header(self.current_level, self.paused,
                                self.start_time + self.paused_time,
                                self.level_end, self.end_time)
        self.maze.draw()

        if event.type == self.LOOP_SHIFT:
            self.maze.handle_shift()
        elif event.type == pygame.KEYDOWN:
            self.key_flags.append(event.key)
            pygame.time.set_timer(self.LOOP_KEY, 200)  # hold down loop
        if event.type == pygame.KEYDOWN or event.type == self.LOOP_KEY:
            for key in self.key_flags:
                anim = self.handle_interaction(key)
                self.close_game = anim['quit']
                self.paused = self.pause_game(self.paused, anim['pause'])
                self.maze.move(anim, self.paused)
        elif event.type == pygame.KEYUP:
            self.key_flags.remove(event.key)
            if not self.key_flags:
                pygame.time.set_timer(self.LOOP_KEY, 0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if back.collidepoint(pos):
                self.screen = Screen.LEVELS

        if self.maze.is_end_game():
            if not self.level_end:
                self.end_time = pygame.time.get_ticks()-self.paused_time-self.start_time
                self.level_end = True
                self.paused = True
                pygame.time.set_timer(self.LOOP_SHIFT, 0)
                score.save(self.current_level, self.end_time)
            self.draw.end(self.current_level, self.end_time)

            next = False
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    next = True
            if event.type == pygame.MOUSEBUTTONUP:
                next = True
            if next:
                self.current_level += 1
                self.setup_level(self.current_level)

    def handle_interaction(self, key):
        """records player's interaction"""
        anim = {'move': False, 'right': False, 'left': False,
                'up': False, 'down': False, 'quit': False, 'pause': False}
        if key in [pygame.K_RIGHT, pygame.K_d, pygame.K_KP6]:
            anim['move'] = True
            anim['right'] = True
        if key in [pygame.K_LEFT, pygame.K_a, pygame.K_KP4]:
            anim['move'] = True
            anim['left'] = True
        if key in [pygame.K_UP, pygame.K_w, pygame.K_KP8]:
            anim['move'] = True
            anim['up'] = True
        if key in [pygame.K_DOWN, pygame.K_s, pygame.K_KP2]:
            anim['move'] = True
            anim['down'] = True
        if key == pygame.K_q or key == pygame.K_ESCAPE:
            anim['quit'] = True
        if key == pygame.K_SPACE or key == pygame.K_PAUSE:
            anim['pause'] = True
        return anim

    def pause_game(self, old, change):
        if not old and change:
            pygame.time.set_timer(self.LOOP_SHIFT, 0)
            self.pause_start = pygame.time.get_ticks()
            return True
        if old and change:
            pygame.time.set_timer(self.LOOP_SHIFT, self.timer)
            self.paused_time += pygame.time.get_ticks() - self.pause_start
            self.pause_start = None
            return False
        return old


Game()
