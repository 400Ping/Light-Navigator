import pygame
import sys
import time

# Constants and Configuration
SCREEN_SIZE = 850
GRID_SIZE = 30
DOT_RADIUS = 1
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
ROUND_DURATION = 0.5
ENGINE_LIT_LIMIT = 3  # Set this to the count limit for the engine

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (120, 120, 120)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Lit Game")

# Global Variables
stop_lighting = False   # for detect control-c signal
is_win = False
engine_pos = (GRID_SIZE // 2, GRID_SIZE // 2) # place at center
elements = {}   # a map storing position(x, y) to a element (engine, box, hollow, lit...)
lit_rounds = {}
engine_lit_rounds = 0

def draw_grid():
    screen.fill(BLACK)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            center = (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
            if (x, y) in elements:
                if elements[(x, y)] == 'engine':
                    pygame.draw.circle(screen, WHITE, center, CELL_SIZE // 4)
                    pygame.draw.circle(screen, BLACK, center, DOT_RADIUS * 3)
                elif elements[(x, y)] == 'hollow':
                    pygame.draw.circle(screen, LIGHT_GRAY, center, CELL_SIZE // 8)
                elif elements[(x, y)] == 'lit':
                    pygame.draw.circle(screen, WHITE, center, CELL_SIZE // 6)
                elif isinstance(elements[(x, y)], dict):  # it's a box
                    pygame.draw.rect(screen, LIGHT_GRAY, (center[0] - CELL_SIZE // 4, center[1] - CELL_SIZE // 4, CELL_SIZE // 2, CELL_SIZE // 2), 1)
                    for side, lit in elements[(x, y)].items():
                        if lit:
                            draw_lit_side(center, side)
            else:
                pygame.draw.circle(screen, LIGHT_GRAY, center, DOT_RADIUS)

def draw_lit_side(center, side):
    if side == 'top':
        pygame.draw.line(screen, WHITE, (center[0] - CELL_SIZE // 4, center[1] + CELL_SIZE // 4), (center[0] + CELL_SIZE // 4, center[1] + CELL_SIZE // 4), 3)
    elif side == 'bottom':
        pygame.draw.line(screen, WHITE, (center[0] - CELL_SIZE // 4, center[1] - CELL_SIZE // 4), (center[0] + CELL_SIZE // 4, center[1] - CELL_SIZE // 4), 3)
    elif side == 'left':
        pygame.draw.line(screen, WHITE, (center[0] - CELL_SIZE // 4, center[1] - CELL_SIZE // 4), (center[0] - CELL_SIZE // 4, center[1] + CELL_SIZE // 4), 3)
    elif side == 'right':
        pygame.draw.line(screen, WHITE, (center[0] + CELL_SIZE // 4, center[1] - CELL_SIZE // 4), (center[0] + CELL_SIZE // 4, center[1] + CELL_SIZE // 4), 3)

def light_up_surroundings():
    global stop_lighting, is_win, engine_lit_rounds

    lit_nodes = {(engine_pos[0], engine_pos[1]): None}
    new_lit_nodes = True

    while new_lit_nodes and not stop_lighting:
        new_lit_nodes = False
        current_lit_nodes = list(lit_nodes.keys())
        print("Current lit:", current_lit_nodes)
        
        for event in pygame.event.get():
            handle_event(event)

        for x, y in current_lit_nodes:
            directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (nx, ny) != lit_nodes[(x, y)] and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if elements.get((nx, ny)) == 'hollow':
                        elements[(nx, ny)] = 'lit'
                        lit_nodes[(nx, ny)] = (x, y)
                        new_lit_nodes = True
                    elif isinstance(elements.get((nx, ny)), dict):  # it's a box
                        side = get_box_side(dx, dy)
                        if side and not elements[(nx, ny)][side]:
                            elements[(nx, ny)][side] = True
                            new_lit_nodes = True
                            if all(elements[(nx, ny)].values()):
                                print("You win!")
                                is_win = True
                                stop_lighting = True

        time.sleep(ROUND_DURATION)
        engine_lit_rounds += 1

        for x, y in current_lit_nodes:
            if elements[(x, y)] == 'lit':
                elements[(x, y)] = 'hollow'
                lit_nodes.pop((x, y))

        if (engine_pos[0], engine_pos[1]) in lit_nodes:
            lit_nodes.pop((engine_pos[0], engine_pos[1]))

        # if ENGINE_LIT_LIMIT != 0:
        if True:
            if engine_lit_rounds >= ENGINE_LIT_LIMIT:
                lit_nodes[(engine_pos[0], engine_pos[1])] = None
                engine_lit_rounds = 0

        draw_grid()
        pygame.display.flip()

        if not is_win:
            reset_box_sides()

def get_box_side(dx, dy):
    if dx == 0 and dy == -1:
        return 'top'
    elif dx == 0 and dy == 1:
        return 'bottom'
    elif dx == -1 and dy == 0:
        return 'right'
    elif dx == 1 and dy == 0:
        return 'left'
    return ''

def handle_event(event):
    global stop_lighting
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
            stop_lighting = True
            reset_lit_elements()
            draw_grid()
            pygame.display.flip()

def reset_lit_elements():
    for key in elements:
        if elements[key] == 'lit':
            elements[key] = 'hollow'
        elif isinstance(elements[key], dict):
            for side in elements[key]:
                elements[key][side] = False

def reset_box_sides():
    for (bx, by) in elements:
        if isinstance(elements[(bx, by)], dict):  # it's a box
            for side in elements[(bx, by)]:
                elements[(bx, by)][side] = False

def add_box(x, y):
    elements[(x, y)] = {'top': False, 'bottom': False, 'left': False, 'right': False}

def main():
    global stop_lighting, is_win

    clock = pygame.time.Clock()
    play_button = pygame.Rect(SCREEN_SIZE // 2 - 50, SCREEN_SIZE - 60, 100, 50)

    elements[engine_pos] = 'engine'

    while True:
        screen.fill(BLACK)
        draw_grid()
        pygame.draw.rect(screen, WHITE, play_button)
        font = pygame.font.SysFont(None, 24)
        play_text = font.render('Play', True, BLACK)
        screen.blit(play_text, play_text.get_rect(center=play_button.center))

        if is_win:
            win_text = font.render('Win', True, WHITE)
            screen.blit(win_text, win_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 4)))

        for event in pygame.event.get():
            handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(event, play_button)

        pygame.display.flip()
        clock.tick(60)

def handle_mouse_click(event, play_button):
    global stop_lighting, is_win

    if play_button.collidepoint(event.pos):
        reset_lit_elements()
        stop_lighting = False
        is_win = False
        light_up_surroundings()
    else:
        mx, my = event.pos
        x = mx // CELL_SIZE
        y = my // CELL_SIZE

        if (x, y) not in elements and 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                add_box(x, y)
            else:
                elements[(x, y)] = 'hollow'
        elif (x, y) in elements:
            elements.pop((x, y))

if __name__ == "__main__":
    main()
