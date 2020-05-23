import pygame
from pygame.locals import *
from random import random, randrange
import time

def background(color):
    window.fill(color) 

def initialize_maze():
    """20*22"""
    maze = [ [is_wall]*20 for i in range(22)]
    for i in range(1,19):
        for j in range(1,21):
            maze[j][i]=(random()<WALL_RATE)
    #clear exits
    maze[0][4]=not is_wall
    maze[0][5]=not is_wall
    maze[0][14]=not is_wall
    maze[0][15]=not is_wall
    maze[21][4]=not is_wall
    maze[21][5]=not is_wall
    maze[21][14]=not is_wall
    maze[21][15]=not is_wall
    #clear start
    maze[11][10]=not is_wall
    return maze

def top_corner(x, y):
    """coordinates to pixels"""
    x=size*x+b
    y=size*y+c
    return (x, y)

def draw_rectangle(topCorner, width, height, color):
    Rect = pygame.Rect(topCorner[0], topCorner[1], width, height)
    pygame.draw.rect(window, color, Rect)

def draw_maze(grid, size, color):
    for j in range(grid_height):
        for i in range(grid_width):
            if (grid[j][i]):
                draw_rectangle(top_corner(i,j), size, size, color)

def draw_char(x, y):
    x, y = top_corner(x,y)
    scale = 0.7
    x += (1-scale)/2*size
    y += (1-scale)/2*size
    draw_rectangle((x,y), size*scale, size*scale, (0,0,0,255))

def handle_interaction(x, y, grid, key=None):
    """records player's interaction"""
    anim={'move':False,'right':False,'left':False,'up':False,'down':False,'quit':False,'pause':False}
    if key==pygame.K_RIGHT and x<grid_width-1 and not(grid[y][x+1]):
        anim['move'] = True
        anim['right'] = True
    if key==pygame.K_LEFT and x>0 and not(grid[y][x-1]):
        anim['move'] = True
        anim['left'] = True
    if key==pygame.K_UP and y>0 and not(grid[y-1][x]):
        anim['move'] = True
        anim['up'] = True
    if key==pygame.K_DOWN and y<grid_height-1 and not(grid[y+1][x]):
        anim['move'] = True
        anim['down'] = True
    if key==pygame.K_q or key==pygame.K_ESCAPE:
        anim['quit'] = True
    if key==pygame.K_SPACE or key==pygame.K_PAUSE:
        print("Key pressed")
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
        print("Set pause")
        pygame.time.set_timer(USEREVENT+1, 0)
        return True
    if old and change:
        print("End pause")
        pygame.time.set_timer(USEREVENT+1, 1000)
        return False
    return old

def handle_shift(grid):
    """from anywhere in any direction"""
    #chose orientation
    horizontal = (random()<0.5) #horizontal or vertical axis
    if horizontal:
        uplim = grid_width-1
    else:
        uplim = grid_height-1

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
        if(horizontal):
            for y in range(1,grid_height-1):
                grid[y][i]=grid[y][i+positives]
        else:
            for x in range(1,grid_width-1):
                grid[i][x]=grid[i+positives][x]

    """create new walls"""
    if(horizontal):
        for y in range(1,grid_height-1):
            grid[y][stop]=(random()<WALL_RATE)
    else:
        for x in range(1,grid_width-1):
            grid[stop][x]=(random()<WALL_RATE)

def print_maze(matrix):
    for i in range(grid_height):
        print(matrix[i])

# define variables
is_wall = True
WALL_RATE = 0.45
grid_height = 22
grid_width = 20
res_x = 510 #swap to dynamic
res_y = 560 #swap to dynamic
c_path = (250, 210, 140, 255)
c_wall = (0, 153, 0, 255)
size=min(res_x//grid_width, res_y//grid_height)
b=(res_x-size*grid_width)//2
c=(res_y-size*grid_height)//2
pos_x = 10 #centre cleared by def
pos_y = 11 #centre cleared by def

#setup
pygame.display.init()
window = pygame.display.set_mode((res_x,res_y))
pygame.display.set_caption("Moving labyrinth")
maze=initialize_maze()
pygame.time.set_timer(USEREVENT+1, 1000) #loop for shift

#program
background(c_path)
draw_maze(maze, size, c_wall)
draw_char(pos_x, pos_y)
pygame.display.update()

end_game = False
paused = False
while not end_game: 
    for event in pygame.event.get():
        background(c_path)
        draw_maze(maze, size, c_wall)
        draw_char(pos_x, pos_y)
        if event.type == USEREVENT+1:
            handle_shift(maze)
        if event.type == pygame.KEYDOWN:
            anim = handle_interaction(pos_x, pos_y, maze, event.key)
            end_game = anim['quit']
            paused = pause_game(paused, anim['pause'])
            pos_x, pos_y = move(anim, pos_x, pos_y)
        if event.type == pygame.QUIT:
            end_game = True
        handle_interaction(pos_x, pos_y, maze) #delete?
        pygame.display.update()
quit()