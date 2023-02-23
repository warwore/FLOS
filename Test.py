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

def draw_obstacles():
    """Draws the obstacles on the game window."""
    for obstacle in obstacles:
        pygame.draw.rect(screen, 'Red', obstacle)

def draw_dropoff():
    """Draws the dropoff points on the game window."""
    for dropoff in dropoffs:
        pygame.draw.circle(screen, 'Blue', dropoff, 5)

def draw_pickup():
    """Draws the pickup points on the game window."""
    for pickup in pickups:
        pygame.draw.circle(screen, 'Green', pickup, 5)

def check_collision():
    """Checks for collision between the AGV and obstacles."""
    for obstacle in obstacles:
        if agv_rect.colliderect(obstacle):
            return True
    return False

def check_dropoff():
    """Checks if AGV is at a dropoff point."""
    for dropoff in dropoffs:
        if agv_rect.collidepoint(dropoff):
            return True
    return False

def check_pickup():
    """Checks if AGV is at a pickup point."""
    for pickup in pickups:
        if agv_rect.collidepoint(pickup):
            return True
    return False

def update_delivery_status():
    """Updates the delivery status."""
    global delivery_status
    if check_dropoff():
        delivery_status = 'Delivered'
    elif check_pickup():
        delivery_status = 'Picked Up'
    else:
        delivery_status = 'In Transit'

def draw_delivery_status():
    """Draws the delivery status on the game window."""
    text_delivery_status_surf = font.render(delivery_status, False, 'Black')
    text_delivery_status_rect = text_delivery_status_surf.get_rect(midleft=(15, 365))
    screen.blit(text_delivery_status_surf, text_delivery_status_rect)

