import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

#Mouse
LMB = 1
RMB = 3

# Setup the Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Logistics Management Simulator")

# Fonts
font = pygame.font.Font(None, 36)

# Clock for FPS
clock = pygame.time.Clock()

# Game States
game_state = "playing"
selected_facility = None
selected_source = None
selected_destination = None

# Facility Types
FACILITIES = {
    "warehouse": {"color": GREEN, "capacity": 50, "level": 1},
    "factory": {"color": BLUE, "capacity": 30, "level": 1, "production": {"wood": 1}},
    "depot": {"color": RED, "capacity": 20, "level": 1},
}

# Vehicles
vehicles = []
VEHICLE_SPEED = 2

# Map Dimensions (Grid)
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Map Data (Grid)
grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

# Resources
resources = {"wood": 0, "metal": 0, "fuel": 0}
resource_production = {"wood": 1, "metal": 0, "fuel": 0}

# Functions
def draw_grid():
    """Draw the grid for the map."""
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)

def draw_facilities():
    """Render facilities on the map."""
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if grid[x][y] is not None:
                facility = grid[x][y]
                pygame.draw.rect(
                    screen,
                    FACILITIES[facility]["color"],
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                )

def place_facility(facility_type, grid_x, grid_y):
    """Place a facility on the grid."""
    if grid[grid_x][grid_y] is None:
        grid[grid_x][grid_y] = facility_type
        print(f"Placed {facility_type} at ({grid_x}, {grid_y})")

def draw_vehicles():
    """Draw vehicles on the screen."""
    for vehicle in vehicles:
        pygame.draw.rect(
            screen, YELLOW, (vehicle["x"], vehicle["y"], TILE_SIZE // 2, TILE_SIZE // 2)
        )

def update_vehicles():
    """Update vehicle positions."""
    for vehicle in vehicles:
        if vehicle["route"]:
            target_x, target_y = vehicle["route"][0]
            target_x *= TILE_SIZE
            target_y *= TILE_SIZE
            dx, dy = target_x - vehicle["x"], target_y - vehicle["y"]

            # Move vehicle toward the target
            if abs(dx) > VEHICLE_SPEED:
                vehicle["x"] += VEHICLE_SPEED if dx > 0 else -VEHICLE_SPEED
            elif abs(dy) > VEHICLE_SPEED:
                vehicle["y"] += VEHICLE_SPEED if dy > 0 else -VEHICLE_SPEED
            else:
                # Reached the target
                vehicle["route"].pop(0)
                if not vehicle["route"]:
                    vehicle["task"] = None  # Task completed

def assign_vehicle(source, destination):
    """Assign a vehicle to transport resources between two facilities."""
    for vehicle in vehicles:
        if vehicle["task"] is None:
            vehicle["route"] = [source, destination]
            vehicle["task"] = "transport"
            print(f"Vehicle assigned from {source} to {destination}")
            break

def upgrade_facility(grid_x, grid_y):
    """Upgrade a facility to increase its capacity."""
    facility = grid[grid_x][grid_y]
    if facility:
        FACILITIES[facility]["level"] += 1
        FACILITIES[facility]["capacity"] += 10
        print(f"{facility} at ({grid_x}, {grid_y}) upgraded to level {FACILITIES[facility]['level']}!")

def update_resources():
    """Update resources based on facility production."""
    global resources
    for facility_type, data in FACILITIES.items():
        if "production" in data:
            for resource, amount in data["production"].items():
                resources[resource] += amount * data["level"]

def draw_ui():
    """Draw the UI for resources."""
    pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
    ui_text = f"Wood: {resources['wood']}  |  Metal: {resources['metal']}  |  Fuel: {resources['fuel']}"
    text = font.render(ui_text, True, BLACK)
    screen.blit(text, (10, SCREEN_HEIGHT - 80))

# Main Game Loop
def game_loop():
    global selected_facility, selected_source, selected_destination

    # Add one vehicle at start
    vehicles.append({"x": 0, "y": 0, "route": [], "task": None})

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            # Mouse Click for Placing Facility or Upgrading
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == LMB:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x, grid_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
                    if selected_facility is not None:
                        place_facility(selected_facility, grid_x, grid_y)
                    elif event.button == 3:  # Right-click to upgrade
                        upgrade_facility(grid_x, grid_y)

            # Key Press to Select Facility or Assign Vehicle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    selected_facility = "warehouse"
                elif event.key == pygame.K_f:
                    selected_facility = "factory"
                elif event.key == pygame.K_d:
                    selected_facility = "depot"
                elif event.key == pygame.K_v:
                    if selected_source and selected_destination:
                        assign_vehicle(selected_source, selected_destination)
                        selected_source, selected_destination = None, None

        # Update resources and vehicles
        if pygame.time.get_ticks() % 1000 < 16:  # ~60 FPS
            update_resources()
        update_vehicles()

        # Draw game elements
        draw_grid()
        draw_facilities()
        draw_vehicles()
        draw_ui()

        pygame.display.flip()
        clock.tick(60)

# Run the Game
game_loop()
