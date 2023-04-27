#Instructions:
#After running, create your own factory layout, or load in the one that is currently saved. The simulation must contain an equal amount of pickup (yellow)
#and dropoff (blue) points. The number of recharge points must equal the amount of pickup and dropoff points divided by two. Once the
#points are configured, press A to spawn in the AGVs. Then, press U to see the battery indicators. Press W to remove the grid lines.
#Pressing s on the keyboard once A is pressed starts the scanning process. Input values in cm for the coordinates and diamter for the RFID and antenna.




import pygame
import button
import csv 
import paho.mqtt.client as mqtt
import time
import os   
from struct import *
import math

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

pygame.init()
clock = pygame.time.Clock()
FPS = 60

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
LOWER_MARGIN = 100
SIDE_MARGIN = 300


screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('AGV Simulator')


#define game variables
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 4
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0 
scroll_speed = 1
TILE_OFFSET = TILE_SIZE // 2
game_paused = False

clientRFID = "testRFIDMain"
clientANTENNA = "testANTENNAMain"
broker = 'test.mosquitto.org'
topicRFID = "FLOSCapstone/acl61582/RFIDMain"
topicANTENNA = "FLOSCapstone/acl61582/ANTENNAMain"
username = "giiuser"
password = "giipassword"

def onMessageRFID(client_obj, userdata, message):
    x,y,to_send_byte = unpack('ii 6s',message.payload)
    AGV_col = str(to_send_byte,'utf-8')
    print(f"The {AGV_col} AGV is at ({x},{y}) (RFID)")


def onMessageANTENNA(client_obj, userdata, message):
    x,y,to_send_byte = unpack('ii 6s',message.payload)
    AGV_col = str(to_send_byte,'utf-8')
    print(f"The {AGV_col} AGV is at ({x},{y}) (antenna)")

clientRFID = mqtt.Client(clientRFID)
clientANTENNA = mqtt.Client(clientANTENNA)
clientRFID.on_message = onMessageRFID
clientANTENNA.on_message = onMessageANTENNA
#clientANTENNA.username_pw_set(username,password)
#clientRFID.username_pw_set(username,password)
clientRFID.connect(broker)
clientANTENNA.connect(broker)
clientRFID.subscribe(topicRFID)
clientANTENNA.subscribe(topicANTENNA)



#load images
bg = pygame.image.load('graphics/background.png').convert_alpha()
#store tiles in list
img_list = [] 
for x in range(TILE_TYPES):
    img = pygame.image.load(f'graphics/TileTypes/{x}.png')
    img = pygame.transform.scale(img,(TILE_SIZE, TILE_SIZE))
    img_list.append(img)

save_img = pygame.image.load('graphics/save_btn.png').convert_alpha()
load_img = pygame.image.load('graphics/load_btn.png').convert_alpha()

#define colours
WHITE = (255,255,255)
BLACK = (0, 0, 0)
ORANGE = (250, 213, 165)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)

#define fonts
font = pygame.font.SysFont("arialblack", 40)
battery_level_font = pygame.font.SysFont("arialblack", 20)
battery_font = pygame.font.SysFont("arialblack", 10)

#creat empty tile list
world_data = []
for row in range(ROWS):
    r = [TILE_TYPES] * MAX_COLS #Updated to match tile type variable
    world_data.append(r)

# #create ground
# for tile in range(0, MAX_COLS):
#     world_data[ROWS - 1][tile] = 0
def draw_text(text, font, text_color, x, y):
    img = font.render(text,True, WHITE)
    screen.blit(img,(x,y))

#draw background function 
def draw_bg():
    screen.fill(WHITE)
    width = bg.get_width()
    for x in range(4):
        screen.blit(bg, ((x * width) - scroll, 0))

#draw grid
def draw_grid():
    #Vertical lines
    for c in range(MAX_COLS + 1): 
        pygame.draw.line(screen, BLACK, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    #horizontal lines
    for c in range(ROWS + 1): 
        pygame.draw.line(screen, BLACK, (0, c * TILE_SIZE), (SCREEN_WIDTH , c * TILE_SIZE))

#function for drawing the world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile <= TILE_TYPES - 1: #Updated
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE) ) 

def mqtt_convert_backx(x):
    x1 = x*SCREEN_WIDTH/9965.36

    return(math.ceil(x1))
def mqtt_convert_backy(y):
    y1 = SCREEN_HEIGHT - y*(SCREEN_HEIGHT/3616.96)

    return(math.ceil(y1))

RFID_path = 'graphics/RFID_IMG.png'
RFID_num = int(input('How Many RFIDs are there? (Please enter a number)'))

