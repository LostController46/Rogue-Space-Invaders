import pygame
import config
import bullets

PLAYER_IMG = pygame.image.load("images/player.png")

class Player():
    def __init__(self, x = 640, y = 700, health = 20, speed = 15, damage = 1, bulletList = []):
        self.image = pygame.transform.scale(PLAYER_IMG, (50, 50))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.baseStats = {
            "defenses": 
            {
                "maxHealth": health,               
                "reduction": 0,                       #Reduces damage taken
                "immuneFrames": 1000,                 #The higher it is the more immunity frames
                "regain": 0,                          #Regain health at the start of a level
                "extraLife": 0,                       #Survive death once
            },
            "combat" : 
            {
                "damage": damage,
                "chargeShotDamage" : damage * 2,  
                "shotDelay": 300,                     #The lower it is the faster the firing speed
                "chargeDelay": 300,                   #The lower it is the faster the charge
                "exploit": 0,                         #Increases damage enemies take
            },
            "extra": 
            {
                "speed": speed,
                "luck": 0,                            #Increases chances for rarer parts
            },
            "weaknesses":                           #Increases damage against this type of enemy
            {
                "basicWeak": False,                   
                "shooterWeak": False,
                "chargerWeak": False,
                "blockerWeak": False,
                "combustionWeak": False,
                "bossWeak": False
            }
}
        #Health & Immunity Frames
        self.maxHealth = health
        self.currentHealth = health
        self.reduction = 0
        self.immuneFrames = 1000
        self.immuneTime = 0
        self.regain = 0
        self.alive = True
        self.immune = False
        self.extraLife = 0
        #Damage Stats
        self.damage = damage
        self.chargeShotDamage = damage * 2
        #Extra Stats
        self.speed = speed
        self.luck = 0
        self.cash = 0
        self.parts = []
        #Exploit Enemy Weaknesses
        self.basicWeak = False
        self.shooterWeak = False
        self.chargerWeak = False
        self.blockerWeak = False
        self.combustionWeak = False
        self.bossWeak = False
        #Bullet & Weapons
        self.lastShotTime = 0
        self.shotDelay = 300
        self.chargeDelay = 300
        self.charging = False
        self.chargingStart = 0
        self.currentWeapon = 0  #Bullet is weapon 0
        self.bulletList = bulletList
        #Currently Paused
        self.pause = False
        #Upgrades
        self.partAdditions = 0
        self.partMulti = 0.0
        #Shop Upgrades
        self.shipUpgrades = [
            {
                "name": "Ship Max Health",
                "statType": "defense",
                "LVL" : 1,
                "maxLevel": 5,
                "cost": 30,
                "type": "maxHealth",
                "description": "Increases max health of ship."
            },
            {
                "name": "Ship Speed",
                "statType": "extra",
                "LVL" : 1,
                "maxLevel": 3,
                "cost": 20,
                "type": "speed",
                "description": "Increases speed of ship."
            },
            {
                "name": "Bullet Upgrade",
                "statType": "combat",
                "LVL" : 1,
                "maxLevel": 3,
                "cost": 30,
                "type": "bulletDamage",
                "description": "Increases damage of bullets."
            },
            {
                "name": "Laser Upgrade",
                "statType": "combat",
                "LVL" : 0,
                "maxLevel": 3,
                "cost": 50,
                "type": "laserDamage",
                "description": "Increases damage of laser. NOT IMPLEMENTED"
            },
            {
                "name": "Missile Upgrade",
                "statType": "combat",
                "LVL" : 0,
                "maxLevel": 3,
                "cost": 50,
                "type": "missileDamage",
                "description": "Increases damage of missiles. NOT IMPLEMENTED"
            }]

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
        if key[pygame.K_w] and key[pygame.K_RSHIFT] and currentTime - self.lastShotTime >= self.chargeDelay:
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
                                    bullets.chargedShotSPD, self.chargeShotDamage, color=(235, 180, 52), 
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
                self.currentHealth -= amount
                self.immune = True
                self.immuneTime = currentTime
                if self.currentHealth <= 0:
                    self.currentHealth = 0
                    self.alive = False
                    #Send to Game Over Screen
    def partCollected(self, part):
        self.parts.append(part)
        self.updateStats()
    def updateStats(self):
        base = self.baseStats
        #Reset all stats (can probably loop this)
        self.currentHealth = base["defenses"]["maxHealth"]
        self.reduction = base["defenses"]["reduction"]
        self.immuneFrames = base["defenses"]["immuneFrames"]
        self.regain = base["defenses"]["regain"]
        self.extraLife = base["defenses"]["extraLife"]
        self.damage = base["combat"]["damage"]
        self.chargeShotDamage = base["combat"]["chargeShotDamage"]
        self.shotDelay = base["combat"]["shotDelay"]
        self.chargeDelay = base["combat"]["chargeDelay"]
        self.exploit = base["combat"]["exploit"]
        self.speed = base["extra"]["speed"]
        self.luck = base["extra"]["luck"]
        for key, val in base["weaknesses"].items():
            setattr(self, key, val)
        #Apply upgrades from Shop Upgrades

        #Apply stats from Parts
        for part in self.parts:
            part.upgrade(self)
    def draw(self, gameScreen):
        gameScreen.blit(self.image, self.rect)
    def printStats(self):
        print("----- PLAYER STATS -----")
        print(f"Speed: {self.speed}")
        print(f"Fire Rate: {self.shotDelay}")
        print(f"Damage: {self.damage}")
        print("-------------------------")