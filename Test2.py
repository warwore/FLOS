import pygame
import button
import csv 

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
    r = [-1] * MAX_COLS
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
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE) ) 

#function for drawing agv
agv_start = (16*25,25) 
def draw_agv():
    agv_rect = pygame.draw.circle(screen, (0,0,255), agv_start, 3)
                
def find_pickup(matrix):
    c = 0
    coords = []
    for i in range(ROWS):
        for j in range(MAX_COLS):
            if matrix[i][j] == 1:
                c += 1
                coords.append((i,j))
    return coords, c

def find_dropoff(matrix):
    c = 0
    coords = []
    for i in range(ROWS):
        for j in range(MAX_COLS):
            if matrix[i][j] == 2:
                c += 1
                coords.append((i,j))
    return coords, c        
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
run = True
while run:

    #background
    draw_bg()
    draw_grid()
    draw_world()

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
           world_data[y][x] = - 1

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
                 
        #Test function       
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_t:
                number, pickup = find_pickup(world_data)
                print(number)
                print(pickup)
        
        #Test function       
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_y:
                number, pickup = find_dropoff(world_data)
                print(number)
                print(pickup)
                
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