class RFID(pygame.sprite.Sprite):
    def __init__(self,RFID_path,x_pos,y_pos):
        super().__init__()

        self.image = pygame.image.load(RFID_path).convert_alpha()
        self.image = pygame.transform.scale(self.image,(TILE_SIZE,TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = [x_pos,y_pos]
        self.pos = self.rect.center
    
    def draw(self,surface):
        surface.blit(self.image,self.rect)


ANTENNA_num = int(input("How many Antennas are there?"))
ANTENNA_path = 'graphics/Black_Circle_Antenna.png'
class ANTENNA(pygame.sprite.Sprite):
    def __init__(self,ANTENNA_path,x,y,diameter):
        super().__init__()
        
        self.image = pygame.image.load(ANTENNA_path).convert_alpha(screen)
        self.image = pygame.transform.scale(self.image,(diameter,diameter))
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]  
        self.diameter = diameter

    def draw(self,surface):
        surface.blit(self.image,self.rect)

        



#create agv class                
class AGV(pygame.sprite.Sprite):
    def __init__(self, number):
        super().__init__()
        
        # basic
        self.colors = ['red', 'blue', 'purple', 'orange', 'brown'] #Possible colors
        self.color = self.colors[number] #
        self.color_path = os.path.join('graphics/'+self.color+'-circle.png')
        self.image = pygame.image.load(self.color_path).convert_alpha()
        self.image = pygame.transform.scale(self.image,(11, 11))
        self.rect = self.image.get_rect(center = (TILE_OFFSET + 25 * number,15*TILE_SIZE - TILE_OFFSET)) #Each AGV will get placed on a different block
        
        
        # movement
        self.pos = self.rect.center
        self.speed = 0.7
        self.direction = pygame.math.Vector2(0,0)
        self.battery = 100 #Initial battery
        self.compare_battery = 0 #Used to check if the battery has decreased
        
        # path
        self.path = []
        self.collision_rects = []
        self.target_pickup_x, self.target_pickup_y = 0,0
        self.target_dropoff_x, self.target_dropoff_y = 0,0
        self.recharge_x, self.recharge_y = 0,0
        self.mode = 'idle'

    def get_battery(self):
        return round(self.battery, 1)

    def set_mode(self,mode): #Modes are 'picking up', 'dropping off', and 'driving'
        self.mode = mode

    def set_battery_compare(self,battery):
        self.compare_battery = battery

        
    def get_coord(self):
        col = self.rect.centerx // TILE_SIZE
        row = self.rect.centery // TILE_SIZE
        return (col,row)
    
     
    def set_dropoff(self,x,y):
        self.target_dropoff_x = x
        self.target_dropoff_y = y
        
    def set_pickup(self,x,y):
        self.target_pickup_x = x
        self.target_pickup_y = y


    def set_recharge(self,x,y):
        self.recharge_x = x
        self.recharge_y = y
        

    def set_path(self,path):
        self.path = path
        self.create_collision_rects()
        
    def create_collision_rects(self):
        if self.path:
            self.collision_rects = []
            for point in self.path:
                x = (point[0] * 25) + TILE_OFFSET
                y = (point[1] * 25) + TILE_OFFSET
                rect = pygame.Rect((x - 2,y - 2),(4,4))
                self.collision_rects.append(rect)
                
    def get_direction(self):
        if self.collision_rects:
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collision_rects[0].center)
            self.direction = (end-start).normalize()
        else:
            self.direction = pygame.math.Vector2(0,0)
            self.path = []
    
    def check_collisions(self):
        if self.collision_rects:
            for rect in self.collision_rects:
                if rect.collidepoint(self.pos):
                    del self.collision_rects[0]
                    self.get_direction()
    
    def update(self):
        self.pos += self.direction * self.speed
        self.check_collisions()
        self.rect.center = self.pos
        self.battery -= .007 * self.speed #Decrease battery relative to AGV speed
AGVs = [] #Create empty list to store the AGV objects
RFIDs = pygame.sprite.Group()
for rfid in range(RFID_num):
    new_RFID = RFID(RFID_path,int(mqtt_convert_backx(float(input("What is the x coordinate for the RFID?")))),
                    int(mqtt_convert_backy(float(input("What is the y coordinate for the RFID?")))))
    RFIDs.add(new_RFID)
ANTENNAs = pygame.sprite.Group()
for antennas in range (ANTENNA_num):
    new_ANTENNA = ANTENNA(ANTENNA_path,int(mqtt_convert_backx(float(input("What is the x coordinate of the center of the antenna?")))),
                           int(mqtt_convert_backx(float(input("What is the y coordinate of the center of the antenna?")))),
                           int(mqtt_convert_backx(float(input("What is the diameter of the antenna?")))))
    ANTENNAs.add(new_ANTENNA)
