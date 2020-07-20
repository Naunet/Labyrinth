# libraries
import pygame
from pygame.constants import *
import time
from enum import Enum
# local
import view
import wall
import score


def handle_interaction(key):
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


def pause_game(old, change):
    global pause_start, paused_time
    if not old and change:
        pygame.time.set_timer(LOOP_SHIFT, 0)
        pause_start = pygame.time.get_ticks()
        return True
    if old and change:
        pygame.time.set_timer(LOOP_SHIFT, TIMER)
        paused_time += pygame.time.get_ticks() - pause_start
        pause_start = None
        return False
    return old


def run():
    global close_game, paused, level_end, end_time
    if event.type == LOOP_SHIFT:
        maze.handle_shift()
    if event.type == pygame.KEYDOWN:
        key_flags.append(event.key)
        pygame.time.set_timer(LOOP_KEY, 200)  # hold down loop
    if event.type == pygame.KEYDOWN or event.type == LOOP_KEY:
        for key in key_flags:
            anim = handle_interaction(key)
            close_game = anim['quit']
            paused = pause_game(paused, anim['pause'])
            maze.move(anim, paused)
    if event.type == pygame.KEYUP:
        key_flags.remove(event.key)
        if not key_flags:
            pygame.time.set_timer(LOOP_KEY, 0)

    draw.header(current_level, paused, paused_time, level_end, end_time)
    maze.draw()

    if maze.is_end_game():
        if not level_end:
            end_time = pygame.time.get_ticks()-paused_time
            level_end = True
            paused = True
            pygame.time.set_timer(LOOP_SHIFT, 0)
            score.save(current_level, end_time)
        draw.end(current_level, end_time)


# define macro variables
GRID_WIDTH = 20
GRID_HEIGHT = 22
if GRID_WIDTH < 5 or GRID_HEIGHT < 5:
    raise Exception("Maze dimensions too small! \
        ({}, {})".format(GRID_WIDTH, GRID_HEIGHT))
TIMER = 1000
LOOP_KEY = USEREVENT+2
LOOP_SHIFT = USEREVENT+1

# define global variables
key_flags = list()
current_level = 1
level_end = False
paused = False
paused_time = 0
pause_start = None
end_time = None

# setup
pygame.time.set_timer(LOOP_SHIFT, TIMER)  # loop for shift
draw = view.View(GRID_WIDTH, GRID_HEIGHT)
maze = wall.Wall(draw, GRID_WIDTH, GRID_HEIGHT)

# screen flag


class Screen(Enum):
    MENU = 1
    SETTINGS = 2
    LEVELS = 3
    GAME = 4
    SANDBOX = 5


screen = Screen.MENU

# program
close_game = False
while not close_game:
    for event in [pygame.event.wait()] + pygame.event.get():
        if event.type == pygame.QUIT:
            close_game = True
        if screen == Screen.MENU:
            boxes = draw.menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = [index for index,
                           b in enumerate(boxes) if b.collidepoint(pos)]
                print(clicked)
                if clicked:
                    if clicked[0] == 0:
                        screen = Screen.GAME  # LEVELS
                    if clicked[0] == 1:
                        screen = Screen.SANDBOX
                    if clicked[0] == 2:
                        screen = Screen.SETTINGS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    close_game = True
        if screen == Screen.GAME:
            run()
        pygame.display.update()
quit()
