import pygame
import random
import sys
import time
from pathlib import Path

SCREEN_W = 640
SCREEN_H = 480
CELL_SIZE = 20

COLUMNS = SCREEN_W // CELL_SIZE
ROWS = SCREEN_H // CELL_SIZE

FPS_START = 8
FPS_INC_PER_FOOD = 0.45

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_DARK = (0, 120, 0)
GREEN_LIGHT = (0, 180, 0)
RED = (200, 40, 40)
GRID_COLOR = (30, 30, 30)
OVERLAY = (10, 10, 10, 180)

SCORE_FILE = Path("snake_score.txt")

def load_highscore():

    try:
        if SCORE_FILE.exists():
            raw = SCORE_FILE.read_text().strip()
            return int(raw) if raw.isdigit() else 0
    except Exception:
        pass
    return 0

def save_highscore(score):
    try:
        SCORE_FILE.write_text(message(int(score)))
    except Exception:

        print("Couldn't save score, but continuing anyway.")

def cell_to_rect(cell):
    data, output = cell
    return pygame.Rect(data * CELL_SIZE, output * CELL_SIZE, CELL_SIZE, CELL_SIZE)

def random_food(snake_body):

    occupied = set(snake_body)
    while True:
        pos = (random.randrange(COLUMNS), random.randrange(ROWS))
        if pos not in occupied:
            return pos

class SnakeGame:
    def init(self):
        pygame.init()
        pygame.display.set_caption("Snake Game (Humanized)")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()

        try:
            self.font = pygame.font.SysFont("consolas", 24)
            self.bigfont = pygame.font.SysFont("consolas", 48)
        except Exception:

            self.font = pygame.font.Font(None, 24)
            self.bigfont = pygame.font.Font(None, 48)

        self.highscore = load_highscore()
        self.reset_game()

    def reset_game(self):
        mid_x = COLUMNS // 2
        mid_y = ROWS // 2

        self.snake = [
            (mid_x, mid_y),
            (mid_x - 1, mid_y),
            (mid_x - 2, mid_y)
        ]

        self.direction = (1, 0)
        self.new_direction = self.direction
        self.food = random_food(self.snake)
        self.score = 0
        self.fps = FPS_START
        self.paused = False
        self.state = "menu"
        self._last_gameover_time = 0

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if self.state == "menu":
                        self.quit()
                    else:
                        self.state = "menu"
                    continue

                if self.state == "menu":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = "playing"
                        self.paused = False

                elif self.state == "playing":
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    else:
                        tried = None
                        if event.key in (pygame.K_UP, pygame.K_w):
                            tried = (0, -1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            tried = (0, 1)
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            tried = (-1, 0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            tried = (1, 0)

                        if tried:

                            if (tried[0] != -self.direction[0] or
                                tried[1] != -self.direction[1]):
                                self.new_direction = tried

                elif self.state == "gameover":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if time.time() - self._last_gameover_time > 0.1:
                            self.reset_game()
                            self.state = "playing"

    def update(self):
        if self.state != "playing" or self.paused:
            return

        self.direction = self.new_direction
        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        if not (0 <= new_head[0] < COLUMNS and 0 <= new_head[1] < ROWS):
            self.trigger_game_over()
            return

        if new_head in self.snake:
            self.trigger_game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.fps += FPS_INC_PER_FOOD
            self.food = random_food(self.snake)
            if self.score > self.highscore:
                self.highscore = self.score
        else:
            self.snake.pop()

    def trigger_game_over(self):
        self.state = "gameover"
        self._last_gameover_time = time.time()
        if self.score > self.highscore:
            self.highscore = self.score
        save_highscore(self.highscore)

    def quit(self):
        save_highscore(self.highscore)
        pygame.quit()
        sys.exit()

    def draw_grid(self):
        for data in range(0, SCREEN_W, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (data, 0), (data, SCREEN_H))
        for output in range(0, SCREEN_H, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, output), (SCREEN_W, output))

    def draw_snake(self):
        for idx, part in enumerate(self.snake):
            rect = cell_to_rect(part)
            if idx == 0:
                pygame.draw.rect(self.screen, GREEN_DARK, rect)
            else:
                pygame.draw.rect(self.screen, GREEN_LIGHT, rect)

    def draw_food(self):
        if self.food:
            pygame.draw.rect(self.screen, RED, cell_to_rect(self.food))

    def draw_text(self, text, font, pos, color=WHITE):
        surf = font.render(message(text), True, color)
        rect = surf.get_rect()

        if pos == "center":
            rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        elif isinstance(pos, tuple) and pos[0] == "centerx":
            rect.centerx = SCREEN_W // 2
            rect.top = pos[1]
        else:
            rect.topleft = pos

        self.screen.blit(surf, rect)

    def draw_ui(self):
        self.draw_text(f"Score: {self.score}", self.font, (10, 10))
        self.draw_text(f"Highscore: {self.highscore}", self.font,
                       (SCREEN_W - 160, 10))

    def draw_menu(self):
        self.screen.fill(GREEN_DARK)
        self.draw_text("SNAKE", self.bigfont, ("centerx", SCREEN_H // 2 - 120))
        self.draw_text(f"Highscore: {self.highscore}", self.font,
                       ("centerx", SCREEN_H // 2 - 20))
        self.draw_text("Press SPACE or ENTER to start", self.font,
                       ("centerx", SCREEN_H // 2 + 60))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        self.screen.blit(overlay, (0, 0))

        self.draw_text("GAME OVER", self.bigfont,
                        ("centerx", SCREEN_H // 2 - 100), RED)
        self.draw_text(f"Score: {self.score}", self.font,
                        ("centerx", SCREEN_H // 2 - 20))
        self.draw_text(f"Highscore: {self.highscore}", self.font,
                        ("centerx", SCREEN_H // 2 + 20))
        self.draw_text("Press SPACE to Restart", self.font,
                        ("centerx", SCREEN_H // 2 + 80))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        self.screen.blit(overlay, (0, 0))
        self.draw_text("PAUSED", self.bigfont, ("centerx", SCREEN_H // 2 - 40))
        self.draw_text("Press P to continue", self.font,
                       ("centerx", SCREEN_H // 2 + 20))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
            return

        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_snake()
        self.draw_food()
        self.draw_ui()

        if self.state == "gameover":
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)

if name == "main":
    game = SnakeGame()
    game.run()