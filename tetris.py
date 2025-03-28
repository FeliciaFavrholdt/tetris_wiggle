import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
GRID_WIDTH = COLUMNS * BLOCK_SIZE
PREVIEW_WIDTH = 6 * BLOCK_SIZE
WINDOW_WIDTH = GRID_WIDTH + PREVIEW_WIDTH
WINDOW_HEIGHT = ROWS * BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # Cyan
    (0, 0, 255),    # Blue
    (255, 165, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (128, 0, 128),  # Purple
    (255, 0, 0),    # Red
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],                          # I
    [[1, 1], [1, 1]],                        # O
    [[0, 1, 0], [1, 1, 1]],                  # T
    [[1, 0, 0], [1, 1, 1]],                  # J
    [[0, 0, 1], [1, 1, 1]],                  # L
    [[0, 1, 1], [1, 1, 0]],                  # S
    [[1, 1, 0], [0, 1, 1]],                  # Z
]

# Create grid
def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

# Tetromino class
class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0
        self.wiggle_time = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def draw(self, window):
        self.wiggle_time += 0.1  # advance time to animate wiggle
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    wiggle_x = math.sin(self.wiggle_time + i * 0.5 + j * 0.3) * 3
                    rect = pygame.Rect(
                        (self.x + j) * BLOCK_SIZE + wiggle_x,
                        (self.y + i) * BLOCK_SIZE,
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )
                    pygame.draw.rect(window, self.color, rect, border_radius=6)
                    pygame.draw.rect(window, GRAY, rect, 1, border_radius=6)

# Valid space
def valid_space(piece, grid):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                x = piece.x + j
                y = piece.y + i
                if x < 0 or x >= COLUMNS or y >= ROWS:
                    return False
                if y >= 0 and grid[y][x] != BLACK:
                    return False
    return True

# Lock piece into grid
def add_to_locked(piece, locked):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                x = piece.x + j
                y = piece.y + i
                locked[(x, y)] = piece.color

# Clear filled rows
def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(COLUMNS):
                del locked[(x, y)]
            for key in sorted(locked.copy(), key=lambda k: k[1])[::-1]:
                x, row_y = key
                if row_y < y:
                    color = locked.pop((x, row_y))
                    locked[(x, row_y + 1)] = color
    return cleared

# Game over
def check_game_over(locked):
    for (x, y) in locked:
        if y < 1:
            return True
    return False

# Draw grid lines
def draw_grid(surface):
    for x in range(COLUMNS):
        for y in range(ROWS):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, GRAY, rect, 1)

# Draw next piece
def draw_next_piece(surface, piece):
    font = pygame.font.SysFont("arial", 20)
    label = font.render("Next:", True, WHITE)
    surface.blit(label, (GRID_WIDTH + 20, 20))

    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    GRID_WIDTH + 20 + j * BLOCK_SIZE,
                    50 + i * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                pygame.draw.rect(surface, piece.color, rect, border_radius=6)
                pygame.draw.rect(surface, GRAY, rect, 1, border_radius=6)

# Set up window
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")
FPS = 60
clock = pygame.time.Clock()

# Main game loop
def main():
    run = True
    fall_time = 0
    fall_speed = 0.5
    score = 0

    locked_positions = {}
    current_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(FPS) / 1000
        fall_time += dt
        current_piece.wiggle_time += dt * 8  # controls wiggle speed

        pygame.display.set_caption(f"Tetris | Score: {score}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        for _ in range(3):
                            current_piece.rotate()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            current_piece.x -= 1
            if not valid_space(current_piece, grid):
                current_piece.x += 1
            pygame.time.delay(100)
        elif keys[pygame.K_RIGHT]:
            current_piece.x += 1
            if not valid_space(current_piece, grid):
                current_piece.x -= 1
            pygame.time.delay(100)
        elif keys[pygame.K_DOWN]:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
            pygame.time.delay(50)

        # Move piece down automatically
        if fall_time >= fall_speed:
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                add_to_locked(current_piece, locked_positions)
                cleared = clear_rows(grid, locked_positions)
                score += cleared * 100
                current_piece = next_piece
                next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
                if not valid_space(current_piece, grid) or check_game_over(locked_positions):
                    run = False
            fall_time = 0

        # Draw everything
        WINDOW.fill(BLACK)
        draw_grid(WINDOW)
        current_piece.draw(WINDOW)
        draw_next_piece(WINDOW, next_piece)

        for (x, y), color in locked_positions.items():
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(WINDOW, color, rect, border_radius=6)
            pygame.draw.rect(WINDOW, GRAY, rect, 1, border_radius=6)

        pygame.display.update()

    # Game Over screen
    WINDOW.fill(BLACK)
    font = pygame.font.SysFont("arial", 36)
    text = font.render("GAME OVER", True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    WINDOW.blit(text, text_rect)
    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()
    sys.exit()

# Run game
if __name__ == "__main__":
    main()
