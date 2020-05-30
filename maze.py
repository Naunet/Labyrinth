import pygame
from pygame.locals import *
from random import random, randrange
import time
import view


def initialize_maze():
    """20*22"""
    maze = [[IS_WALL]*GRID_WIDTH for i in range(GRID_HEIGHT)]
    for i in range(1, GRID_WIDTH-1):
        for j in range(1, GRID_HEIGHT-1):
            maze[j][i] = (random() < WALL_RATE)
    # clear exits
    for x, y in EXITS:
        maze[y][x] = not IS_WALL
    # clear start
    maze[START_Y][START_X] = not IS_WALL
    return maze


def handle_interaction(key):
    """records player's interaction"""
    anim = {'move': False, 'right': False, 'left': False,
            'up': False, 'down': False, 'quit': False, 'pause': False}
    if key == pygame.K_RIGHT and pos_x < GRID_WIDTH-1 and not(maze[pos_y][pos_x+1]):
        anim['move'] = True
        anim['right'] = True
    if key == pygame.K_LEFT and pos_x > 0 and not(maze[pos_y][pos_x-1]):
        anim['move'] = True
        anim['left'] = True
    if key == pygame.K_UP and pos_y > 0 and not(maze[pos_y-1][pos_x]):
        anim['move'] = True
        anim['up'] = True
    if key == pygame.K_DOWN and pos_y < GRID_HEIGHT-1 and not(maze[pos_y+1][pos_x]):
        anim['move'] = True
        anim['down'] = True
    if key == pygame.K_q or key == pygame.K_ESCAPE:
        anim['quit'] = True
    if key == pygame.K_SPACE or key == pygame.K_PAUSE:
        anim['pause'] = True
    return anim


def move(anim, x, y):
    if not anim['move'] or paused:
        return (x, y)
    if anim['right']:
        return (x+1, y)
    if anim['left']:
        return (x-1, y)
    if anim['up']:
        return (x, y-1)
    if anim['down']:
        return (x, y+1)


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


def handle_shift(grid):
    global pos_x, pos_y
    """from anywhere in any direction"""
    # chose orientation
    columns = (random() < 0.5)  # lines or columns
    uplim = GRID_WIDTH-1
    if not columns:
        uplim = GRID_HEIGHT-1

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
            for y in range(1, GRID_HEIGHT-1):
                grid[y][i] = grid[y][i+positives]
        else:
            for x in range(1, GRID_WIDTH-1):
                grid[i][x] = grid[i+positives][x]

    """create new walls"""
    if columns:
        for y in range(1, GRID_HEIGHT-1):
            grid[y][stop] = (random() < WALL_RATE)
    else:
        for x in range(1, GRID_WIDTH-1):
            grid[stop][x] = (random() < WALL_RATE)

    """clear center"""
    grid[START_Y][START_X] = not IS_WALL

    """move character"""
    if grid[pos_y][pos_x] == IS_WALL:
        if columns:
            if grid[pos_y][pos_x-positives] == IS_WALL:
                pos_x = START_X
                pos_y = START_Y
            else:
                pos_x -= positives
        else:
            if grid[pos_y-positives][pos_x] == IS_WALL:
                pos_x = START_X
                pos_y = START_Y
            else:
                pos_y -= positives


def is_end_game(x, y):
    if (x, y) in EXITS:
        return True
    return False


def save_score(current_time):  # in ms
    # read previous scores
    scorefile = open('highscores.txt', 'r+')
    scorelist = scorefile.readlines()
    scorefile.close()
    # check if level already in scores
    exists = None
    previous = None
    for score in scorelist:
        level, time = score.split(': ')
        if level == str(current_level):
            exists = score
            previous = int(time)
    # compare times and update
    if exists:
        if previous > end_time:
            i = scorelist.index(exists)
            scorelist.remove(exists)
            scorelist.insert(i, "{}: {}\n".format(current_level, current_time))
    else:
        scorelist.append("{}: {}\n".format(current_level, current_time))
    # write new scores
    scorefile = open('highscores.txt', 'w+')
    scorefile.writelines(scorelist)
    scorefile.close()


# define macro variables
GRID_WIDTH = 20
GRID_HEIGHT = 22
if GRID_WIDTH < 5 or GRID_HEIGHT < 5:
    # maze too small
    quit()
IS_WALL = True
WALL_RATE = 0.45
START_X = GRID_WIDTH//2  # centre cleared by def
START_Y = GRID_HEIGHT//2  # centre cleared by def
EXITS = [(GRID_WIDTH//2, 0), (GRID_WIDTH//2 + 1, 0),
         (GRID_WIDTH - 1, GRID_HEIGHT//2), (GRID_WIDTH - 1, GRID_HEIGHT//2 + 1),
         (0, GRID_HEIGHT//2), (0, GRID_HEIGHT//2 + 1),
         (GRID_WIDTH//2, GRID_HEIGHT - 1), (GRID_WIDTH//2 + 1, GRID_HEIGHT - 1)]
TIMER = 1000
LOOP_KEY = USEREVENT+2
LOOP_SHIFT = USEREVENT+1

# define global variables
pos_x = START_X
pos_y = START_Y
key_flags = list()
current_level = 1
level_end = False
paused_time = 0
pause_start = None
end_time = None

# setup
pygame.time.set_timer(LOOP_SHIFT, TIMER)  # loop for shift
maze = initialize_maze()
draw = view.View(GRID_WIDTH, GRID_HEIGHT)

# program
close_game = False
paused = False
while not close_game:
    for event in [pygame.event.wait()] + pygame.event.get():
        if event.type == LOOP_SHIFT:
            handle_shift(maze)
        if event.type == pygame.KEYDOWN:
            key_flags.append(event.key)
            pygame.time.set_timer(LOOP_KEY, 200)  # hold down loop
        if event.type == pygame.KEYDOWN or event.type == LOOP_KEY:
            for key in key_flags:
                anim = handle_interaction(key)
                close_game = anim['quit']
                paused = pause_game(paused, anim['pause'])
                pos_x, pos_y = move(anim, pos_x, pos_y)
        if event.type == pygame.KEYUP:
            key_flags.remove(event.key)
            if not key_flags:
                pygame.time.set_timer(LOOP_KEY, 0)
        if event.type == pygame.QUIT:
            close_game = True

        draw.game(current_level, maze, pos_x, pos_y,
                         paused, paused_time, level_end, end_time)

        if is_end_game(pos_x, pos_y):
            if not level_end:
                end_time = pygame.time.get_ticks()-paused_time
                level_end = True
                paused = True
                pygame.time.set_timer(LOOP_SHIFT, 0)
                save_score(end_time)
            draw.end(current_level)

        pygame.display.update()
quit()
