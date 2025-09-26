import pygame
import random

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 860
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
gameScreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Space Invaders")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
smallFont = pygame.font.Font(None, 50)


#region Player Class
class Player:
    def __init__(self, x = 640, y = 630, width = 50, height = 50, health = 20, speed = 15, damage = 1):
        self.rect = pygame.Rect((x, y, width, height))
        self.speed = speed
        self.damage = damage
        self.health = health
        self.cash = 0
        #Charge Shot
        self.charging = False
        self.chargingStart = 0
        self.lastShotTime = 0
        self.shotDelay = 300
        #Health & Immunity Frames
        self.alive = True
        self.immune = False
        self.immuneTime = 0
        self.immuneFrames = 1000

    def update(self, key, currentTime, paused):
        #Movement for player
        if paused:
            return
        if key[pygame.K_RCTRL] and key[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed / 2
        elif key[pygame.K_RCTRL] and key[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed / 2
        elif key[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        elif key[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        #Action for shooting
        #Charged Shot
        if key[pygame.K_w] and key[pygame.K_RSHIFT] and currentTime - self.lastShotTime >= self.shotDelay:
            if not self.charging:
                self.charging = True
                self.chargingStart = currentTime
        elif self.charging and (not key[pygame.K_w] or not key[pygame.K_RSHIFT]):
            self.charging = False 
            chargeDuration = currentTime - self.chargingStart
            fullyCharged = chargeDuration >= maxChargeTime
            chargedShotX = self.rect.centerx - bulletWidth
            chargedShotY = self.rect.top
            if fullyCharged:
                bullet.append(Bullet(chargedShotX, chargedShotY, bulletWidth, bulletHeight, 
                                    chargedShotSPD, chargedShotATK, color=(235, 180, 52), 
                                    direction = "N", charged=True))
                self.lastShotTime = currentTime
        #Normal shot
        elif key[pygame.K_w] and currentTime - self.lastShotTime >= self.shotDelay and not key[pygame.K_RSHIFT]:
            bulletX = self.rect.centerx - bulletWidth
            bulletY = self.rect.top
            bullet.append(Bullet(bulletX, bulletY, bulletWidth, bulletHeight, 
                                bulletSPD, self.damage, color=(255,255,255), direction = "N"))
            self.lastShotTime = currentTime
        if self.immune and currentTime - self.immuneTime >= self.immuneFrames:
            self.immune = False
    def takeDamage(self, amount, currentTime):
        if self.alive:
            if not self.immune:
                self.health -= amount
                self.immune = True
                self.immuneTime = currentTime
                if self.health <= 0:
                    self.health = 0
                    self.alive = False
                    #Send to Game Over Screen
    def draw(self, gameScreen):
        pygame.draw.rect(gameScreen, (0, 255, 0), self.rect)
#endregion
#Player code
player = Player()
currentLevel = 1

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
#region Bullet Classes
class Bullet:
    def __init__(self, x, y, width, height, speed, damage, color, direction = "N", charged = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.damage = damage
        self.color = color
        self.charged = charged
        self.direction = direction
    def update(self, paused):
        if paused:
            return
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

    def draw(self, gameScreen):
        pygame.draw.rect(gameScreen, self.color, self.rect)
class Laser(Bullet):
    def __init__(self, gunRect, width = 10, height = SCREEN_HEIGHT, speed = 1, damage = 2, color=(25,255,0), direction = "N", duration = 1000):
        self.gunRect = gunRect
        self.width = width
        self.speed = speed
        self.damage = damage
        self.rect = pygame.Rect(0, 0, width, height)
        self.color = color
        self.direction = direction
        self.spawnTime = pygame.time.get_ticks()
        self.duration = duration
        self.updatePosition()
    def updatePosition(self):
        self.rect.centerx = self.gunRect.centerx
        if self.direction == "S":
            self.rect.top = self.gunRect.bottom
            self.rect.height = SCREEN_HEIGHT - self.rect.top
        elif self.direction == "N":
            self.rect.bottom = self.gunRect.top
            self.rect.height = self.rect.bottom
    def update(self, currentTime, paused):
        if paused:
            return
        self.updatePosition()
        if currentTime - self.spawnTime >= self.duration:
            self.expired = True
    def draw(self, gameScreen):
        pygame.draw.rect(gameScreen, self.color, self.rect)
#endregion
#Enemy code
enemies = []
enemyBullets = []
enemyHP = 1
enemySPD = 3
enemyDelay = 1000
enemySpawnDelay = 2000
lastSpawnTime = 0
lastEnemyShotTime = 0
bosses = []
#region Enemy Classes
class Enemy:
    def __init__(self, x, y, width = 50, height = 50, health = enemyHP, speed = enemySPD, color = (255,0,0), damage = 1):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.color = color
        self.health = health
        self.damage = damage
    def update(self, paused):
        if paused:
            return
        self.rect.y += self.speed
    def draw(self, gameScreen):
        pygame.draw.rect(gameScreen, self.color, self.rect)
class Shooter(Enemy):
    def __init__(self, x, y, width = 60 , height = 30, health = 1, speed = enemySPD + 2):
        super().__init__(x, y, width, height, health, speed, color = (255,0,255))
        self.patrolY = 100 + random.randint(-20, 20)
        self.movingDown = True
        self.direction = 1 #-1 = Left/1 = Right
        self.cooldown = enemyDelay
        self.lastShot = lastEnemyShotTime
        self.damage = 1
    def update(self, currentTime, enemyBullets, player, paused):
        if paused:
            return
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
            if player and abs(self.rect.centerx - player.rect.centerx) < 100 + random.randint(-100,0):
                if currentTime - self.lastShot >= self.cooldown:
                    enemyBullets.append(Bullet(self.rect.centerx - 5, self.rect.bottom, 10, 20, 6, 1, 
                                               (255, 255, 0), direction = "S"))
                    self.lastShot = currentTime
class Charger(Enemy):
    def __init__(self, x, y, width = 40, height = 50, health = enemyHP + 1, speed = enemySPD + 4):
        super().__init__(x, y, width, height, health, speed, color = (255,165,0))
        self.damage = 2
    def update(self, player, paused):
        if paused:
            return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        #Normalize the vector to get more consistent speed
        distance = (dx * dx + dy * dy) ** 0.5
        if distance != 0:
            dx /= distance
        self.rect.x += int(dx * self.speed)
        self.rect.y += self.speed - 1
class Blocker(Enemy):
    def __init__(self, x, y, width = 70, height = 50, health = enemyHP * 4, speed = enemySPD):
        super().__init__(x, y, width, height, health, speed, color = (128, 128, 128))
        self.patrolY = 140 + random.randint(-20, 20)
        self.movingDown = True
        self.direction = 1 #-1 = Left/1 = Right
        self.damage = 0
    def update(self, paused):
        if paused:
            return
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
    def __init__(self, x, y, width = 50, height = 50, health = enemyHP, speed = enemySPD):
        super().__init__(x, y, width, height, health, speed, color = (172, 216, 230))
        self.type = random.choice(["T", "X"])
        self.damage = 1
    def update(self, paused):
        if paused:
            return
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
class Boss(Enemy):
    def __init__(self, x, y, width = 200, height = 150, health = 50, speed = enemySPD, color = (139,133,137)):
        super().__init__(x, y, width, height, health, speed, color)
        self.patrolY = 100
        self.movingDown = True
        self.alive = True
    def update(self, paused):
        if paused:
            return
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
    def draw(self, gameScreen):
        pygame.draw.rect(gameScreen, self.color, self.rect)

class BossShooterBlockerFusion(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, width = 200, height = 150, health= 50, speed = enemySPD + 1, color = (139, 133, 137))
        self.gunHealth = {"leftGun": 30, "rightGun": 30}
        self.gunOffset = {"leftGun": (0, 70), "rightGun": (self.rect.width - 30, 70)}
        self.guns = {gun: pygame.Rect(0,0, 30, 100) for gun in self.gunHealth}
        self.laserCooldown = 3000
        self.laserDuration = 1000
        self.lastLaserShot = 0
        self.firingLaser = False
        self.damage = 2
        self.direction = 1 #-1 = Left/1 = Right
        self.updateGuns(paused)
    def updateGuns(self, paused):
        if paused:
            return
        for gun, rect in self.guns.items():
            rect.x = self.rect.x + self.gunOffset[gun][0]
            rect.y = self.rect.y + self.gunOffset[gun][1]
    def update(self, currentTime, paused):
        super().update(paused)
        if paused:
            return
        if not self.movingDown:
            if self.firingLaser:
                if currentTime - self.lastLaserShot >= self.laserDuration:
                    self.firingLaser = False
            else:
                if currentTime - self.lastLaserShot >= self.laserCooldown:
                    self.fireLasers()
                    self.lastLaserShot = currentTime
                    self.firingLaser = True
            for gun, offset in self.gunOffset.items():
                self.guns[gun].topleft = (self.rect.x + offset[0], self.rect.y + offset[1])
    def fireLasers(self):        
            for gun, health in self.gunHealth.items():
                if health > 0:
                    laser = Laser(self.guns[gun], width = 10, height = SCREEN_HEIGHT, damage = self.damage, direction="S", duration=self.laserDuration)
                    enemyBullets.append(laser)

    def draw(self, gameScreen):
        super().draw(gameScreen)

        for gun, health in self.gunHealth.items():
            if health > 0:
                gunX = self.rect.x + self.gunOffset[gun][0]
                gunY = self.rect.y + self.gunOffset[gun][1]
                pygame.draw.rect(gameScreen, (0,0, 255), (gunX, gunY, 30, 100))
                
    def takeDamage(self, amount, gun = None, charged=False):
        if charged:
            amount *= 2
        if gun:
            if gun in self.gunHealth and self.gunHealth[gun] > 0:
                self.gunHealth[gun] -= amount
        else:
            self.health -= amount
        if all(hp <= 0 for hp in self.gunHealth.values()):
            self.alive = False
#endregion

#region HUD
def drawLeftHUD(gameScreen, font, health, cash, level):
    hudRect = pygame.Rect(10, gameScreen.get_height() -80, 200, 70)
    pygame.draw.rect(gameScreen, (50, 50, 50), hudRect)
    pygame.draw.rect(gameScreen, (200, 200, 200), hudRect, 2)
    textHealth = font.render(f"HP: {health}", True, (255, 0, 0))
    textCash = font.render(f"Cash: {cash}", True, (255, 255, 0))
    textLevel = font.render(f"Level: {level}", True, (0, 255, 0))
    gameScreen.blit(textHealth, (hudRect.x + 10, hudRect.y + 10))
    gameScreen.blit(textCash, (hudRect.x + 10, hudRect.y + 30))
    gameScreen.blit(textLevel, (hudRect.x + 10, hudRect.y + 50))
#endregion

#Game States: MainMenu Gameplay, How To Play, Map
state = "MainMenu"  #Where the game starts
selectedOption = 0
menu_options = ["Start Game", "How To Play", "Quit"]
paused = False

def drawMainMenu(selected):
    gameScreen.fill((0,0,0))

    #Title Screen
    title = font.render("Rogue Space Invaders", True, (255,255,255))
    gameScreen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    #Options
    for i, option in enumerate(menu_options):
        color = (255, 255, 0) if i == selected else (255, 255, 255)
        text = smallFont.render(option, True, color)
        gameScreen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 60))

def drawHowToPlay():
    gameScreen.fill((0,0,0))

    title = font.render("How To Play", True, (255,255,255))
    gameScreen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    controls = ["Move Left/Right: A / D", "Focus Movement: Hold RCtrl", "Shoot: W",
                "Charge Shot: Hold W & RShift, Release RShift when charged",
                "Pause: Esc"]
    enemyInfo = [("Basic", (255,0,0), "Moves straight down."),
                 ("Shooter", (255,0,255), "Patrols and shoots bullets."),
                 ("Charger", (255,165,0), "Charges towards you quickly."),
                 ("Blocker", (128,128,128), "Patrols and can only be damaged by Charged Shots."),
                 ("Combustion", (172,216,230), "Explodes into bullets when destroyed.")]
    y = 150
    for line in controls:
        text = smallFont.render(line, True, (200,200,200))
        gameScreen.blit(text, (50, y))
        y += 50
    for name, color, desc in enemyInfo:
        pygame.draw.rect(gameScreen, color, (50, y, 40, 40))
        text = smallFont.render(f"{name} - {desc}", True, (255,255,255))
        gameScreen.blit(text, (100, y + 5))
        y += 60
    backText = smallFont.render("Press ESC to return", True, (255, 255, 0))
    gameScreen.blit(backText, (SCREEN_WIDTH // 2 - backText.get_width() // 2, SCREEN_HEIGHT - 100))

#def drawPause():
        
bossSpawned = False
enemiesKilled = 0
def gameplay():
    global lastShotTime
    global lastSpawnTime
    global charging
    global chargingStart
    global maxChargeTime
    global currentTime
    global enemiesKilled
    global bossSpawned

    key = pygame.key.get_pressed()
    currentTime = pygame.time.get_ticks()
    
    #Only update if game isn't paused.
    player.update(key, currentTime, paused)
    #Update bullets
    for shot in bullet[:]:
            shot.update(paused)
            if shot.rect.bottom < 0:
                bullet.remove(shot)

    #Update enemies
    for enemy in enemies[:]:
        if isinstance(enemy, Shooter):
            enemy.update(currentTime, enemyBullets, player, paused)
        elif isinstance(enemy, Charger):
            enemy.update(player, paused)
            if enemy.rect.colliderect(player.rect):
                player.takeDamage(enemy.damage, currentTime)
        else:
            enemy.update(paused)
            if enemy.rect.colliderect(player.rect):
                player.takeDamage(enemy.damage, currentTime)

        if enemy.rect.top > SCREEN_HEIGHT:
            enemy.rect.y = -50
            enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)

    #Enemy & bosses gets hit by a bullet
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
                    enemiesKilled += 1
                break
    for boss in bosses[:]: 
        for shot in bullet[:]: 
            bulletRemoved = False 
            for gun, gunRect in boss.guns.items(): 
                if shot.rect.colliderect(gunRect): 
                    boss.takeDamage(shot.damage, gun, charged=shot.charged) 
                    bulletRemoved = True 
                    break 
                if not bulletRemoved and shot.rect.colliderect(boss.rect): 
                    boss.takeDamage(shot.damage, charged=shot.charged)
                    bulletRemoved = True
                #For incase a bullet hit both the boss and gun
                if bulletRemoved and shot in bullet:
                    bullet.remove(shot)
    #Enemy & boss spawning & which type
    if enemiesKilled >= 1 and not bossSpawned and not paused:
        boss = BossShooterBlockerFusion(SCREEN_WIDTH//2 - 75, -150)
        bosses.append(boss)
        bossSpawned = True
    elif currentTime - lastSpawnTime > enemySpawnDelay and (enemiesKilled < 1) and not paused:
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

    #Draws the player, bullets, enemies, and their bullets
    gameScreen.fill((0,0,0))
    if player.alive:
        player.draw(gameScreen)
    for shot in bullet:
        shot.draw(gameScreen)
    for enemy in enemies:
        enemy.draw(gameScreen)
    for enemyBull in enemyBullets[:]:
        if not paused:    
            if isinstance(enemyBull, Laser):
                enemyBull.update(currentTime, paused)
            else:
                enemyBull.update(paused)
        if getattr(enemyBull, "expired", False):
            enemyBullets.remove(enemyBull)
        if enemyBull.rect.top > SCREEN_HEIGHT or enemyBull.rect.bottom < 0 or enemyBull.rect.right < 0 or enemyBull.rect.left > SCREEN_WIDTH:
            enemyBullets.remove(enemyBull)
        elif enemyBull.rect.colliderect(player.rect):
            if isinstance(enemyBull, Laser):
                player.takeDamage(enemyBull.damage, currentTime)
            else:
                player.takeDamage(enemyBull.damage, currentTime)
                enemyBullets.remove(enemyBull)
        else:
            enemyBull.draw(gameScreen)
    for boss in bosses:
        if boss.alive:
            boss.update(currentTime, paused)
            boss.draw(gameScreen)
    drawLeftHUD(gameScreen, font, player.health, player.cash, currentLevel)
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
                        state = "How To Play"
                    elif selectedOption == 2:
                        run = False
        elif state == "Gameplay":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = "MainMenu"
    if state == "MainMenu":
        drawMainMenu(selectedOption)
    elif state == "Gameplay":
        gameplay()
    elif state == "How To Play":
        drawHowToPlay()

    if player.charging:
        if not paused:
            chargeDuration = currentTime - player.chargingStart
            progress = min(chargeDuration / maxChargeTime, 1.0)

        barWidth = player.rect.width
        barHeight = 8
        barX = player.rect.x
        barY = player.rect.bottom + 10

        pygame.draw.rect(gameScreen, (80, 80, 80), (barX, barY, barWidth, barHeight))
        pygame.draw.rect(gameScreen, (0, 200, 255), (barX, barY, int(barWidth * progress), barHeight))
    
    if state == "Gameplay" and paused:
        pauseFont = pygame.font.Font(None, 120)
        pauseText = pauseFont.render("PAUSED", True, (255,255,255))
        textRect = pauseText.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        gameScreen.blit(pauseText, textRect)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        gameScreen.blit(overlay, (0,0))
        gameScreen.blit(pauseText, textRect)

    windowWidth, windowHeight = screen.get_size()
    scale = min(windowWidth / SCREEN_WIDTH, windowHeight / SCREEN_HEIGHT)
    scaledWidth = int(SCREEN_WIDTH * scale)
    scaledHeight = int(SCREEN_HEIGHT * scale)
    scaledSurface = pygame.transform.scale(gameScreen, (scaledWidth, scaledHeight))
    xOffset = (windowWidth - scaledWidth) // 2
    yOffset = (windowHeight - scaledHeight) // 2
    screen.fill((255,255,255))
    screen.blit(scaledSurface, (xOffset, yOffset))

    pygame.display.flip()

pygame.quit()