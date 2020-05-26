import pygame
from pygame.locals import *
from random import random, randrange
import time

def background(color, level):
    window.fill(color)
    text = font.render("Level "+str(level), True, (0,0,20)) 
    textRect = text.get_rect()
    offset = (HEADER-textRect.height)//2
    textRect.topleft = (offset, offset)
    window.blit(text, textRect)

def draw_clock():
    text = font.render("Pause", True, (0,0,0), (255,255,255))
    if end_level:
        time = end_time//1000
        string = "{0:02}:{1:02}".format(time//60, time%60)
        text = font.render(string, True, (255,0,0), (255,255,255)) 
    if not paused:
        time = (pygame.time.get_ticks() - paused_time)//1000 #convert to seconds
        string = "{0:02}:{1:02}".format(time//60, time%60)
        text = font.render(string, True, (0,0,0), (255,255,255)) 
    textRect = text.get_rect()
    offset = (HEADER-textRect.height)//2
    textRect.topright = (RES_X-offset, offset)
    window.blit(text, textRect)

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

def draw_maze(size, color):
    for j in range(GRID_HEIGHT):
        for i in range(GRID_WIDTH):
            if (maze[j][i]):
                draw_rectangle(top_corner(i,j), size, size, color)

def draw_char(x, y):
    #To be improved
    x, y = top_corner(x,y)
    scale = 0.7
    x += (1-scale)/2*SIZE
    y += (1-scale)/2*SIZE
    draw_rectangle((x,y), SIZE*scale, SIZE*scale, (0,0,0,255))

def draw_game(level):
    background(C_PATH, level)
    draw_clock()
    draw_maze(SIZE, C_WALL)
    draw_char(pos_x, pos_y)

def handle_interaction(key):
    """records player's interaction"""
    anim={'move':False,'right':False,'left':False,'up':False,'down':False,'quit':False,'pause':False}
    if key==pygame.K_RIGHT and pos_x<GRID_WIDTH-1 and not(maze[pos_y][pos_x+1]):
        anim['move'] = True
        anim['right'] = True
    if key==pygame.K_LEFT and pos_x>0 and not(maze[pos_y][pos_x-1]):
        anim['move'] = True
        anim['left'] = True
    if key==pygame.K_UP and pos_y>0 and not(maze[pos_y-1][pos_x]):
        anim['move'] = True
        anim['up'] = True
    if key==pygame.K_DOWN and pos_y<GRID_HEIGHT-1 and not(maze[pos_y+1][pos_x]):
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

def is_end_game(x, y):
    if (x, y) in EXITS:
        return True
    return False

def draw_end():
    text = font.render('Level Complete!', True, (0,0,0), (255,255,255)) 
    textRect = text.get_rect() 
    textRect.center = (RES_X//2,RES_Y//3) 
    window.blit(text, textRect)

def save_score(time): #in ms
    #file open
    #file write
    #file save
    #file close
    return

#High scores https://stackoverflow.com/questions/17181813/blitting-text-in-pygame

# define macro variables
GRID_HEIGHT = 22
GRID_WIDTH = 20
RES_X = 510 #swap to dynamic
RES_Y = 610 #swap to dynamic
IS_WALL = True
WALL_RATE = 0.45
C_PATH = (250, 210, 140, 255)
C_WALL = (0, 153, 0, 255)
HEADER = 50
SIZE = min(RES_X//GRID_WIDTH, (RES_Y-HEADER)//GRID_HEIGHT)
BORDER_X = (RES_X-SIZE*GRID_WIDTH)//2
BORDER_Y = HEADER + (RES_Y-SIZE*GRID_HEIGHT-HEADER)//2
START_X = 10 #centre cleared by def
START_Y = 11 #centre cleared by def
EXITS = [(4,0), (5,0), (14,0), (15,0), 
        (4,GRID_HEIGHT-1), (5,GRID_HEIGHT-1), 
        (14,GRID_HEIGHT-1), (15,GRID_HEIGHT-1)]
TIMER = 1000
LOOP_KEY = USEREVENT+2
LOOP_SHIFT = USEREVENT+1

#define global variables
pos_x = START_X
pos_y = START_Y
key_flags = list()
level = 1
end_level = False
paused_time = 0
pause_start = None
end_time = None

#setup
pygame.display.init()
pygame.font.init()
window = pygame.display.set_mode((RES_X,RES_Y))
pygame.display.set_caption("Moving labyrinth")
font = pygame.font.Font(pygame.font.get_default_font(), 32)
pygame.time.set_timer(LOOP_SHIFT, TIMER) #loop for shift
maze = initialize_maze()

#program 
close_game = False
paused = False
while not close_game: 
    for event in [pygame.event.wait()] + pygame.event.get():
        if event.type == LOOP_SHIFT:
            handle_shift(maze)
        if event.type == pygame.KEYDOWN:
            key_flags.append(event.key)
            pygame.time.set_timer(LOOP_KEY, 200) #hold down loop
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

        draw_game(level)

        if is_end_game(pos_x, pos_y):
            if not end_level:
                end_time = pygame.time.get_ticks()-paused_time
                end_level = True
                paused = True
                pygame.time.set_timer(LOOP_SHIFT, 0)
                save_score(end_time)
            draw_end()

        pygame.display.update()
quit()
