import pygame
from sys import exit
import numpy as np
pygame.init() 

#Game Window
WIDTH = 800
HEIGHT = 400

screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption('AGV Simulator') 
clock = pygame.time.Clock() #for setting fps
font = pygame.font.Font('graphics/Arial.ttf', 15) 


#Creating background
fleet_rect = pygame.Rect(15, 15, 120, 100)  #left,top,width,height
delivery_rect = pygame.Rect(30, 150, 120, 225)
factory_map_rect = pygame.Rect(150, 15, 630, 360)

#Creating text
text_fleet_surf = font.render('Fleet', False, 'Black')
text_fleet_rect = text_fleet_surf.get_rect(topleft = (55,0))

text_delivery_surf = font.render('Delivery', False, 'Black')
text_delivery_rect = text_delivery_surf.get_rect(topleft = (45,135))

text_factory_map_surf = font.render('Factory Map', False, 'Black')
text_factory_map_rect = text_factory_map_surf.get_rect(topleft = (400,0))


#Creating AGV
agv_start_pos = (150, 300)
agv_surf = pygame.image.load('graphics/agv.png').convert_alpha() 
agv_surf = pygame.transform.scale(agv_surf, (20,20)) #making agv smaller
agv_rect = agv_surf.get_rect(topleft = agv_start_pos) #converting to rect

#Draw the backround stuff
def draw_bg():
    screen.fill('White')
    pygame.draw.rect(screen, 'Black', fleet_rect, 2)
    pygame.draw.rect(screen, 'Black', delivery_rect, 2)
    pygame.draw.rect(screen, 'Black', factory_map_rect, 2)

#Draw the text
def draw_text():
    #placing text on window
    screen.blit(text_factory_map_surf,text_factory_map_rect)
    screen.blit(text_fleet_surf,text_fleet_rect)
    screen.blit(text_delivery_surf, text_delivery_rect)

#Draw the agv
def draw_agv():
    #placing agv on window
    screen.blit(agv_surf, agv_rect)

#Makes a new list with corrected coordinates
corrected = []    
def autocorrect(lines):
    if done_line:
        corrected.append(lines[0])
        for i in range(0, len(lines), 2):
            if (abs(lines[i][0] - lines[i+1][0]) > abs(lines[i][1] - lines[i+1][1])):
                corrected.append((lines[i+1][0], lines[i][1]))
                corrected.append((lines[i+1][0], lines[i][1]))
            else:
                corrected.append((lines[i][0], lines[i+1][1]))
                corrected.append((lines[i][0], lines[i+1][1]))
        del corrected[len(corrected) - 1]



lines = []
start = agv_start_pos
done_line = False;
#Draws the lines from a list
def draw_lines(x):    
    if done_line:
        for i in range(0, len(x), 2): #change to while?
            pygame.draw.line(screen,'Gold', x[i], x[i+1]) #Need a start coordinate and end coordinate to draw a line     
    
while True:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT: #Checking if the window is trying to be closed
            pygame.quit()
            exit()
    
        
        # press a to save a coordinate
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                end = pygame.mouse.get_pos() #Get the coordinates of cursor location
                lines.append(start)
                lines.append(end)
                start = end
                print('Line saved')
                print('Current Coordiantes saved', lines)
                
        #Start drawing the lines on the screen after pressing 'd' key    
        # press d to start drawing the lines on the screen
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                print('Now Drawing ROUTE')
                done_line = True
    
    
                                         
    draw_bg()
    draw_text()
    autocorrect(lines) #make straiiiight lines
    draw_lines(corrected)
    draw_agv()

    
    pygame.display.update()
    clock.tick(60) #60 FPS