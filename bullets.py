import config
import pygame

bulletATK = config.bulletATK
enemyBulletATK = config.bulletATK
bulletSPD = config.bulletSPD
bulletWidth = config.bulletWidth
bulletHeight = config.bulletHeight
shotDelay = config.shotDelay
lastShotTime = config.lastShotTime
chargedShotATK = config.bulletATK * 2
chargedShotSPD = config.chargedShotSPD
charging = config.charging
chargingStart = config.chargingStart
maxChargeTime = config.maxChargeTime

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
    def __init__(self, gunRect, width = 10, height = config.SCREEN_HEIGHT, speed = 1, damage = 2, color=(25,255,0), direction = "N", duration = 1000):
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
            self.rect.height = config.SCREEN_HEIGHT - self.rect.top
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