import pygame
import sys
import random
import math

# Initialize the game engine and configure display settings
pygame.init()
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
GRID_WIDTH = COLUMNS * BLOCK_SIZE
PREVIEW_WIDTH = 6 * BLOCK_SIZE
WINDOW_WIDTH = GRID_WIDTH + PREVIEW_WIDTH
WINDOW_HEIGHT = ROWS * BLOCK_SIZE

# Color palette configuration
BACKGROUND_COLOR = (236, 231, 236)
GRID_COLOR = (250, 249, 235)
TEXT_COLOR = (40, 40, 40)

# Shape color mapping and structure
SHAPE_COLORS = {
    "I": (166, 196, 250), "O": (231, 222, 95), "T": (113, 147, 200),
    "J": (182, 105, 132), "L": (249, 184, 113), "S": (125, 178, 102), "Z": (244, 168, 198)
}

SHAPES = {
    "I": [[1, 1, 1, 1]], "O": [[1, 1], [1, 1]], "T": [[0, 1, 0], [1, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]], "L": [[0, 0, 1], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]], "Z": [[1, 1, 0], [0, 1, 1]]
}

# Display setup
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")
FPS = 60
clock = pygame.time.Clock()

# Constructs the playing grid from locked block positions
def create_grid(locked_positions={}):
    grid = [[BACKGROUND_COLOR for _ in range(COLUMNS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLUMNS:
            grid[y][x] = color
    return grid

# Represents a falling shape in the game
class Shape:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.shape = SHAPES[shape_key]
        self.color = SHAPE_COLORS[shape_key]
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.wiggle_time = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def draw(self, window):
        self.wiggle_time += 0.1
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    wiggle_x = math.sin(self.wiggle_time + i * 0.5 + j * 0.3) * 3
                    rect = pygame.Rect((self.x + j) * BLOCK_SIZE + wiggle_x, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(window, self.color, rect, border_radius=6)
                    pygame.draw.rect(window, GRID_COLOR, rect, 1, border_radius=6)

# Checks if the current shape can legally occupy its position
def valid_space(shape, grid):
    for i, row in enumerate(shape.shape):
        for j, cell in enumerate(row):
            if cell:
                x = shape.x + j
                y = shape.y + i
                if x < 0 or x >= COLUMNS or y >= ROWS:
                    return False
                if y >= 0 and grid[y][x] != BACKGROUND_COLOR:
                    return False
    return True

# Locks a shape's blocks into the grid when it lands
def add_to_locked(shape, locked):
    for i, row in enumerate(shape.shape):
        for j, cell in enumerate(row):
            if cell:
                x = shape.x + j
                y = shape.y + i
                if y >= 0:
                    locked[(x, y)] = shape.color

# Clears completed rows and shifts down remaining blocks
def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BACKGROUND_COLOR not in grid[y]:
            cleared += 1
            for x in range(COLUMNS):
                del locked[(x, y)]
            for key in sorted(list(locked.keys()), key=lambda k: k[1])[::-1]:
                x, row_y = key
                if row_y < y:
                    locked[(x, row_y + 1)] = locked.pop((x, row_y))
    return cleared

# Draws the grid lines over the board
def draw_grid(surface):
    for x in range(COLUMNS):
        for y in range(ROWS):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)

# Displays the upcoming shape and control instructions
def draw_controls_and_next_piece(surface, shape):
    font = pygame.font.SysFont("arial", 20)
    title_font = pygame.font.SysFont("arial", 24, bold=True)
    surface.blit(title_font.render("Next Piece", True, TEXT_COLOR), (GRID_WIDTH + 20, 20))

    for i, row in enumerate(shape.shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(GRID_WIDTH + 20 + j * BLOCK_SIZE, 60 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, shape.color, rect, border_radius=6)
                pygame.draw.rect(surface, GRID_COLOR, rect, 1, border_radius=6)

    surface.blit(title_font.render("Controls", True, TEXT_COLOR), (GRID_WIDTH + 20, 180))
    controls = [
        ("← / →", "Move"), ("↑", "Rotate"), ("↓", "Down"),
        ("SPACE", "Drop"), ("P", "Pause"), ("R", "Restart"), ("Q", "Quit")
    ]
    for i, (key, action) in enumerate(controls):
        label = font.render(f"{key:<6} - {action}", True, TEXT_COLOR)
        surface.blit(label, (GRID_WIDTH + 20, 220 + i * 28))

# Main menu interface with difficulty selection
def main_menu():
    WINDOW.fill(BACKGROUND_COLOR)
    title_font = pygame.font.SysFont("arial", 36, bold=True)
    prompt_font = pygame.font.SysFont("arial", 24)
    title_text = title_font.render("TETRIS", True, TEXT_COLOR)
    instruction_text = prompt_font.render("Choose a level to start:", True, TEXT_COLOR)
    WINDOW.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, 150)))
    WINDOW.blit(instruction_text, instruction_text.get_rect(center=(WINDOW_WIDTH // 2, 220)))

    level_font = pygame.font.SysFont("arial", 22)
    level_info = ["1 - Easy", "2 - Medium", "3 - Hard"]
    for i, line in enumerate(level_info):
        label = level_font.render(line, True, TEXT_COLOR)
        WINDOW.blit(label, label.get_rect(center=(WINDOW_WIDTH // 2, 270 + i * 30)))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 0.7
                elif event.key == pygame.K_2:
                    return 0.4
                elif event.key == pygame.K_3:
                    return 0.2

# Main game loop and mechanics
def main_game(fall_speed):
    fall_time, score = 0, 0
    is_paused = False
    locked_positions = {}
    current_shape = Shape(random.choice(list(SHAPES.keys())))
    next_shape = Shape(random.choice(list(SHAPES.keys())))
    game_over = False

    while True:
        grid = create_grid(locked_positions)
        dt = clock.tick(FPS) / 1000
        fall_time += dt
        current_shape.wiggle_time += dt * 8

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_paused = not is_paused
                if game_over and event.key == pygame.K_r:
                    return
                if not is_paused and not game_over:
                    if event.key == pygame.K_UP:
                        current_shape.rotate()
                        if not valid_space(current_shape, grid):
                            for _ in range(3):
                                current_shape.rotate()
                    if event.key == pygame.K_SPACE:
                        while valid_space(current_shape, grid):
                            current_shape.y += 1
                        current_shape.y -= 1

        if is_paused:
            WINDOW.fill(BACKGROUND_COLOR)
            font = pygame.font.SysFont("arial", 36)
            pause_text = font.render("PAUSED", True, TEXT_COLOR)
            WINDOW.blit(pause_text, pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
            pygame.display.update()
            continue

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                current_shape.x -= 1
                if not valid_space(current_shape, grid):
                    current_shape.x += 1
                pygame.time.delay(100)
            elif keys[pygame.K_RIGHT]:
                current_shape.x += 1
                if not valid_space(current_shape, grid):
                    current_shape.x -= 1
                pygame.time.delay(100)
            elif keys[pygame.K_DOWN]:
                current_shape.y += 1
                if not valid_space(current_shape, grid):
                    current_shape.y -= 1
                pygame.time.delay(50)

            if fall_time >= fall_speed:
                current_shape.y += 1
                if not valid_space(current_shape, grid):
                    current_shape.y -= 1
                    add_to_locked(current_shape, locked_positions)
                    cleared = clear_rows(grid, locked_positions)
                    score += cleared
                    current_shape = next_shape
                    next_shape = Shape(random.choice(list(SHAPES.keys())))
                    if not valid_space(current_shape, grid):
                        game_over = True
                fall_time = 0

        pygame.display.set_caption(f"Tetris | Score: {score}")
        WINDOW.fill(BACKGROUND_COLOR)
        draw_grid(WINDOW)
        current_shape.draw(WINDOW)
        draw_controls_and_next_piece(WINDOW, next_shape)
        font = pygame.font.SysFont("arial", 20)
        score_label = font.render(f"Score: {score}", True, TEXT_COLOR)
        WINDOW.blit(score_label, (GRID_WIDTH + 20, 440))

        for (x, y), color in locked_positions.items():
            if y >= 0:
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(WINDOW, color, rect, border_radius=6)
                pygame.draw.rect(WINDOW, GRID_COLOR, rect, 1, border_radius=6)

        if game_over:
            font_big = pygame.font.SysFont("arial", 30)
            font_small = pygame.font.SysFont("arial", 20)
            over_text = font_big.render("GAME OVER", True, TEXT_COLOR)
            restart_text = font_small.render("Press R to Restart", True, TEXT_COLOR)
            center_x = GRID_WIDTH + PREVIEW_WIDTH // 2
            WINDOW.blit(over_text, over_text.get_rect(center=(center_x, 500)))
            WINDOW.blit(restart_text, restart_text.get_rect(center=(center_x, 540)))

        pygame.display.update()

# Entry point
if __name__ == "__main__":
    while True:
        fall_speed = main_menu()
        main_game(fall_speed)