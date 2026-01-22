import pygame
from pygame.locals import *
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 800, 400
FPS = 60
GROUND_HEIGHT = 80
GRAVITY = 0.8
JUMP_VELOCITY = -15

OBSTACLE_SPAWN_MIN = 900
OBSTACLE_SPAWN_MAX = 1600

SPEED_START = 6
SPEED_ACCEL = 0.0012

SPRITE_SCALE = 3

BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
SKY = (235, 245, 255)

# ================= INIT =================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hugo's Adventure")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 48)

# ================= ASSETS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sprite_sheet = pygame.image.load(
    os.path.join(BASE_DIR, "HugoAdventure.png")
).convert_alpha()

mouse_sheet = pygame.image.load(
    os.path.join(BASE_DIR, "pixel art pygame.png")
).convert_alpha()

STATS_FILE = os.path.join(BASE_DIR, "ranking.csv")

def load_ranking():
    if not os.path.exists(STATS_FILE):
        return []
    ranking = []
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "," in line:
                name, score = line.strip().split(",")
                ranking.append((name, int(score)))
    ranking.sort(key=lambda x: x[1], reverse=True)
    return ranking

def save_ranking(name, score):
    ranking = load_ranking()
    ranking.append((name, score))
    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        for n, s in ranking:
            f.write(f"{n},{s}\n")

class Hugo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        COLS = 2
        ROWS = 2

        FRAME_W = sprite_sheet.get_width() // COLS
        FRAME_H = sprite_sheet.get_height() // ROWS

        self.frames = []
        positions = [(0, 0), (1, 0), (0, 1)]

        for col, row in positions:
            img = sprite_sheet.subsurface(
                col * FRAME_W, row * FRAME_H,
                FRAME_W, FRAME_H
            )
            img = pygame.transform.scale(
                img,
                (FRAME_W * SPRITE_SCALE, FRAME_H * SPRITE_SCALE)
            )
            self.frames.append(img)

        self.jump_image = pygame.transform.scale(
            sprite_sheet.subsurface(
                FRAME_W, FRAME_H,
                FRAME_W, FRAME_H
            ),
            (FRAME_W * SPRITE_SCALE, FRAME_H * SPRITE_SCALE)
        )

        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vel_y = 0
        self.on_ground = False
        self.anim_time = 0
        self.anim_speed = 120
        self.index = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False
            self.image = self.jump_image

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        ground_y = HEIGHT - GROUND_HEIGHT

        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0
            self.on_ground = True

            self.anim_time += clock.get_time()
            if self.anim_time >= self.anim_speed:
                self.anim_time = 0
                self.index = (self.index + 1) % len(self.frames)
                self.image = self.frames[self.index]
        else:
            self.image = self.jump_image

    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Obstacle:
    def __init__(self, x):
        self.width = 40
        self.height = 60
        self.rect = pygame.Rect(
            x,
            HEIGHT - GROUND_HEIGHT - self.height,
            self.width,
            self.height
        )
        self.passed = False

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, surf):
        pygame.draw.rect(surf, (200, 60, 60), self.rect)

class MouseObstacle:
    def __init__(self, x):
        COLS = 4
        ROWS = 4

        FRAME_W = mouse_sheet.get_width() // COLS
        FRAME_H = mouse_sheet.get_height() // ROWS

        col, row = 3, 3

        self.image = pygame.transform.scale(
            mouse_sheet.subsurface(
                col * FRAME_W,
                row * FRAME_H,
                FRAME_W,
                FRAME_H
            ),
            (FRAME_W * 1.5, FRAME_H * 1.5)
        )

        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - GROUND_HEIGHT + 12
        self.rect.x = x

        self.hitbox = self.rect.inflate(
            -self.rect.width * 0.6,
            -self.rect.height * 0.6
        )

        self.passed = False

    def update(self, speed):
        self.rect.x -= speed
        self.hitbox.center = self.rect.center

    def draw(self, surf):
        surf.blit(self.image, self.rect)