print(len(ANTENNAs))
                
#AGVs = [] #Create empty list to store the AGV objects

battery_surf = [] #Create an empty list to store the battery indicators 
battery_rect = []
draw_battery = False

battery_text = battery_level_font.render('Battery Levels', True, BLACK, ORANGE)
battery_text_rect = battery_text.get_rect()
battery_text_rect.center = (SCREEN_WIDTH + 150, SIDE_MARGIN - 50)

def update_indicators():
    for i in range(len(AGVs)):
        battery_surf.append(battery_font.render(str(AGVs[i].sprite.get_battery())+ "%", True, BLACK, ORANGE))
        battery_rect.append(battery_surf[i].get_rect())
        battery_rect[i].center = (SCREEN_WIDTH + 50 + i * 50, SIDE_MARGIN)
        screen.blit(battery_surf[i], battery_rect[i])
        screen.blit(AGVs[i].sprite.image, (SCREEN_WIDTH + 40 + i * 50, SIDE_MARGIN - 30)) #Add agv image
    battery_surf.clear()
    battery_rect.clear()

def RFIDTrigger():
    for i in range(len(AGVs)):
        for AGV in (AGVs[i]):
            if pygame.sprite.spritecollideany(AGV,RFIDs):
                x_AGV = ((AGVs[i].sprite.rect.x))
                y_AGV =(AGVs[i].sprite.rect.y)   
                x,y = mqtt_convert(x_AGV,y_AGV)
                x = int(x)
                y = int(y)
                to_send_string = AGVs[i].sprite.color
                to_send_byte = bytes(to_send_string,'utf-8')
                to_send = pack('2i 6s',x,y,to_send_byte)
                clientRFID.publish(topicRFID,to_send)
    else:
        return
    
def ANTENNATrigger():
    for i in range(len(AGVs)):
        for AGV in (AGVs[i]):
            X1,Y1 = AGVs[i].sprite.rect.topleft
            X2,Y2 = AGVs[i].sprite.rect.bottomright
            for ANTENNA in (ANTENNAs):
                XC = ANTENNA.rect.centerx
                YC = ANTENNA.rect.centery
                XN = max(X1, min(XC, X2))
                YN = max(Y1, min(YC, Y2))
                DX = XN - XC
                DY = YN - YC
                if (DX**2 + DY**2) <= ((ANTENNA.diameter)/2)**2:
                    x_AGV = ((AGVs[i].sprite.rect.x))
                    y_AGV =(AGVs[i].sprite.rect.y)
                    x,y = mqtt_convert(x_AGV,y_AGV)
                    x = int(x)
                    y = int(y)  
                    to_send_string = AGVs[i].sprite.color
                    to_send_byte = bytes(to_send_string,'utf-8')
                    to_send = pack('2i 6s',x,y,to_send_byte)
                    clientANTENNA.publish(topicANTENNA,to_send)


                  


#Find number of consumption points
def find_consumption(matrix):
    c = 0
    for i in range(ROWS):
        for j in range(MAX_COLS):
            if matrix[i][j] == 1 or matrix[i][j] == 2:
                c += 1
    return c

#Finds the recharge point
def find_recharge(matrix):
    coords = []
    for i in range(ROWS):
        for j in range(MAX_COLS):
            if matrix[i][j] == 3:
                coords.append((j,i))
    return coords

#Finds locations of pickup points
def find_pickup(matrix):
    coords = []
    for i in range(ROWS):
        for j in range(MAX_COLS):
            if matrix[i][j] == 1:
                coords.append((j,i))
    return coords

#Finds locations of dropoff points
def find_dropoff(matrix):
    coords = []
    for i in range(ROWS):
        for j in range(MAX_COLS):
            if matrix[i][j] == 2:
                coords.append((j,i))
    return coords      

#Draw path
def draw_path(path):
    if path:
        points = []
        for point in path:
            x = (point[0] * 25) + TILE_OFFSET
            y = (point[1] * 25) + TILE_OFFSET
            points.append((x,y))
            pygame.draw.circle(screen, '#4a4a4a', (x,y), 2)
        pygame.draw.lines(screen, '#4a4a4a', False, points, 5)


finder = AStarFinder(diagonal_movement=DiagonalMovement.always) 

def mqtt_convert(x,y):
    x1 = x * 9965.36/SCREEN_WIDTH
    y1 = (SCREEN_HEIGHT - y) * 3616.96/SCREEN_HEIGHT

    return(math.ceil(x1),math.ceil(y1))


