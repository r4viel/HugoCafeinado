import pygame
import random
import csv
import sys
import os

WIDTH, HEIGHT = 800, 400
FPS = 60
GROUND_HEIGHT = 80
GRAVITY = 0.8
JUMP_VELOCITY = -15
OBSTACLE_SPAWN_MIN = 900
OBSTACLE_SPAWN_MAX = 1600
SPEED_START = 6
SPEED_ACCEL = 0.0012

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
SKY = (235, 245, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Dinossauro - Pygame")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 48)

# ======================
# CONTADOR DE MORTES
# ======================
death_count = 0


class Dino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 44
        self.h = 48
        self.vel_y = 0
        self.on_ground = True
        self.alive = True
        self.step = 0
        self.step_timer = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y - self.h), self.w, self.h)

    def jump(self):
        if self.on_ground and self.alive:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        if self.y >= HEIGHT - GROUND_HEIGHT:
            self.y = HEIGHT - GROUND_HEIGHT
            self.vel_y = 0
            self.on_ground = True

        if not self.on_ground:
            self.step = 2
        else:
            self.step_timer += 1
            if self.step_timer > 6:
                self.step_timer = 0
                self.step = (self.step + 1) % 2

    def draw(self, surf):
        r = self.rect()
        pygame.draw.rect(surf, BLACK, r)
        eye = (r.x + int(self.w * 0.7), r.y + 12)
        pygame.draw.circle(surf, WHITE, eye, 4)
        pygame.draw.circle(surf, BLACK, eye, 2)

        if self.step == 0:
            pygame.draw.line(surf, BLACK, (r.x + 10, r.y + self.h), (r.x + 10, r.y + self.h + 12), 4)
            pygame.draw.line(surf, BLACK, (r.x + 30, r.y + self.h), (r.x + 30, r.y + self.h + 6), 4)
        elif self.step == 1:
            pygame.draw.line(surf, BLACK, (r.x + 10, r.y + self.h), (r.x + 10, r.y + self.h + 6), 4)
            pygame.draw.line(surf, BLACK, (r.x + 30, r.y + self.h), (r.x + 30, r.y + self.h + 12), 4)
        else:
            pygame.draw.line(surf, BLACK, (r.x + 20, r.y + self.h), (r.x + 20, r.y + self.h + 8), 4)


class Obstacle:
    def __init__(self, x, kind='cactus'):
        self.x = x
        self.kind = kind
        if kind == 'cactus':
            self.w = random.choice([18, 24, 30])
            self.h = random.choice([36, 48, 56])
        else:
            self.w = 34
            self.h = 24
            self.y_offset = random.choice([60, 80])
        self.passed = False

    def rect(self):
        if self.kind == 'cactus':
            return pygame.Rect(int(self.x), HEIGHT - GROUND_HEIGHT - self.h, self.w, self.h)
        else:
            return pygame.Rect(int(self.x), HEIGHT - GROUND_HEIGHT - self.y_offset, self.w, self.h)

    def update(self, speed):
        self.x -= speed

    def draw(self, surf):
        r = self.rect()
        if self.kind == 'cactus':
            pygame.draw.rect(surf, BLACK, r)
        else:
            pygame.draw.ellipse(surf, BLACK, r)


def draw_ground(surf, offset):
    pygame.draw.rect(surf, BLACK, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    step = 40
    for i in range(-step, WIDTH + step, step):
        x = i + int(offset % step)
        pygame.draw.line(surf, GRAY, (x, HEIGHT - GROUND_HEIGHT + 10), (x + 20, HEIGHT - GROUND_HEIGHT + 10), 2)


def draw_text(surf, text, x, y):
    surf.blit(font.render(text, True, BLACK), (x, y))


def game_loop():
    global death_count

    dino = Dino(80, HEIGHT - GROUND_HEIGHT)
    obstacles = []
    distance_to_next = random.randint(OBSTACLE_SPAWN_MIN, OBSTACLE_SPAWN_MAX)
    speed = SPEED_START
    ground_offset = 0
    score = 0
    wrote_score = False
    game_over = False

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over:
                    dino.jump()
                if event.key == pygame.K_r and game_over:
                    return True

        if not game_over:
            speed += SPEED_ACCEL * dt
            ground_offset += speed
            dino.update()

            distance_to_next -= speed
            if distance_to_next <= 0:
                kind = 'cactus' if random.random() < 0.85 else 'bird'
                obstacles.append(Obstacle(WIDTH + 20, kind))
                distance_to_next = random.randint(450, OBSTACLE_SPAWN_MAX)

            for ob in list(obstacles):
                ob.update(speed)

                if dino.rect().colliderect(ob.rect()):
                    game_over = True
                    death_count += 1

                if not ob.passed and ob.x + ob.w < dino.x:
                    ob.passed = True
                    score += 1

        screen.fill(SKY)
        dino.draw(screen)
        for ob in obstacles:
            ob.draw(screen)
        draw_ground(screen, ground_offset)

        draw_text(screen, f"Pontuação: {score}", WIDTH - 170, 10)
        draw_text(screen, f"Mortes: {death_count}", 10, 10)

        if game_over and not wrote_score:
            file_exists = os.path.isfile("dados.csv")
            with open("dados.csv", "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Pontuacao", "Morte"])
                writer.writerow([score, death_count])
            wrote_score = True

            txt = big_font.render("GAME OVER", True, BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 30))

            sub = font.render("R = Reiniciar | ESC = Sair", True, BLACK)
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))

        pygame.display.flip()


def main():
    while True:
        restart = True
        while restart:
            restart = game_loop()


if __name__ == "__main__":
    main()
