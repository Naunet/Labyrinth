import pygame
from pygame.locals import *
from random import random, randrange
import time

def background(color):
    window.fill(color) 

def initialize_maze():
    """20*22"""
    maze = [ [IS_WALL]*GRID_WIDTH for i in range(GRID_HEIGHT)]
    for i in range(1,GRID_WIDTH-1):
        for j in range(1,GRID_HEIGHT-1):
            maze[j][i]=(random()<WALL_RATE)
    #clear exits
    for x,y in EXITS:
        maze[y][x] = not IS_WALL
    #clear start
    maze[START_Y][START_X]=not IS_WALL
    return maze

def top_corner(x, y):
    """coordinates to pixels"""
    x=SIZE*x+BORDER_X
    y=SIZE*y+BORDER_Y
    return (x, y)

def draw_rectangle(topCorner, width, height, color):
    Rect = pygame.Rect(topCorner[0], topCorner[1], width, height)
    pygame.draw.rect(window, color, Rect)

def draw_maze(grid, size, color):
    for j in range(GRID_HEIGHT):
        for i in range(GRID_WIDTH):
            if (grid[j][i]):
                draw_rectangle(top_corner(i,j), size, size, color)

def draw_char(x, y):
    #To be improved
    x, y = top_corner(x,y)
    scale = 0.7
    x += (1-scale)/2*SIZE
    y += (1-scale)/2*SIZE
    draw_rectangle((x,y), SIZE*scale, SIZE*scale, (0,0,0,255))

def handle_interaction(x, y, grid, key):
    """records player's interaction"""
    anim={'move':False,'right':False,'left':False,'up':False,'down':False,'quit':False,'pause':False}
    if key==pygame.K_RIGHT and x<GRID_WIDTH-1 and not(grid[y][x+1]):
        anim['move'] = True
        anim['right'] = True
    if key==pygame.K_LEFT and x>0 and not(grid[y][x-1]):
        anim['move'] = True
        anim['left'] = True
    if key==pygame.K_UP and y>0 and not(grid[y-1][x]):
        anim['move'] = True
        anim['up'] = True
    if key==pygame.K_DOWN and y<GRID_HEIGHT-1 and not(grid[y+1][x]):
        anim['move'] = True
        anim['down'] = True
    if key==pygame.K_q or key==pygame.K_ESCAPE:
        anim['quit'] = True
    if key==pygame.K_SPACE or key==pygame.K_PAUSE:
        anim['pause'] = True
    return anim

def move(anim, x, y):
    if not anim['move'] or paused:
        return (x, y)
    if anim['right']:
        return (x+1, y)
    if anim['left']:
        return (x-1,y)
    if anim['up']:
        return (x, y-1)
    if anim['down']:
        return (x, y+1)

def pause_game(old, change):
    if not old and change:
        pygame.time.set_timer(USEREVENT+1, 0)
        return True
    if old and change:
        pygame.time.set_timer(USEREVENT+1, TIMER)
        return False
    return old

def handle_shift(grid, pos_x, pos_y):
    """from anywhere in any direction"""
    #chose orientation
    columns = (random()<0.5) #lines or columns
    uplim = GRID_WIDTH-1
    if not columns:
        uplim = GRID_HEIGHT-1

    #values
    start = 1
    stop = randrange(1,uplim)
    positives = 1

    #chose section
    above = (random()<0.5) #above or left
    if not above:
        start = stop
        stop = uplim-1
        
    #chose direction
    downwards = (random()<0.5) #downwards or right
    if downwards:
        tmp = start
        start = stop
        stop = tmp
        positives = -1
    
    """shift"""
    for i in range(start, stop, positives):
        if(columns):
            for y in range(1,GRID_HEIGHT-1):
                grid[y][i]=grid[y][i+positives]
        else:
            for x in range(1,GRID_WIDTH-1):
                grid[i][x]=grid[i+positives][x]

    """create new walls"""
    if(columns):
        for y in range(1,GRID_HEIGHT-1):
            grid[y][stop] = (random()<WALL_RATE)
    else:
        for x in range(1,GRID_WIDTH-1):
            grid[stop][x] = (random()<WALL_RATE)

    """clear center"""
    grid[START_Y][START_X] = not IS_WALL 

    """move character"""
    if(grid[pos_y][pos_x]==IS_WALL):
        if(columns):
            if(grid[pos_y][pos_x-positives]==IS_WALL):
                pos_x = START_X
                pos_y = START_Y
            else:
                pos_x -= positives
        else:
            if(grid[pos_y-positives][pos_x]==IS_WALL):
                pos_x = START_X
                pos_y = START_Y
            else:
                pos_y -= positives

    return pos_x, pos_y

def print_maze(matrix):
    for i in range(GRID_HEIGHT):
        print(matrix[i])

def is_end_game(x, y):
    if (x, y) in EXITS:
        return True
    return False

def draw_end():
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 32)
    text = font.render('Well Done!', True, (0,0,0), (255,255,255)) 
    textRect = text.get_rect() 
    textRect.center = (RES_X//2,RES_Y//4) 
    window.blit(text, textRect)

#High scores https://stackoverflow.com/questions/17181813/blitting-text-in-pygame

# define macro variables
IS_WALL = True
WALL_RATE = 0.45
GRID_HEIGHT = 22
GRID_WIDTH = 20
RES_X = 510 #swap to dynamic
RES_Y = 560 #swap to dynamic
C_PATH = (250, 210, 140, 255)
C_WALL = (0, 153, 0, 255)
SIZE = min(RES_X//GRID_WIDTH, RES_Y//GRID_HEIGHT)
BORDER_X = (RES_X-SIZE*GRID_WIDTH)//2
BORDER_Y = (RES_Y-SIZE*GRID_HEIGHT)//2
START_X = 10 #centre cleared by def
START_Y = 11 #centre cleared by def
EXITS = [(4,0), (5,0), (14,0), (15,0), 
        (4,21), (5,21), (14,21), (15,21)]
TIMER = 1000

#define global variables
pos_x = START_X
pos_y = START_Y
key_flags = list()

#setup
pygame.display.init()
window = pygame.display.set_mode((RES_X,RES_Y))
pygame.display.set_caption("Moving labyrinth")
maze = initialize_maze()
pygame.time.set_timer(USEREVENT+1, TIMER) #loop for shift

#program
end_game = False
paused = False
while not end_game: 
    #pygame.event.wait()
    for event in pygame.event.get():
        if event.type == USEREVENT+1:
            pos_x, pos_y = handle_shift(maze, pos_x, pos_y)
        if event.type == pygame.KEYDOWN:
            key_flags.append(event.key)
            pygame.time.set_timer(USEREVENT+2, 200) #hold down loop
        if event.type == pygame.KEYDOWN or event.type == USEREVENT+2:
            for key in key_flags:
                anim = handle_interaction(pos_x, pos_y, maze, key)
                end_game = anim['quit']
                paused = pause_game(paused, anim['pause'])
                pos_x, pos_y = move(anim, pos_x, pos_y)
        if event.type == pygame.KEYUP:
            key_flags.remove(event.key)
            if not key_flags:
                pygame.time.set_timer(USEREVENT+2, 0)
        if event.type == pygame.QUIT:
            end_game = True

        background(C_PATH)
        draw_maze(maze, SIZE, C_WALL)
        draw_char(pos_x, pos_y)

        if is_end_game(pos_x, pos_y):
            paused = True
            pygame.time.set_timer(USEREVENT+1, 0)
            draw_end()

        pygame.display.update()
quit()
