# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Space Invaders
# 

# %%
import pygame as pg
import os
import random
import time

# init the game
pg.init()

"""
Game parameters
"""

# Player can shoot every COOL_DOWN/FPS seconds
COOL_DOWN = 10

# Palenties
LASER_HIT = 10
ENEMY_HIT = 20

# Max frame/s of loop
FPS = 90

P_VELOCITY = 5
P_SHIFT_FACTOR = 3
L_VELOCITY = 5
WAVE_LENGTH = 5
E_VELOCITY = 1
E_SHOOT_INTERVAL = 5 # may shoot every _ seconds
BEST_SCORE = 0

# Set Console
W, H = 750, 750
WIN = pg.display.set_mode((W,H))

# Set Caption of the game
GAME_NAME = "Space Invaders"
pg.display.set_caption(GAME_NAME)

# Load all ships images
IMAGE_FOL = "assets"
RED_SPACE_SHIP = pg.image.load(os.path.join(IMAGE_FOL,"pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pg.image.load(os.path.join(IMAGE_FOL,"pixel_ship_GREEN_small.png"))
BLUE_SPACE_SHIP = pg.image.load(os.path.join(IMAGE_FOL,"pixel_ship_BLUE_small.png"))

# Player Ship
YELLOW_SPACE_SHIP = pg.image.load(os.path.join(IMAGE_FOL,"pixel_ship_YELLOW.png"))

# LASERS
RED_LASER = pg.image.load(os.path.join(IMAGE_FOL,"pixel_LASER_RED.png"))
GREEN_LASER = pg.image.load(os.path.join(IMAGE_FOL,"pixel_LASER_GREEN.png"))
YELLOW_LASER = pg.image.load(os.path.join(IMAGE_FOL,"pixel_LASER_YELLOW.png"))
BLUE_LASER = pg.image.load(os.path.join(IMAGE_FOL,"pixel_LASER_BLUE.png"))

# LOAD BACKGROUND
BG = pg.image.load(os.path.join(IMAGE_FOL,"BACKGROUND-BLACK.png"))
BG = pg.transform.scale(BG, (W,H))

# Set colors
WHITE = (255,255,255)
BLACK = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
SILVER = (192,192,192)


# %%
class Laser():
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pg.mask.from_surface(img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        """
        Return True if Laser is still on screen
        """
        return self.y > height or self.y < 0

    def collision(self, obj):
        return collide(self, obj)


# %%
class Ship:
    def __init__(self,x ,y):
        self.x, self.y = x, y
        self.health = 100
        self.lasers = list()
        self.cool_down_counter = 0
        self.ship_img = None
        self.laser_img = None
        

    def draw(self, window):
        # Draws the ship and the lasers fired by the object
        window.blit(self.ship_img, (self.x, self.y))
        for l in self.lasers:
            l.draw(window)

    def move_lasers(self, vel, player):
        """
        # Move the laser for the ship
        # Player Class has their own move_lasers method
        """
        # Check if we can shoot more lasers
        self.cool_down()

        for l in self.lasers[:]:
            # Move the lasers
            l.move(vel)
            # if they are not on screen anymore
            if l.off_screen(H):
                self.lasers.remove(l)
            # if they are on screen, check if they are hitting player ship
            elif l.collision(player):
                player.health -= LASER_HIT
                self.lasers.remove(l)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cool_down(self):
        # Check if number of lasers fired by the player is in the range of COOL_DOWN
        if self.cool_down_counter > COOL_DOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        """
        # Add new lasers to the list
        """
        # Waiting for FPS/COOL_DOWN seconds
        if self.cool_down_counter == 0:
            self.cool_down_counter = 1
            l = Laser(self.x + self.ship_img.get_width()//2 - self.laser_img.get_width()//2 , self.y, self.laser_img)
            self.lasers.append(l)


# %%
class Player(Ship):
    def __init__(self,x ,y):
        super().__init__(x,y)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pg.mask.from_surface(self.ship_img)
        self.max_health = 100
        self.score = 0


    def move_lasers(self, vel,level, enemies):
        self.cool_down()
        for l in self.lasers[:]:
            l.move(vel)
            # Remove offscreen lasers
            if l.off_screen(H):
                self.lasers.remove(l)
            else:
                for o in enemies[:]:
                    # Check if any fire is hitting the enemy ship
                    if l.collision(o):
                        self.score += level*5
                        # Added if's due to the ValueError: list.remove(x): x not in list
                        if o in enemies:
                            enemies.remove(o)
                        if l in self.lasers:
                            self.lasers.remove(l)

    def draw_health_bar(self, window):

        # Red bar
        T_L = (self.x, self.y + self.get_height() + 10)
        W_H = (self.get_width(), 10)
        pg.draw.rect(window, RED, (T_L, W_H ))

        # Green bar
        if self.health:
            W_H = (self.get_width()*self.health/self.max_health, 10)
            pg.draw.rect(window, GREEN, (T_L, W_H ))
        

    def draw(self, window):
        super().draw(window)
        self.draw_health_bar(window)


# %%
class Enemy(Ship):
    SHIP_COLOR_MAP = {
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "red": (RED_SPACE_SHIP, RED_LASER)
    }

    def __init__(self,x,y,color, health=100):
        super().__init__(x,y)
        self.color = color
        self.ship_img, self.laser_img = self.SHIP_COLOR_MAP[color]
        self.mask = pg.mask.from_surface(self.ship_img)
        self.threat_level = random.choice([1,2])


    def move(self, val):
        self.y += val


    def shoot(self):
        """
        Enemy's lasers list updates
        """
        # Laser LEFT X = ship.x + ship_w/2 - laser_w/2
        # Laser TOP Y = ship.y + ship_h//2
        laser_x = self.x + self.ship_img.get_width()//2 - self.laser_img.get_width()//2 
        laser_y = self.y + self.ship_img.get_height()//2
        l = Laser(laser_x, laser_y , self.laser_img)
        self.lasers.append(l)


# %%
def collide(a,b):
    """
                a.x to b.x (x_offset)
                :    :
      a.x ----> +----:---------+
        to      |    :         |
      b.y ------|--> +-----------+
    (y_offset)  |    |   b       |
                |    +-----------+
                |      a       |
                +--------------+
    """
    offset_x, offset_y = b.x - a.x, b.y - a.y
    return a.mask.overlap(b.mask, (offset_x, offset_y)) != None


# %%
def main():
    run = True
    level = 0
    lives = 10
    lost = False
    player = Player(300,640)
    HEALTH_BAR_PADING = 15
    enemies = []
    clock = pg.time.Clock()

    MAIN_FONT_NAME = "calibri"
    MAIN_FONT_SIZE = 28
    LOST_FONT_NAME = "elephant"
    LOST_FONT_SIZE = 70
    # Make the font
    main_font = pg.font.SysFont(MAIN_FONT_NAME, MAIN_FONT_SIZE, bold=True)
    lost_font = pg.font.SysFont(LOST_FONT_NAME, LOST_FONT_SIZE)

    
    def draw_window():
        WIN.blit(BG,(0,0))
        padding = 10
        
        # write with the font
        lives_label = main_font.render("Lives: {}".format(lives), 1, GREEN)
        level_label = main_font.render("Level: {}".format(level), 1, WHITE)
        score_label = main_font.render(f"Score: {player.score}", 1, YELLOW)

        # Declare where to show
        lives_label_T_L = (padding, padding)
        score_label_T_L = (W - padding - score_label.get_width() , padding)
        level_label_T_L = (W - padding - score_label.get_width(),score_label.get_height() + padding)

        # Show
        WIN.blit(lives_label, lives_label_T_L)
        WIN.blit(level_label, level_label_T_L)
        WIN.blit(score_label, score_label_T_L)

        # Show all enemies on screen
        for e in enemies:
            e.draw(WIN)

        # Show the player
        player.draw(WIN)

        if lost:
            # Show lost message
            lost_label = lost_font.render(f"Planet Invaded!!", 1, RED)
            WIN.blit(lost_label, (W/2 - lost_label.get_width()/2, H/2 - lost_label.get_height()))
            
            #change best score before returning
            global BEST_SCORE
            if player.score > BEST_SCORE: BEST_SCORE = player.score
            
            pg.display.update()
            time.sleep(3)
            return

        pg.display.update()


    while run:
        # Limit the execetion of loop to FPS value
        clock.tick(FPS)

        lost = True if lives <= 0 or player.health <= 0 else False
        if lost: run = False

        if len(enemies) == 0:
            level += 1
            global WAVE_LENGTH
            WAVE_LENGTH += 5
            for _ in range(WAVE_LENGTH):

                # Create and populate Enemies list
                # They appear on random places
                e_x = random.randint(50, W - 100)
                e_y = random.randint(-2*H, -100)
                e_c = random.choice(["red", "green", "blue"])
                e = Enemy(e_x, e_y, e_c)
                enemies.append(e)
        """
        Check user inputs
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        
        # Movements
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and player.x - P_VELOCITY > 0: #Move left
            player.x -= P_VELOCITY
            if keys[pg.K_RSHIFT]: player.x -= P_SHIFT_FACTOR
        if keys[pg.K_RIGHT] and player.x + P_VELOCITY + player.get_width() < W: #Move right
            player.x += P_VELOCITY
            if keys[pg.K_RSHIFT]: player.x += P_SHIFT_FACTOR
        if keys[pg.K_UP] and player.y - P_VELOCITY > 0: #Move up
            player.y -= P_VELOCITY
            if keys[pg.K_RSHIFT]: player.y -= P_SHIFT_FACTOR
        if keys[pg.K_DOWN] and player.y + P_VELOCITY + player.get_height() + HEALTH_BAR_PADING < H: #Move down
            player.y += P_VELOCITY
            if keys[pg.K_RSHIFT]: player.y += P_SHIFT_FACTOR

    
        for e in enemies[:]: 
            #Move the enemies
            e.move(E_VELOCITY*e.threat_level)
            # Move their laser
            e.move_lasers(L_VELOCITY*e.threat_level + 2*level,player)
            # 1C1 / 120C1 is the probability to get "1", equals 50%
            # 50% chance that within second, an enemy will shoot
            enemy_may_shoot = random.randint(1,E_SHOOT_INTERVAL*FPS) == 1
            if enemy_may_shoot: #Enemy Shoot
                e.shoot()

            if collide(e, player): #Player collide with enemy
                player.health -= ENEMY_HIT
                enemies.remove(e)
            elif e.get_height() + e.y > H: # enemy crossed the borderline
                lives -= 1
                enemies.remove(e)

        if keys[pg.K_SPACE]: #Player Shoot
            player.shoot()

        # Move player lasers
        player.move_lasers(-(L_VELOCITY + level*2),level, enemies)

        # Draw everything
        draw_window()


# %%
def main_menu():
    TITLE_FONT_NAME = "comicsans"
    HELP_FONT_NAME = "comicsans"
    BEST_SCORE_FONT_NAME = "comicsans"
    TITLE_font_size = 90
    HELP_FONT_SIZE = 26
    BEST_SCORE_FONT_SIZE = 28
    
    TITLE = "Press enter to start..."
    MOVE = "Press Arrow (or RShift + Arrow) Keys To Move"
    SHOOT = "Press Space Key To Shoot"

    TITLE_FONT = pg.font.SysFont(TITLE_FONT_NAME, TITLE_font_size)
    HELP_FONT = pg.font.SysFont(HELP_FONT_NAME, HELP_FONT_SIZE)
    BEST_SCORE_FONT = pg.font.SysFont(BEST_SCORE_FONT_NAME, BEST_SCORE_FONT_SIZE)

    TITLE_lable = TITLE_FONT.render(TITLE, 1, WHITE)
    MOVE_lable = HELP_FONT.render(MOVE, 1, SILVER)
    SHOOT_label = HELP_FONT.render(SHOOT, 1, SILVER)

    TITLE_lable_T_L = ((W - TITLE_lable.get_width())/2 , (H - TITLE_lable.get_height())/2/2)
    MOVE_lable_T_L = (TITLE_lable_T_L[0], H - 100)
    SHOOT_label_T_L = (MOVE_lable_T_L[0], MOVE_lable_T_L[1] + MOVE_lable.get_height() + 5)
    BEST_SCORE_label_T_L = (W - 200, H - 100)


    def get_best_score_label():
        SCORE = f"Best Score: {BEST_SCORE}"
        BEST_SCORE_label = BEST_SCORE_FONT.render(SCORE, 1, GREEN)
        return BEST_SCORE_label


    run = True
    while run:
        WIN.blit(BG, (0,0))
        WIN.blit(TITLE_lable, TITLE_lable_T_L)
        WIN.blit(MOVE_lable, MOVE_lable_T_L)
        WIN.blit(SHOOT_label, SHOOT_label_T_L)
        WIN.blit(get_best_score_label(), BEST_SCORE_label_T_L)
        pg.display.update()
        for e in pg.event.get():
            if e.type == pg.QUIT:
                run = False
        if pg.key.get_pressed()[pg.K_RETURN]:
            main()
    
    pg.quit()

main_menu()


