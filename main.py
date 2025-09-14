import pygame
import random

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 860
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Space Invaders")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
smallFont = pygame.font.Font(None, 50)


#Player code
playerHP = 5
playerSPD = 15
player = pygame.Rect((300, 500, 50, 50))

#Bullet code
bullet = []
bulletATK = 1
bulletSPD = 20
bulletWidth = 10
bulletHeight = 30
shotDelay = 300
lastShotTime = 0

#Charged Shot code
chargedShot = []
chargedShotATK = bulletATK * 2
chargedShotSPD = 30
charging = False
chargingStart = 0
maxChargeTime = 1000
class Bullet:
    def __init__(self, x, y, width, height, speed, damage, color, direction = "N", charged = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.damage = damage
        self.color = color
        self.charged = charged
        self.direction = direction
    def update(self):
        dx = 0
        dy = 0
        if "N" in self.direction:
            dy -= self.speed
        elif "S" in self.direction:
            dy += self.speed
        if "E" in self.direction:
            dx += self.speed
        elif "W" in self.direction:
            dx -= self.speed
        
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


#Enemy code
enemies = []
enemyBullets = []
enemyHP = 1
enemySPD = 3
enemyDelay = 1000
enemySpawnDelay = 2000
lastSpawnTime = 0
lastEnemyShotTime = 0
class Enemy:
    def __init__(self, x, y, width = 50, height = 50, speed = enemySPD, color = (255,0,0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.color = color
        self.health = enemyHP
    def update(self):
        self.rect.y += self.speed
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
class Shooter(Enemy):
    def __init__(self, x, y, width = 60 , height = 30, speed = enemySPD + 2):
        super().__init__(x, y, width, height, speed, color = (255,0,255))
        self.patrolY = 100 + random.randint(-20, 20)
        self.movingDown = True
        self.direction = 1 #-1 = Left/1 = Right
        self.cooldown = enemyDelay
        self.lastShot = lastEnemyShotTime
    def update(self, currentTime, enemyBullets, player):
        #Has the shooter move into position
        if self.movingDown:
            self.rect.y += self.speed
            if self.rect.y >= self.patrolY:
                self.movingDown = False
        #Once in position patrol their Y
        else:
            self.rect.x += self.speed * self.direction
            if self.rect.right >= SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
                self.direction = -1
            elif self.rect.left <= 0:
                self.rect.left = 0
                self.direction = 1
            #Only shoots when the player is near enough with some variance
            if player and abs(self.rect.centerx - player.centerx) < 100 + random.randint(-100,0):
                if currentTime - self.lastShot >= self.cooldown:
                    enemyBullets.append(Bullet(self.rect.centerx - 5, self.rect.bottom, 10, 20, 6, 1, 
                                               (255, 255, 0), direction = "S"))
                    self.lastShot = currentTime
class Charger(Enemy):
    def __init__(self, x, y, width = 40, height = 50, speed = enemySPD + 4):
        super().__init__(x, y, width, height, speed, color = (255,165,0))
        self.health = enemyHP + 1
    def update(self, player):
        dx = player.centerx - self.rect.centerx
        dy = player.centery - self.rect.centery
        #Normalize the vector to get more consistent speed
        distance = (dx * dx + dy * dy) ** 0.5
        if distance != 0:
            dx /= distance
        self.rect.x += int(dx * self.speed)
        self.rect.y += self.speed - 1
class Blocker(Enemy):
    def __init__(self, x, y, width = 70, height = 50, speed = enemySPD):
        super().__init__(x, y, width, height, speed, color = (128, 128, 128))
        self.health = enemyHP * 4
        self.patrolY = 140 + random.randint(-20, 20)
        self.movingDown = True
        self.direction = 1 #-1 = Left/1 = Right
    def update(self):
        if self.movingDown:
            self.rect.y += self.speed
            if self.rect.y >= self.patrolY:
                self.movingDown = False
        #Once in position patrol their Y
        else:
            self.rect.x += self.speed * self.direction
            if self.rect.right >= SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
                self.direction = -1
            elif self.rect.left <= 0:
                self.rect.left = 0
                self.direction = 1
    def takeDamage(self, damage, charged = False):
        if charged:
            self.health -= damage
class Combustion(Enemy):
    def __init__(self, x, y, width = 50, height = 50, speed = enemySPD):
        super().__init__(x, y, width, height, speed, color = (172, 216, 230))
        self.health = enemyHP
        self.type = random.choice(["T", "X"])
    def update(self):
        self.rect.y += self.speed
    def onDeath(self, enemyBullets):
        if self.type == "T":
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="N"))
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="S"))
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="E"))
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="W"))
        elif self.type == "X":
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="NE"))
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="NW"))
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="SE"))
            enemyBullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="SW"))

#Game States: MainMenu Gameplay, Controls, Pause, Map
state = "MainMenu"  #Where the game starts
selectedOption = 0
menu_options = ["Start Game", "Controls", "Quit"]

def drawMainMenu(selected):
    screen.fill((0,0,0))

    #Title Screen
    title = font.render("Rogue Space Invaders", True, (255,255,255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    #Options
    for i, option in enumerate(menu_options):
        color = (255, 255, 0) if i == selected else (255, 255, 255)
        text = smallFont.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 60))

#def drawControls():

#def drawPause():

