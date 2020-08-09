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

    def initialize(self):
        self.key_flags = list()
        self.current_level = 1
        self.width = 20
        self.height = 22
        self.draw.set_dimensions(self.width, self.height)
        self.maze = wall.Wall(self.draw, self.width, self.height)
        if self.width < 5 or self.height < 5:
            raise Exception("Maze dimensions too small! \
                ({}, {})".format(self.width, self.height))
        self.timer = 1000
        pygame.time.set_timer(self.LOOP_SHIFT, self.timer)  # loop for shift
        self.level_end = False
        self.paused = False
        self.paused_time = 0
        self.pause_start = None
        self.start_time = pygame.time.get_ticks()
        self.end_time = None
        pygame.time.set_timer(self.LOOP_CLOCK, 500)  # update clock

    def setup(self):
        self.draw = view.View()
        self.close_game = False

    def run(self):
        while not self.close_game:
            for event in [pygame.event.wait()] + pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_game = True     
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        self.close_game = True
                if self.screen == Screen.GAME:
                    self.play(event)
                if self.screen == Screen.LEVELS:
                    self.level_select(event)
                if self.screen == Screen.MENU:
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
            print(clicked)
            self.current_level = clicked[0]+1
            if clicked:
                self.screen = Screen.GAME
                self.initialize()

    def play(self, event):
        if event.type == self.LOOP_SHIFT:
            self.maze.handle_shift()
        if event.type == pygame.KEYDOWN:
            self.key_flags.append(event.key)
            pygame.time.set_timer(self.LOOP_KEY, 200)  # hold down loop
        if event.type == pygame.KEYDOWN or event.type == self.LOOP_KEY:
            for key in self.key_flags:
                anim = self.handle_interaction(key)
                self.close_game = anim['quit']
                self.paused = self.pause_game(self.paused, anim['pause'])
                self.maze.move(anim, self.paused)
        if event.type == pygame.KEYUP:
            self.key_flags.remove(event.key)
            if not self.key_flags:
                pygame.time.set_timer(self.LOOP_KEY, 0)

        self.draw.header(self.current_level, self.paused,
                         self.start_time + self.paused_time, 
                         self.level_end, self.end_time)
        self.maze.draw()

        if self.maze.is_end_game():
            if not self.level_end:
                self.end_time = pygame.time.get_ticks()-self.paused_time-self.start_time
                self.level_end = True
                self.paused = True
                pygame.time.set_timer(self.LOOP_SHIFT, 0)
                score.save(self.current_level, self.end_time)
            self.draw.end(self.current_level, self.end_time)
            
            # click anywhere to continue
            if event.type == pygame.MOUSEBUTTONUP:
                self.initialize()
                self.setup()
                self.screen = Screen.LEVELS

    def handle_interaction(self, key):
        """records player's interaction"""
        anim = {'move': False, 'right': False, 'left': False,
                'up': False, 'down': False, 'quit': False, 'pause': False}
        if key == pygame.K_RIGHT:
            anim['move'] = True
            anim['right'] = True
        if key == pygame.K_LEFT:
            anim['move'] = True
            anim['left'] = True
        if key == pygame.K_UP:
            anim['move'] = True
            anim['up'] = True
        if key == pygame.K_DOWN:
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
