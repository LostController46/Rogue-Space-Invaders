import pygame
import config
import bullets

class Player():
    def __init__(self, x = 640, y = 630, width = 50, height = 50, health = 20, speed = 15, damage = 1, bulletList = []):
        self.rect = pygame.Rect((x, y, width, height))
        self.speed = speed
        self.damage = damage
        self.health = health
        self.cash = 0
        self.currentWeapon = 0  #Bullet is weapon 0
        self.bulletList = bulletList
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
        #Currently Paused
        self.pause = False

    def update(self, key, currentTime, paused):
        #Movement for player
        self.pause = paused
        if paused:
            return
        if key[pygame.K_RCTRL] and key[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed / 2
        elif key[pygame.K_RCTRL] and key[pygame.K_d] and self.rect.right < config.SCREEN_WIDTH:
            self.rect.x += self.speed / 2
        elif key[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        elif key[pygame.K_d] and self.rect.right < config.SCREEN_WIDTH:
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
            fullyCharged = chargeDuration >= bullets.maxChargeTime
            chargedShotX = self.rect.centerx - bullets.bulletWidth
            chargedShotY = self.rect.top
            if fullyCharged:
                self.bulletList.append(bullets.Bullet(chargedShotX, chargedShotY, bullets.bulletWidth, bullets.bulletHeight, 
                                    bullets.chargedShotSPD, bullets.chargedShotATK, color=(235, 180, 52), 
                                    direction = "N", charged=True))
                self.lastShotTime = currentTime
        #Normal shot
        elif key[pygame.K_w] and currentTime - self.lastShotTime >= self.shotDelay and not key[pygame.K_RSHIFT]:
            bulletX = self.rect.centerx - bullets.bulletWidth
            bulletY = self.rect.top
            self.bulletList.append(bullets.Bullet(bulletX, bulletY, bullets.bulletWidth, bullets.bulletHeight, 
                                bullets.bulletSPD, self.damage, color=(255,255,255), direction = "N"))
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