def gameplay():
    global lastShotTime
    global lastSpawnTime
    global charging
    global chargingStart
    global maxChargeTime
    key = pygame.key.get_pressed()
    global currentTime 
    currentTime = pygame.time.get_ticks()

    #Movement for player
    if key[pygame.K_RCTRL] and key[pygame.K_a] and player.left > 0:
        player.x -= playerSPD / 2
    elif key[pygame.K_RCTRL] and key[pygame.K_d] and player.right > 0:
        player.x += playerSPD / 2
    elif key[pygame.K_a] and player.left > 0:
        player.x -= playerSPD
    elif key[pygame.K_d] and player.right < SCREEN_WIDTH:
        player.x += playerSPD
        
    
    #Action for shooting
    #Charged Shot
    if key[pygame.K_w] and key[pygame.K_RSHIFT] and currentTime - lastShotTime >= shotDelay:
        if not charging:
            charging = True
            chargingStart = currentTime
    elif charging and (not key[pygame.K_w] or not key[pygame.K_RSHIFT]):
        charging = False 
        chargeDuration = currentTime - chargingStart
        fullyCharged = chargeDuration >= maxChargeTime
        chargedShotX = player.centerx - bulletWidth
        chargedShotY = player.top
        if fullyCharged:
            bullet.append(Bullet(chargedShotX, chargedShotY, bulletWidth, bulletHeight, 
                                 chargedShotSPD, chargedShotATK, color=(235, 180, 52), 
                                 direction = "N", charged=True))
            lastShotTime = currentTime
    #Normal shot
    elif key[pygame.K_w] and currentTime - lastShotTime >= shotDelay and not key[pygame.K_RSHIFT]:
        bulletX = player.centerx - bulletWidth
        bulletY = player.top
        bullet.append(Bullet(bulletX, bulletY, bulletWidth, bulletHeight, 
                             bulletSPD, bulletATK, color=(255,255,255), direction = "N"))
        lastShotTime = currentTime
    
    #Update bullets
    for shot in bullet[:]:
            shot.update()
            if shot.rect.bottom < 0:
                bullet.remove(shot)

    #Update enemies
    for enemy in enemies[:]:
        if isinstance(enemy, Shooter):
            enemy.update(currentTime, enemyBullets, player)
        elif isinstance(enemy, Charger):
            enemy.update(player)
        else:
            enemy.update()

        if enemy.rect.top > SCREEN_HEIGHT:
            enemy.rect.y = -50
            enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)

    #Enemy gets hit by a bullet
    for enemy in enemies[:]:
        for shot in bullet[:]:
            if enemy.rect.colliderect(shot.rect):
                bullet.remove(shot)
                if isinstance(enemy, Blocker):
                    enemy.takeDamage(shot.damage, charged=shot.charged)
                else:
                    enemy.health -= shot.damage
                if enemy.health <= 0:
                    if isinstance(enemy, Combustion):
                        enemy.onDeath(enemyBullets)
                    enemies.remove(enemy)
                break

    #Draws the player, bullets, enemies, and their bullets
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (0, 255, 0), player)
    for shot in bullet:
        shot.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    for enemyBull in enemyBullets[:]:
        enemyBull.update()
        if enemyBull.rect.top > SCREEN_HEIGHT or enemyBull.rect.bottom < 0 or enemyBull.rect.right < 0 or enemyBull.rect.left > SCREEN_WIDTH:
            enemyBullets.remove(enemyBull)
        else:
            enemyBull.draw(screen)

    #Enemy spawning & which type
    if currentTime - lastSpawnTime > enemySpawnDelay:
        enemyX = random.randint(0, SCREEN_WIDTH - 50)
        enemyType = random.choice(["Basic", "Shooter", "Charger", "Blocker", "Combustion"])    #add other enemies here

        if enemyType == "Basic":
            #The -50 for the Y makes it so the enemy spawns offscreen before being shown.
            enemies.append(Enemy(enemyX, -50))
        elif enemyType == "Shooter":
            enemies.append(Shooter(enemyX, -50))
        elif enemyType == "Charger":
            enemies.append(Charger(enemyX, -50))
        elif enemyType == "Blocker":
            enemies.append(Blocker(enemyX, -50))
        elif enemyType == "Combustion":
            enemies.append(Combustion(enemyX, -50))

        
        lastSpawnTime = currentTime

#def drawMap():


#--Main Loop--#
run = True
selectedOption = 0

while run:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if state == "MainMenu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    selectedOption = (selectedOption - 1) % len(menu_options)
                elif event.key == pygame.K_s:
                    selectedOption = (selectedOption + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selectedOption == 0:
                        state = "Gameplay"
                    elif selectedOption == 1:
                        state = "Controls"
                    elif selectedOption == 2:
                        run = False
            elif state == "Gameplay":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "Pause"
    if state == "MainMenu":
        drawMainMenu(selectedOption)
    elif state == "Gameplay":
        gameplay()

    if charging:
        chargeDuration = currentTime - chargingStart
        progress = min(chargeDuration / maxChargeTime, 1.0)

        barWidth = player.width
        barHeight = 8
        barX = player.x
        barY = player.bottom + 10

        pygame.draw.rect(screen, (80, 80, 80), (barX, barY, barWidth, barHeight))
        pygame.draw.rect(screen, (0, 200, 255), (barX, barY, int(barWidth * progress), barHeight))
    
    pygame.display.update()

pygame.quit()