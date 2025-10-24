import pygame
import random
import config
import bullets

BASIC_IMG = pygame.image.load("images/Basic.png")
SHOOTER_IMG = pygame.image.load("images/Shooter.png")
CHARGER_IMG = pygame.image.load("images/Charger.png")

enemyHP = config.enemyHP
enemySPD = config.enemySPD
enemyDelay = config.enemyDelay
enemySpawnDelay = config.enemySpawnDelay
lastSpawnTime = config.lastSpawnTime
lastEnemyShotTime = config.lastEnemyShotTime
enemyWorth = config.enemyWorth
bossWorth = config.bossWorth

class Enemy:
    def __init__(self, x, y, width = 50 , height = 50, health = enemyHP, speed = enemySPD, color = (255,0,0), damage = 1):
        self.image = pygame.transform.scale(BASIC_IMG, (width, height))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = speed
        self.color = color
        self.health = health
        self.damage = damage
        self.worth = enemyWorth
    def update(self, paused):
        if paused:
            return
        self.rect.y += self.speed
    def draw(self, gameScreen):
        gameScreen.blit(self.image, self.rect)
class Shooter(Enemy):
    def __init__(self, x, y, width = 60 , height = 30, health = 1, speed = enemySPD + 2):
        super().__init__(x, y, width, height, health, speed, color = (255,0,255))
        self.image = pygame.transform.scale(SHOOTER_IMG, (width, height))
        self.rect = self.image.get_rect(topleft=(x,y))
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
            if self.rect.right >= config.SCREEN_WIDTH:
                self.rect.right = config.SCREEN_WIDTH
                self.direction = -1
            elif self.rect.left <= 0:
                self.rect.left = 0
                self.direction = 1
            #Only shoots when the player is near enough with some variance
            if player and abs(self.rect.centerx - player.rect.centerx) < 100 + random.randint(-100,0):
                if currentTime - self.lastShot >= self.cooldown:
                    enemyBullets.append(bullets.Bullet(self.rect.centerx - 5, self.rect.bottom, 10, 20, 6, 1, 
                                               (255, 255, 0), direction = "S"))
                    self.lastShot = currentTime
class Charger(Enemy):
    def __init__(self, x, y, width = 40, height = 50, health = enemyHP + 1, speed = enemySPD + 4):
        super().__init__(x, y, width, height, health, speed, color = (255,165,0))
        self.image = pygame.transform.scale(CHARGER_IMG, (width, height))
        self.rect = self.image.get_rect(topleft=(x,y))
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
            if self.rect.right >= config.SCREEN_WIDTH:
                self.rect.right = config.SCREEN_WIDTH
                self.direction = -1
            elif self.rect.left <= 0:
                self.rect.left = 0
                self.direction = 1
    def takeDamage(self, damage, player, charged = False):
        if charged and player.blockerWeak:
            self.health -= damage * 2
        elif charged:
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
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="N"))
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="S"))
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="E"))
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="W"))
        elif self.type == "X":
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="NE"))
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="NW"))
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="SE"))
            enemyBullets.append(bullets.Bullet(self.rect.centerx, self.rect.centery, 10, 10, 6, 1, (255,200,0), direction="SW"))
class Boss(Enemy):
    def __init__(self, x, y, width = 200, height = 150, health = 50, speed = enemySPD, color = (139,133,137)):
        super().__init__(x, y, width, height, health, speed, color)
        self.patrolY = 100
        self.movingDown = True
        self.alive = True
        self.worth = bossWorth
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
            if self.rect.right >= config.SCREEN_WIDTH:
                self.rect.right = config.SCREEN_WIDTH
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
        self.lastLaserShot = pygame.time.get_ticks()
        self.laserActiveTime = 0
        self.timer = pygame.time.get_ticks()
        self.firingLaser = False
        self.damage = 2
        self.direction = 1 #-1 = Left/1 = Right
        self.updateGuns(False)
    def updateGuns(self, paused):
        if paused:
            return
        for gun, rect in self.guns.items():
            rect.x = self.rect.x + self.gunOffset[gun][0]
            rect.y = self.rect.y + self.gunOffset[gun][1]
    def update(self, currentTime, paused, enemyBullets):
        super().update(paused)
        if paused:
            return
        delta = currentTime - self.timer
        self.timer = currentTime
        if not self.movingDown:
            if self.firingLaser:
                self.laserActiveTime += delta
                if self.laserActiveTime >= self.laserDuration:
                    self.firingLaser = False
                    self.lastLaserShot = currentTime
                    self.laserActiveTime = 0
            else:
                if currentTime - self.lastLaserShot >= self.laserCooldown:
                    self.fireLasers(enemyBullets, currentTime)
                    self.firingLaser = True
                    self.laserActiveTime = 0
            for gun, offset in self.gunOffset.items():
                self.guns[gun].topleft = (self.rect.x + offset[0], self.rect.y + offset[1])
    def fireLasers(self, enemyBullets, currentTime):        
            for gun, health in self.gunHealth.items():
                if health > 0:
                    laser = bullets.Laser(self.guns[gun], width = 10, height = config.SCREEN_HEIGHT, damage = self.damage, direction="S", duration=self.laserDuration, currentTime = currentTime)
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