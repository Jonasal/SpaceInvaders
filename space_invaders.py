import pygame 
import os 
import time
import random
pygame.font.init()

# Capitals are constants for python convention
# Open window
WIDTH, HEIGHT = 1200, 750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Opponent
INVADER_ONE_RED = pygame.transform.scale(pygame.image.load(os.path.join("assets", "invader_one.png")), (50,50))
INVADER_TWO_GREEN = pygame.transform.scale(pygame.image.load(os.path.join("assets", "invader_two.png")), (50,50))
INVADER_THREE_BLUE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "invader_three.png")), (50,50))
INVADER_FOUR_YELLOW = pygame.transform.scale(pygame.image.load(os.path.join("assets", "invader_four.png")), (50,50))
INVADER_FIVE_PINK = pygame.transform.scale(pygame.image.load(os.path.join("assets", "invader_five.png")), (50,50))

# Player
PLAYER_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "player.png")),(50,50))

# Lasers
PLAYER_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_laser.png")), (10,30))
INVADER_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "invader_laser.png")), (10,30))

#background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "stars.jpg")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self,x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, WINDOW):
        WINDOW.blit(self.image, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)
    

class Ship:
    COOLDOWN = 30 

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, velocity, object):
        self.cooldown()  
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(object):
                object.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+20, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


class Player(Ship):
    def __init__(self, x,y,health=100):
        super().__init__(x,y,health)
        self.ship_image = PLAYER_SHIP
        self.laser_image = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health

    def move_lasers(self, velocity, objects):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objects:
                    if laser.collision(obj):
                        objects.remove(obj)
                        self.lasers.remove(laser)
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x,self.y + self.ship_image.get_height()+10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x,self.y + self.ship_image.get_height()+10, self.ship_image.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
        'red': (INVADER_ONE_RED, INVADER_LASER),
        'green': (INVADER_TWO_GREEN, INVADER_LASER),
        'blue': (INVADER_THREE_BLUE, INVADER_LASER),
        'yellow': (INVADER_FOUR_YELLOW, INVADER_LASER),
        'pink': (INVADER_FIVE_PINK, INVADER_LASER)
        }
    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+23, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(object_1, object_2):
    offset_x = object_2.x - object_1.x
    offset_y = object_2.y - object_1.y
    return object_1.mask.overlap(object_2.mask, (offset_x,offset_y)) != None


# Game Logic
def main_logic():
    run = True
    FPS = 60
    level = 0
    lives = 5
    player_velocity = 7
    enemy_velocity = 1
    enemies = []
    laser_velocity = 6
    wave_length = 5
    main_font = pygame.font.SysFont("Comicsans", 50)
    lost_font = pygame.font.SysFont("Comicsans", 60)

    player = Player(300,650)

    clock = pygame.time.Clock()
    
    lost = False
    lost_count = 0

    def redraw():
        WINDOW.blit(BACKGROUND, (0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WINDOW.blit(lives_label, (50,50))
        WINDOW.blit(level_label, (WIDTH-level_label.get_width() - 50,50))
        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS*3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level +=1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(['red', 'green', 'blue', 'yellow', 'pink']))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_velocity > 0:
            player.x -= player_velocity
        if keys[pygame.K_RIGHT] and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(-laser_velocity, enemies)

main_logic()