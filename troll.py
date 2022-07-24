import pygame
from pygame.locals import *
import sys
from random import randint
import math
import os
import os.path

pygame.init()

# Important Variables
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 600
CENTER_X = int(SCREEN_WIDTH / 2)
CENTER_Y = int(SCREEN_HEIGHT / 2)
FPS = 60

# Colors
WHITE = [255, 255, 255]
BLACK = [0, 0, 0]

from pathlib import Path


path = os.path.join(str(Path.home()), ".thetrollzone")
if os.path.exists(path) == False:
    os.mkdir(path)
p = os.path.join(str(Path.home()), ".thetrollzone", "redundant.troll")
print(p)
if os.path.exists(p) == False:
    f = open(p, "w")
    f.write("0")
    f.close()

clock = pygame.time.Clock()

def path(path: str):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, path)

Icon = pygame.image.load(path('assets/Icon.png'))

pygame.display.set_icon(Icon)
pygame.display.set_caption("The Troll Zone")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

trollface = pygame.image.load(path('assets/Trollface.png'))
trollface = pygame.transform.scale(trollface, (120, 100))

ball = pygame.image.load(path('assets/ball1.png'))
ball = pygame.transform.scale(ball, (50, 50))
 
fail = pygame.mixer.Sound(path('assets/FAIL #2.mp3'))
boom = pygame.mixer.Sound(path('assets/boom.mp3'))
laugh = pygame.mixer.Sound(path('assets/CARTOON LAUGH.mp3'))
music = pygame.mixer.music.load(path('assets/Trolled.mp3'))

# Game Variables
angle = math.radians(0) # randint(0, 360)
screen_rect = screen.get_rect()

score = 0

start = False
game_over = False

font_big = pygame.font.Font(path('assets/courier.ttf'), 60)
font_small = pygame.font.Font(path('assets/courier.ttf'), 30)

def big_text(text: str, color: list,  x: int, y: int):
    title = font_big.render(text, True, color)
    title_rect = title.get_rect()
    title_rect.center = (x, y)
    if bg.index == 10:
        pygame.draw.rect(screen, WHITE, title_rect)
    screen.blit(title, title_rect)

def small_text(text: str, color: list,  x: int, y: int):
    title = font_small.render(text, True, color)
    title_rect = title.get_rect()
    title_rect.center = (x, y)
    if bg.index == 10:
        pygame.draw.rect(screen, WHITE, title_rect)
    screen.blit(title, title_rect)
    
class Background():
    def __init__(self):
        self.index = 0
        self.bgs = []
        for num in range(1, 15):
            img = pygame.image.load(path(f'assets/bg{num}.png'))
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bgs.append(img)
        self.bg = self.bgs[self.index]
        self.countdown = 0

    def update(self):
        self.bg = self.bgs[self.index]

def edge_action():
    global score, best_score
    boom.play()
    bg.index += 1
    bg.index %= len(bg.bgs)
    score += 100

    f = open(p, "r")
    best_score = int(f.read())
    f.close()
    if score > best_score:  
        best_score = score
    f = open(path(p), "w")
    f.write(str(best_score))
    f.close()

class Troll(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = trollface
        self.rect = self.image.get_rect()
        self.hitbox = pygame.Rect(0, 0, 60, 50)
        self.hitbox.center = [x, y]
        self.rect.center = [x, y]
        self.speed = 4
        self.dir_x = math.cos(angle)
        self.dir_y = math.sin(angle)

    def update(self):
        # Handle Movement
        self.vel_x = self.dir_x * self.speed
        self.vel_y = self.dir_y * self.speed

        if start and not game_over:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.dir_x *= -1
                edge_action()
                self.speed *= 1.05
                self.speed = min(self.speed, 22)

            if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
                self.dir_y *= -1
                edge_action()
                self.speed *= 1.05
                self.speed = min(self.speed, 22)

            # Unstuck
            if self.vel_x == 0:
                self.dir_x += 1
            elif self.vel_y == 0:
                self.dir_y -= 1

            self.hitbox.x = self.rect.x + 30
            self.hitbox.y = self.rect.y + 25

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.skin = 0
        self.skins = []
        for num in range(8, 18):
            img = pygame.image.load(path(f'assets/explosion{num}.png'))
            self.images.append(img)
        for num in range(1, 9):
            img = pygame.image.load(path(f'assets/explosion{num}.png'))
            self.images.append(img)
        for num in range(1, 7):
            img = pygame.image.load(path(f'assets/ball{num}.png'))
            img = pygame.transform.scale(img, (50, 50))
            self.skins.append(img)
        self.image = self.skins[self.skin]
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.decell = .3
        self.accel = 1
        self.max_speed = 7
        self.vel_x = 0
        self.vel_y = 0
        self.dir_x = 0
        self.dir_y = 0

        self.countdown = 0

    def change_skin(self):
        self.skin += 1
        self.skin %= len(self.skins)
        self.image = self.skins[self.skin]

    def death(self):
        self.countdown += 1
        if self.countdown > 3:
            self.countdown = 0
            if self.index < 17:
                self.index += 1
                self.image = self.images[self.index]
            elif self.index == 17:
                self.rect.x = -100
                self.rect.y = -100
                self.index += 1


    def update(self):
        # Handle Direction
        if not game_over and start:
            self.dir_x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            self.dir_y = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])

            # Movement

            if self.dir_x == 0:
                if self.vel_x < 0:
                    self.vel_x += self.decell
                    self.vel_x = min(self.vel_x, 0)
                elif self.vel_x > 0:
                    self.vel_x -= self.decell
                    self.vel_x = max(self.vel_x, 0)
            else:
                self.vel_x += self.accel * self.dir_x
                if self.dir_x > 0:
                    self.vel_x = min(self.vel_x, self.dir_x * self.max_speed)
                elif self.dir_x < 0:
                    self.vel_x = max(self.vel_x, self.dir_x * self.max_speed)

            if self.dir_y == 0:
                if self.vel_y < 0:
                    self.vel_y += self.decell
                    self.vel_y = min(self.vel_y, 0)
                elif self.vel_y > 0:
                    self.vel_y -= self.decell
                    self.vel_y = max(self.vel_y, 0)
            else:
                self.vel_y += self.accel * self.dir_y
                if self.dir_y > 0:
                    self.vel_y = min(self.vel_y, self.dir_y * self.max_speed)
                elif self.dir_y < 0:
                    self.vel_y = max(self.vel_y, self.dir_y * self.max_speed)

            # Boundaries
            if self.rect.left < 0:
                self.rect.x += 0 - self.rect.x
                self.vel_x = 0
            elif self.rect.right > SCREEN_WIDTH:
                self.rect.x -= self.rect.right - SCREEN_WIDTH
                self.vel_x = 0

            if self.rect.top < 0:
                self.rect.y += 0 - self.rect.top
                self.vel_y = 0
            elif self.rect.bottom > SCREEN_HEIGHT:
                self.rect.y -= self.rect.bottom - SCREEN_HEIGHT
                self.vel_y = 0

            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