def draw_ground(offset):
    pygame.draw.rect(
        screen, BLACK,
        (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
    )

    step = 40
    for i in range(-step, WIDTH + step, step):
        x = i + int(offset % step)
        pygame.draw.line(
            screen, GRAY,
            (x, HEIGHT - GROUND_HEIGHT + 10),
            (x + 20, HEIGHT - GROUND_HEIGHT + 10), 2
        )

def game_loop():
    hugo = Hugo(80, HEIGHT - GROUND_HEIGHT - 120)
    obstacles = []

    distance_to_next = random.randint(
        OBSTACLE_SPAWN_MIN, OBSTACLE_SPAWN_MAX
    )

    speed = SPEED_START
    ground_offset = 0
    score = 0
    game_over = False

    player_name = ""
    typing_name = True

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if typing_name:
                if event.type == KEYDOWN:
                    if event.key == K_RETURN and player_name:
                        typing_name = False
                    elif event.key == K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) < 10 and event.unicode.isprintable():
                        player_name += event.unicode
                continue

            if event.type == KEYDOWN:
                if not game_over:
                    if event.key in (K_SPACE, K_UP):
                        hugo.jump()
                else:
                    if event.key == K_r:
                        return True
                    if event.key == K_ESCAPE:
                        return False

        if typing_name:
            screen.fill(SKY)
            screen.blit(big_font.render("Digite seu nome:", True, BLACK), (260, 120))
            screen.blit(font.render(player_name + "_", True, BLACK), (300, 180))
            pygame.display.flip()
            continue

        if not game_over:
            speed += SPEED_ACCEL * dt
            ground_offset += speed

            hugo.update()

            distance_to_next -= speed
            if distance_to_next <= 0:
                if random.choice([True, False]):
                    obstacles.append(Obstacle(WIDTH + 20))
                else:
                    obstacles.append(MouseObstacle(WIDTH + 20))

                distance_to_next = max(
                    450,
                    random.randint(
                        OBSTACLE_SPAWN_MIN - score * 5,
                        OBSTACLE_SPAWN_MAX - score * 6
                    )
                )

            for ob in obstacles[:]:
                ob.update(speed)

                if ob.rect.right < 0:
                    obstacles.remove(ob)

                hugo_hit = hugo.rect.inflate(
                    -hugo.rect.width * 0.4,
                    -hugo.rect.height * 0.2
                )

                if isinstance(ob, MouseObstacle):
                    if hugo_hit.colliderect(ob.hitbox):
                        game_over = True
                        save_ranking(player_name, score)
                else:
                    ob_hit = ob.rect.inflate(
                        -ob.rect.width * 0.2,
                        -ob.rect.height * 0.2
                    )
                    if hugo_hit.colliderect(ob_hit):
                        game_over = True
                        save_ranking(player_name, score)

                if not ob.passed and ob.rect.right < hugo.rect.left:
                    ob.passed = True
                    score += 1

        screen.fill(SKY)
        hugo.draw(screen)

        for ob in obstacles:
            ob.draw(screen)

        draw_ground(ground_offset)

        screen.blit(
            font.render(f"Pontuação: {score}", True, BLACK),
            (WIDTH - 180, 10)
        )

        if game_over:
            screen.blit(
                big_font.render("GAME OVER", True, BLACK),
                (WIDTH // 2 - 120, HEIGHT // 2 - 80)
            )
            screen.blit(
                font.render("R - Reiniciar | ESC - Sair", True, BLACK),
                (WIDTH // 2 - 140, HEIGHT // 2 - 20)
            )

            ranking = load_ranking()
            y = HEIGHT // 2 + 20
            screen.blit(font.render("RANKING:", True, BLACK), (WIDTH // 2 - 60, y))
            y += 25

            for i, (name, score_r) in enumerate(ranking[:5], start=1):
                text = f"{i}. {name} - {score_r}"
                screen.blit(font.render(text, True, BLACK), (WIDTH // 2 - 100, y))
                y += 22

        pygame.display.flip()

def main():
    while True:
        screen.fill(SKY)

        screen.blit(
            big_font.render("Hugo's Adventure", True, BLACK),
            (240, 80)
        )
        screen.blit(font.render("1 - Jogar", True, BLACK), (360, 170))
        screen.blit(font.render("ESC - Sair", True, BLACK), (350, 220))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_1:
                    while game_loop():
                        pass
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
