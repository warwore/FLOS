# Import necessary modules
import pygame
from sys import exit

# Initialize pygame
pygame.init()

# Define constants
WIDTH = 800
HEIGHT = 400
FPS = 60
FLEET_RECT = pygame.Rect(15, 15, 120, 100)
DELIVERY_RECT = pygame.Rect(30, 150, 120, 225)
FACTORY_MAP_RECT = pygame.Rect(150, 15, 630, 360)
AGV_START_POS = (150, 300)
AGV_SPEED = 0.2

# OBSTACLES = [pygame.Rect(200, 100, 50, 50), pygame.Rect(400, 200, 100, 75)]
# PICKUP_POINTS = [pygame.Rect(50, 50, 20, 20), pygame.Rect(500, 150, 30, 30)]
# DROP_OFF_POINTS = [pygame.Rect(700, 50, 20, 20), pygame.Rect(250, 300, 30, 30)]

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('AGV Simulator')

clock = pygame.time.Clock() #for setting fps

# Load fonts
font = pygame.font.Font('graphics/Arial.ttf', 15)

# Load images
agv_surf = pygame.image.load('graphics/agv.png').convert_alpha()
agv_surf = pygame.transform.scale(agv_surf, (20, 20))

# Define functions
def draw_bg():
    """Draws the background of the game window."""
    screen.fill('White')
    pygame.draw.rect(screen, 'Black', FLEET_RECT, 2)
    pygame.draw.rect(screen, 'Black', DELIVERY_RECT, 2)
    pygame.draw.rect(screen, 'Black', FACTORY_MAP_RECT, 2)

    # Draw obstacles
    # for obstacle in OBSTACLES:
    #     pygame.draw.rect(screen, 'Red', obstacle)

    # # Draw pickup points
    # for pickup_point in PICKUP_POINTS:
    #     pygame.draw.rect(screen, 'Green', pickup_point)

    # # Draw drop off points
    # for drop_off_point in DROP_OFF_POINTS:
    #     pygame.draw.rect(screen, 'Blue', drop_off_point)


def draw_text():
    """Draws the text on the game window."""
    text_fleet_surf = font.render('Fleet', False, 'Black')
    text_fleet_rect = text_fleet_surf.get_rect(topleft=(55, 0))
    screen.blit(text_fleet_surf, text_fleet_rect)

    text_delivery_surf = font.render('Delivery', False, 'Black')
    text_delivery_rect = text_delivery_surf.get_rect(topleft=(45, 135))
    screen.blit(text_delivery_surf, text_delivery_rect)

    text_factory_map_surf = font.render('Factory Map', False, 'Black')
    text_factory_map_rect = text_factory_map_surf.get_rect(topleft=(400, 0))
    screen.blit(text_factory_map_surf, text_factory_map_rect)

def draw_agv():
    """Draws the AGV on the game window."""
    screen.blit(agv_surf, agv_rect)

def autocorrect(lines):
    """Autocorrects the lines to make them straight."""
    corrected = []
    if done_line:
        corrected.append(lines[0])
        for i in range(0, len(lines), 2):
            if abs(lines[i][0] - lines[i + 1][0]) > abs(lines[i][1] - lines[i + 1][1]):
                corrected.append((lines[i + 1][0], lines[i][1]))
                corrected.append((lines[i + 1][0], lines[i][1]))
            else:
                corrected.append((lines[i][0], lines[i + 1][1]))
                corrected.append((lines[i][0], lines[i + 1][1]))
        del corrected[len(corrected) - 1]
    return corrected

def draw_lines(x):
    """Draws the lines on the game window."""
    if done_line:
        for i in range(0, len(x), 2):
            pygame.draw.line(screen, 'Gold', x[i], x[i + 1])


# Initialize variables
lines = []
start = AGV_START_POS
done_line = False
current_path_index = 0
agv_rect = agv_surf.get_rect(topleft=AGV_START_POS)
moving = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                end = pygame.mouse.get_pos()
                lines.append(start)
                lines.append(end)
                start = end
                print('Line saved')
                print('Current coordinates saved:', lines)

            if event.key == pygame.K_d:
                print('Now drawing route')
                done_line = True

            if event.key == pygame.K_r:
                current_path_index = 0
                agv_rect.topleft = agv_start_pos
                moving = False

    draw_bg()
    draw_text()

    if done_line:
        corrected = autocorrect(lines)
        if current_path_index < len(corrected) - 1:
            current_path_index += AGV_SPEED
            moving = True
        else:
            done_line = False
            current_path_index = 0
            moving = False

    if moving:
        agv_rect.topleft = corrected[int(current_path_index)]
        draw_lines(corrected)

    draw_agv()

    pygame.display.update()
    clock.tick(FPS)