# Troll stuff
troll_group = pygame.sprite.Group()
troll = Troll(randint(100, SCREEN_WIDTH - 100), randint(100, SCREEN_HEIGHT - 100))
troll_group.add(troll)

# Player Stuff
player_group = pygame.sprite.Group()
player = Player(SCREEN_WIDTH - troll.rect.x, SCREEN_HEIGHT - troll.rect.y)
player_group.add(player)

bg = Background()

def reset_game():
    global score, game_over, start 
    troll.rect.x = randint(100, SCREEN_WIDTH - 100) - 60
    troll.rect.y = randint(100, SCREEN_HEIGHT - 100) - 50
    troll.speed = 4

    game_over = False
    start = False

    player.vel_x = 0
    player.vel_y = 0
    player.index = 0
    player.countdown = 0
    player.image = player.skins[player.skin]
    player.rect.x = SCREEN_WIDTH - troll.rect.x - 25
    player.rect.y = SCREEN_HEIGHT - troll.rect.y - 25

    score = 0

    pygame.mixer.stop()

def text_color():
    if bg.index in [1, 5, 8, 11, 12]:
        return [255, 255, 255]
    else:
        return [0, 0, 0]

f = open(path(p), "r")
best_score = int(f.read())
f.close()

start_music = False

exit = False
while not exit:
    # FPS CAP
    clock.tick(FPS)

    keys = pygame.key.get_pressed()

    bg.update()
    screen.blit(bg.bg, (0, 0))
    
    # Troll Class 
    #pygame.draw.rect(screen, BLACK, troll.rect) # Deboug Box
    troll_group.update()
    troll_group.draw(screen)
    
    # Player Class
    #pygame.draw.rect(screen, BLACK, player.rect) # Deboug Box
    player_group.update()
    player_group.draw(screen)

    score_text = font_small.render('Score: ' + str(score), True, text_color())
    score_rect = score_text.get_rect()
    score_rect.x = 10
    score_rect.y = 40
    if bg.index == 10:
        pygame.draw.rect(screen, WHITE, score_rect)
    screen.blit(score_text, score_rect)

    best_score_text = font_small.render('Best Score: ' + str(best_score), True, text_color())
    best_score_rect = best_score_text.get_rect()
    best_score_rect.x = 10
    best_score_rect.y = 5
    if bg.index == 10:
        pygame.draw.rect(screen, WHITE, best_score_rect)
    screen.blit(best_score_text, best_score_rect)

    # Start Loop
    if not start:
        big_text('The Troll Zone', text_color(), CENTER_X, 100)
        small_text('Press any key to begin...', text_color(), CENTER_X, 140)

        small_text("Press 'SPACE' to change skin", text_color(), CENTER_X, SCREEN_HEIGHT - 100)

    # Game Over
    if player.rect.colliderect(troll.hitbox) and not game_over:
        if not start:
            start = True
        game_over = True

        pygame.mixer.stop()
        fail.play()

        
    # Game over Loop
    if game_over:
        big_text('Problem?', text_color(), CENTER_X, 100)
        small_text("Press 'R' to Restart", text_color(), CENTER_X, 140)
        player.death()
        

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True
        elif event.type == pygame.KEYDOWN:
            # Game Start
            if not game_over and not start and event.key != pygame.K_SPACE:
                start = True

            if event.key == pygame.K_SPACE and not start and not game_over:
                player.change_skin()

            if not game_over and not start_music and event.key != pygame.K_SPACE:
                start_music = True
                pygame.mixer.music.play(-1)

            if game_over and event.key == pygame.K_r:
                reset_game()
                laugh.play()
            # Exit
            if event.key == pygame.K_ESCAPE:
                exit = True

    pygame.display.update()

pygame.quit()
sys.exit()