#creat buttons
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0


#load button images
resume_img = pygame.image.load("graphics/menu/button_resume.png").convert_alpha()
options_img = pygame.image.load("graphics/menu/button_options.png").convert_alpha()
quit_img = pygame.image.load("graphics/menu/button_quit.png").convert_alpha()
video_img = pygame.image.load('graphics/menu//button_video.png').convert_alpha()
audio_img = pygame.image.load('graphics/menu//button_audio.png').convert_alpha()
keys_img = pygame.image.load('graphics/menu//button_keys.png').convert_alpha()
back_img = pygame.image.load('graphics/menu//button_back.png').convert_alpha()

#create button instances
resume_button = button.Button(304, 125, resume_img, 1)
options_button = button.Button(297, 250, options_img, 1)
quit_button = button.Button(336, 375, quit_img, 1)
video_button = button.Button(226, 75, video_img, 1)
audio_button = button.Button(225, 200, audio_img, 1)
keys_button = button.Button(246, 325, keys_img, 1)
back_button = button.Button(332, 450, back_img, 1)






clientRFID.loop_start()
clientANTENNA.loop_start()
#GAME LOOP
setup = True #For grid
path_draw = False #For drawing path
scanning_RFID = False
scanning_ANTENNA = False
next_search_time_RFID = 0
next_search_time_ANTENNA = 0
run = True
while run:

    grid = Grid(matrix = world_data) #Get grid for pathfinding

    #Draw the background
    draw_bg()

    if ANTENNA:
        ANTENNAs.draw(screen)

    #Draw the grid
    if setup:
        draw_grid()

    #if path_draw:
       # draw_path(path)  #paths arent really neccessary to draw
    
    #Draw the world (tiles)
    draw_world() 

    #if ANTENNA:
        #ANTENNAs.draw(screen)


    if RFID:
        RFIDs.draw(screen)


    

    #menu stuff
    if game_paused == True:
        screen.fill(BLACK)
        if resume_button.draw(screen):
            game_paused = False
        if options_button.draw(screen):
            pass
        if quit_button.draw(screen):
            run = False
    else:
        draw_text("Press Space to pause", font, WHITE, 260, 390)

    #AGV
    if AGV: #If the AGVs are instantiated
        for AGV in AGVs:
            AGV.update()
            AGV.draw(screen)
            grid.cleanup()

            if AGV.sprite.mode == 'idle':
                if AGV.sprite.battery < 20:
                    AGV.sprite.set_mode('recharge')
                else:
                    AGV.sprite.set_mode('pick up')


            if AGV.sprite.mode == 'pick up': #If the AGV needs to pick up
                start_x,start_y = AGV.sprite.get_coord()
                start = grid.node(start_x,start_y)
                end_x,end_y = AGV.sprite.target_pickup_x, AGV.sprite.target_pickup_y
                end = grid.node(end_x,end_y)
                path, runs = finder.find_path(start,end,grid)
                AGV.sprite.set_path(path)
                grid.cleanup()
                AGV.sprite.set_battery_compare(AGV.sprite.battery)
                AGV.sprite.set_mode('driving') #Now set it to drive

            #This logic needs to be changed    
            if AGV.sprite.mode == 'driving': #If the AGV is driving and motion has taken place
                if AGV.sprite.get_coord()[0] == AGV.sprite.target_pickup_x and AGV.sprite.get_coord()[1] == AGV.sprite.target_pickup_y : #If the AGV is on the pickup point
                    if AGV.sprite.battery < AGV.sprite.compare_battery: #If time has taken place
                        AGV.sprite.set_mode('drop off') #It now needs to dropoff
                elif AGV.sprite.get_coord()[0] == AGV.sprite.target_dropoff_x and AGV.sprite.get_coord()[1] == AGV.sprite.target_dropoff_y: #If the AGV is on the dropoff point
                        AGV.sprite.set_mode('idle') #It now needs to pickup
                elif AGV.sprite.get_coord()[0] == AGV.sprite.recharge_x and AGV.sprite.get_coord()[1] == AGV.sprite.recharge_y:
                    AGV.sprite.battery += 0.1 #Arbitrary
                    if AGV.sprite.battery > 98: #If sufficiently charged
                        AGV.sprite.set_mode('idle')
            
                    
            if AGV.sprite.mode == 'drop off': #If the AGV needs to drop off
                start_x,start_y = AGV.sprite.get_coord()
                start = grid.node(start_x,start_y)
                end_x,end_y = AGV.sprite.target_dropoff_x, AGV.sprite.target_dropoff_y
                end = grid.node(end_x,end_y)
                path, runs = finder.find_path(start,end,grid)
                AGV.sprite.set_path(path)
                grid.cleanup()
                AGV.sprite.set_battery_compare(AGV.sprite.battery)
                AGV.sprite.set_mode('driving') #Now set it to drive

            if AGV.sprite.mode == 'recharge':
                start_x,start_y = AGV.sprite.get_coord()
                start = grid.node(start_x,start_y)
                end_x,end_y = AGV.sprite.recharge_x, AGV.sprite.recharge_y
                end = grid.node(end_x,end_y)
                path, runs = finder.find_path(start,end,grid)
                AGV.sprite.set_path(path)
                grid.cleanup()
                AGV.sprite.set_battery_compare(AGV.sprite.battery)
                AGV.sprite.set_mode('driving') #Now set it to drive

                

    #Save and load data
    if save_button.draw(screen):
        #save level data
        with open('factory_map.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for row in world_data:
                writer.writerow(row)
    if load_button.draw(screen):
        scroll = 0
        with open('factory_map.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)

    #draw tile panel and tiles
    pygame.draw.rect(screen, ORANGE, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    #Draw the battery indicators
    screen.blit(battery_text, battery_text_rect)
    if draw_battery:
        update_indicators()


    #choose a tile
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count
    #highlight selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)


    #SCROLL THE MAP
    if scroll_left == True and scroll > 0:
        scroll -= 5
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5
    
    if scanning_RFID == True:
        current_time = pygame.time.get_ticks()
        if current_time>next_search_time_RFID:
            RFIDTrigger()
            next_search_time_RFID +=2000
    if scanning_ANTENNA == True:
        current_time = pygame.time.get_ticks()
        if current_time>next_search_time_ANTENNA:
            ANTENNATrigger()
            next_search_time_ANTENNA += 10000
            


    

    #add new tiles to the screen
    #get mouse postion
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = (pos[1]) // TILE_SIZE

    #check that coordinates are within tile area
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        #update tile value
        if pygame.mouse.get_pressed()[0] == 1:
           if world_data[y][x] != current_tile: 
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
           world_data[y][x] = TILE_TYPES #Updated to equal TILE_TYPES variable

    #EVENT HANDLER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:    #Scrolling while the AGVs are moving does not function as intended
            if event.key == pygame.K_LEFT:
                scroll_left = True 
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            #Scan for AGVS
            if event.key == pygame.K_s:
                scanning_RFID = True
                scanning_ANTENNA = True
                print("scanning started")
            #pause
            if event.key == pygame.K_SPACE:
                game_paused = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False 
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            #if event.key == pygame.K_s:
                #scanning = False
            
        
        #Get world data
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                print(world_data)
                
        #Stop drawing lines        
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_w:
                setup = False
                 
        #For Testing       
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_t:
                coords = find_dropoff(world_data)
                print(coords)
        
        #For testing       
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_y:
                print(AGVs[0].sprite.get_coord())
                print(AGVs[0].sprite.recharge_x)
                print(AGVs[0].sprite.recharge_y)
                print(ANTENNAs.spritedict)

        #For testing       
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_u:
                draw_battery = True

        #To create the AGVs 
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_a:
                number = find_consumption(world_data) // 2 #How many AGVs to make. Ideally, each AGV has their own unique drop off and pick up point
                for i in range(number):
                    AGVs.append(pygame.sprite.GroupSingle(AGV(number=i)))
                for i in range(len(AGVs)): #This assumes that each agv gets their own pickup and dropoff point
                    AGVs[i].sprite.set_dropoff(find_dropoff(world_data)[i][0], find_dropoff(world_data)[i][1])
                    AGVs[i].sprite.set_pickup(find_pickup(world_data)[i][0], find_pickup(world_data)[i][1])
                    AGVs[i].sprite.set_recharge(find_recharge(world_data)[i][0], find_recharge(world_data)[i][1]) #For now, each AGV shares the same recharge point
                                  
        #Speed up and slow down simulation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:
                for AGV in AGVs:
                    AGV.sprite.speed *= 1.2
            if event.key == pygame.K_MINUS:
                for AGV in AGVs:
                    AGV.sprite.speed /= 1.2


        #Test getting window position      
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_z:
                print(pygame.mouse.get_pos())
                row = pygame.mouse.get_pos()[1]
                col = pygame.mouse.get_pos()[0]
                print(row,col)
                print(mqtt_convert(col,row))
                 
    
    

    pygame.display.update()

#EXIT 
pygame.quit()
exit()