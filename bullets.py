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
    def update(self, currentTime, paused):
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
    def __init__(self, gunRect, width = 10, height = config.SCREEN_HEIGHT, speed = 1, damage = 2, color=(25,255,0), direction = "N", duration = 1000, currentTime = None, charged = True):
        self.gunRect = gunRect
        self.width = width
        self.speed = speed
        self.damage = damage
        self.rect = pygame.Rect(0, 0, width, height)
        self.color = color
        self.charged = charged
        self.direction = direction
        now = pygame.time.get_ticks() if currentTime is None else currentTime
        self.spawnTime = now
        self.duration = duration
        self.timer = now
        self.activeTime = 0
        self.expired = False
        self.updatePosition()
    def updatePosition(self):
        self.rect.centerx = self.gunRect.centerx
        if self.direction == "S":
            self.rect.top = self.gunRect.bottom
            self.rect.height = config.SCREEN_HEIGHT - self.rect.top
        elif self.direction == "N":
            self.rect.bottom = self.gunRect.top
            self.rect.top = 0
            self.rect.height = self.gunRect.top
    def update(self, currentTime, paused):
        if paused:
            return
        if currentTime < self.timer:
            self.timer = currentTime
        delta = currentTime - self.timer
        self.timer = currentTime
        self.updatePosition()
        self.activeTime += delta
        if self.activeTime >= self.duration:
            self.expired = True
    def draw(self, gameScreen):
        pygame.draw.rect(gameScreen, self.color, self.rect)
class LaserAfterimage(Laser):
    def __init__ (self, originalLaser, duration = 500, charged = False):
        self.rect = originalLaser.rect.copy()
        self.color = originalLaser.color
        self.direction = originalLaser.direction
        self.charged = charged
        self.drift = 2
        self.duration = duration
        self.timer = duration
        self.spawnTime = pygame.time.get_ticks()
        self.velocity = 0
        self.damage = 0
        self.alpha = 255
    def update(self, currentTime, paused):
        if paused:
            return
        elapsed = currentTime - self.spawnTime
        remaining = max(0, self.duration - elapsed)
        self.timer = remaining
        if remaining <= 0:
            self.alpha = 0
        else:
            self.alpha = int(255 * (remaining / self.duration))
        if self.direction == "N":
            self.rect.y -= self.drift
        elif self.direction == "S":
            self.rect.y += self.drift
    def draw(self, gameScreen):
        #Give laser a transparent surface and apply the alpha
        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        surf.fill((*self.color, self.alpha))
        gameScreen.blit(surf, self.rect)
class Missile(Bullet):
    def __init__(self, x, y, targets, width = 20, height = 20, speed = 10, damage = 2, color = (255, 255, 255), duration = 10000, currentTime = None, charged = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.damage = damage
        self.color = color
        self.duration = duration
        now = pygame.time.get_ticks() if currentTime is None else currentTime
        self.spawnTime = now
        self.expired = False
        self.timer = now
        self.target = targets
        self.charged = charged
        self.activeTime = 0
    def updatePosition(self):
        if not self.target:
            return
        target = self.target[0]
        if not target:
            return
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        #Normalize the vector to get more consistent speed
        distance = (dx * dx + dy * dy) ** 0.5
        if distance != 0:
            dx /= distance
            dy /= distance
        self.rect.x += int(dx * self.speed)
        self.rect.y += int(dy * self.speed)

    def update(self, currentTime, paused):
        if paused:
            return
        if currentTime < self.timer:
            self.timer = currentTime
        delta = currentTime - self.timer
        self.timer = currentTime
        self.updatePosition()
        self.activeTime += delta
        if self.activeTime >= self.duration:
            self.expired = True
    def draw(self, gameScreen):
        pygame.draw.rect(gameScreen, self.color, self.rect)