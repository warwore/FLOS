import pygame
import button
import csv 

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
TILE_TYPES = 3
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0 
scroll_speed = 1
TILE_OFFSET = TILE_SIZE // 2


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


#creat empty tile list
world_data = []
for row in range(ROWS):
    r = [3] * MAX_COLS #pathfinding library seeing anything <= 0 as an obstacle. Therefore the default number was changed from -1 to 3
    world_data.append(r)

# #create ground
# for tile in range(0, MAX_COLS):
#     world_data[ROWS - 1][tile] = 0

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
    for c in range(MAX_COLS + 1): 
        pygame.draw.line(screen, BLACK, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))

#function for drawing the world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile <= 2: #Logic for this changed since no tile is now a 3
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE) ) 

#create agv class                
class AGV(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # basic
        self.image = pygame.image.load('graphics/blue-circle.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(10, 10))
        self.rect = self.image.get_rect(center = (TILE_OFFSET,15*TILE_SIZE - TILE_OFFSET))
        
        # movement
        self.pos = self.rect.center
        self.speed = 1.5
        self.direction = pygame.math.Vector2(0,0)
        self.battery = 100 #Initial battery
        self.compare_battery = 0 #Used to check if the battery has decreased
        
        # path
        self.path = []
        self.collision_rects = []
        self.target_pickup_x, self.target_pickup_y = 0,0
        self.target_dropoff_x, self.target_dropoff_y = 0,0
        self.mode = 'picking up'

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
        self.battery -= .1 #Decrease battery over time
                
AGVs = []

#Find number of consumption points
def find_consumption(matrix):
    c = 0
    for i in range(ROWS):
        for j in range(MAX_COLS):
            if matrix[i][j] == 1 or matrix[i][j] == 2:
                c += 1
    return c

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










#GAME LOOP
setup = True #For grid
path_draw = False #For drawing path
run = True
while run:

    grid = Grid(matrix = world_data) #Get grid for pathfinding

    #background
    draw_bg()

    if setup:
        draw_grid()

    #if path_draw:
       # draw_path(path)  #paths arent really neccessary to draw
    draw_world() 

    #AGV
    if AGV: #If the AGVs are instantiated
        for AGV in AGVs:
            AGV.update()
            AGV.draw(screen)
            grid.cleanup()
            if AGV.sprite.mode == 'picking up': #If the AGV needs to pick up
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
                if AGV.sprite.get_coord()[0] == AGV.sprite.target_dropoff_x: #If the AGV is on the dropoff point
                    if AGV.sprite.battery < AGV.sprite.compare_battery: #If time has taken place
                        AGV.sprite.set_mode('picking up') #It now needs to pickup
                elif AGV.sprite.get_coord()[0] == AGV.sprite.target_pickup_x: #If the AGV is on the pickup point
                    if AGV.sprite.battery < AGV.sprite.compare_battery: #If time has taken place
                        AGV.sprite.set_mode('dropping off') #It now needs to dropoff
                    
            if AGV.sprite.mode == 'dropping off': #If the AGV needs to drop off
                start_x,start_y = AGV.sprite.get_coord()
                start = grid.node(start_x,start_y)
                end_x,end_y = AGV.sprite.target_dropoff_x, AGV.sprite.target_dropoff_y
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
           world_data[y][x] = 3 #Logic changed

    #EVENT HANDLER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_left = True 
            if event.key == pygame.K_RIGHT:
                scroll_right = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False 
            if event.key == pygame.K_RIGHT:
                scroll_right = False


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
                start_x,start_y = AGVs[0].sprite.get_coord()
                start = grid.node(start_x, start_y)
                mouse_pos = pygame.mouse.get_pos()
                end_x, end_y = AGVs[0].sprite.target_pickup_x, AGVs[0].sprite.target_pickup_y
                end = grid.node(end_x,end_y)
                path, runs = finder.find_path(start,end,grid)
                path_draw = True
                AGVs[0].sprite.set_path(path)

        #For testing       
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_u:
                start_x,start_y = AGVs[1].sprite.get_coord()
                start = grid.node(start_x, start_y)
                mouse_pos = pygame.mouse.get_pos()
                end_x, end_y = mouse_pos[0] //25, mouse_pos[1] //25
                end = grid.node(end_x,end_y)
                path, runs = finder.find_path(start,end,grid)
                #path_draw = True
                AGVs[1].sprite.set_path(path)

        #To create the AGVs 
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_a:
                number = find_consumption(world_data) // 2 #How many AGVs to make. Ideally, each AGV has their own unique drop off and pick up point
                for i in range(number):
                    AGVs.append(pygame.sprite.GroupSingle(AGV()))
                for i in range(len(AGVs)): #This assumes that each agv gets their own pickup and dropoff point
                    AGVs[i].sprite.set_dropoff(find_dropoff(world_data)[i][0], find_dropoff(world_data)[i][1])
                    AGVs[i].sprite.set_pickup(find_pickup(world_data)[i][0], find_pickup(world_data)[i][1])
                    

        #Test getting window position      
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_z:
                print(pygame.mouse.get_pos())
                row = pygame.mouse.get_pos()[1]//TILE_SIZE
                col = pygame.mouse.get_pos()[0]//TILE_SIZE
                print(row,col)
                 
    
    

    pygame.display.update()

#EXIT 
pygame.quit()
exit()