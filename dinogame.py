import pygame
import random
import csv
import sys

WIDTH, HEIGHT = 800, 400
FPS = 60
GROUND_HEIGHT = 80
GRAVITY = 0.8
JUMP_VELOCITY = -15
OBSTACLE_SPAWN_MIN = 900
OBSTACLE_SPAWN_MAX = 1600
SPEED_START = 6
SPEED_ACCEL = 0.0012

BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
SKY = (235, 245, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Dinossauro - Pygame")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 48)

class Dino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 44
        self.h = 48
        self.vel_y = 0
        self.on_ground = True
        self.alive = True

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

    def draw(self, surf):
        pygame.draw.rect(surf, BLACK, self.rect())

class Obstacle:
    def __init__(self, x):
        self.x = x
        self.w = random.choice([18, 24, 30])
        self.h = random.choice([36, 48, 56])
        self.passed = False

    def rect(self):
        return pygame.Rect(int(self.x), HEIGHT - GROUND_HEIGHT - self.h, self.w, self.h)

    def update(self, speed):
        self.x -= speed

    def draw(self, surf):
        pygame.draw.rect(surf, BLACK, self.rect())

def draw_ground(offset):
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    step = 40
    for i in range(-step, WIDTH + step, step):
        x = i + int(offset % step)
        pygame.draw.line(screen, GRAY, (x, HEIGHT - GROUND_HEIGHT + 10),
                         (x + 20, HEIGHT - GROUND_HEIGHT + 10), 2)

def game_loop():
    dino = Dino(80, HEIGHT - GROUND_HEIGHT)
    obstacles = []
    distance_to_next = random.randint(OBSTACLE_SPAWN_MIN, OBSTACLE_SPAWN_MAX)
    speed = SPEED_START
    ground_offset = 0
    score = 0

    game_over = False
    entering_name = False
    saved = False
    player_name = ""

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        dino.jump()
                else:
                    if entering_name:
                        if event.key == pygame.K_RETURN and player_name:
                            with open("dados.csv", "a", newline="", encoding="utf-8") as f:
                                csv.writer(f).writerow([player_name, score])
                            entering_name = False
                            saved = True
                        elif event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        else:
                            if len(player_name) < 10 and event.unicode.isprintable():
                                player_name += event.unicode
                    else:
                        if event.key == pygame.K_r:
                            return True
                        if event.key == pygame.K_ESCAPE:
                            return False

        if not game_over:
            speed += SPEED_ACCEL * dt
            ground_offset += speed
            dino.update()

            distance_to_next -= speed
            if distance_to_next <= 0:
                obstacles.append(Obstacle(WIDTH + 20))
                distance_to_next = random.randint(
                    int(OBSTACLE_SPAWN_MIN - score * 0.5),
                    int(OBSTACLE_SPAWN_MAX - score * 0.06)
                )
                distance_to_next = max(450, distance_to_next)

            for ob in obstacles[:]:
                ob.update(speed)
                if ob.x + ob.w < -50:
                    obstacles.remove(ob)
                elif dino.rect().colliderect(ob.rect()):
                    game_over = True
                    entering_name = True

                if not ob.passed and ob.x + ob.w < dino.x:
                    ob.passed = True
                    score += 1

        screen.fill(SKY)
        dino.draw(screen)
        for ob in obstacles:
            ob.draw(screen)
        draw_ground(ground_offset)

        screen.blit(font.render(f"Pontuação: {score}", True, BLACK), (WIDTH - 170, 10))

        if game_over:
            screen.blit(big_font.render("GAME OVER", True, BLACK),
                        (WIDTH//2 - 120, HEIGHT//2 - 80))

            if entering_name:
                screen.blit(font.render("Digite seu nome:", True, BLACK),
                            (WIDTH//2 - 110, HEIGHT//2 - 30))
                pygame.draw.rect(screen, BLACK,
                                 (WIDTH//2 - 140, HEIGHT//2, 280, 32), 2)
                screen.blit(font.render(player_name, True, BLACK),
                            (WIDTH//2 - 130, HEIGHT//2 + 6))
            else:
                screen.blit(font.render("R - Reiniciar | ESC - Sair", True, BLACK),
                            (WIDTH//2 - 130, HEIGHT//2 + 10))

        pygame.display.flip()

def show_scores():
    try:
        with open("dados.csv", "r", encoding="utf-8") as f:
            scores = sorted([(r[0], int(r[1])) for r in csv.reader(f)],
                            key=lambda x: x[1], reverse=True)[:3]
    except:
        scores = []

    while True:
        screen.fill(SKY)
        screen.blit(big_font.render("Top 3 Pontuações", True, BLACK), (240, 80))

        for i, (n, s) in enumerate(scores, 1):
            screen.blit(font.render(f"{i}º - {n}: {s}", True, BLACK),
                        (300, 140 + i * 30))

        screen.blit(font.render("B - Voltar", True, BLACK), (350, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                return
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

def main():
    while True:
        screen.fill(SKY)
        screen.blit(big_font.render("Jogo do Dinossauro", True, BLACK), (250, 80))
        screen.blit(font.render("1 - Jogar", True, BLACK), (360, 170))
        screen.blit(font.render("2 - Placar", True, BLACK), (350, 210))
        screen.blit(font.render("ESC - Sair", True, BLACK), (345, 250))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    while game_loop():
                        pass
                if event.key == pygame.K_2:
                    show_scores()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()
