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
                "chargingSpeed": 1000,                #The lower it is the faster the charge
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
        self.chargingSpeed = 1000
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
        #Sabotage Upgrades
        self.saboUpgrades = [
            {
                "name": "Faulty Manufacturing",
                "type": "health",
                "LVL" : 0,
                "maxLevel": 5,
                "cost": 30,
                "description": "Lowers the max health of enemies."
            },
            {
                "name": "Slow Suppy Lines",
                "type": "enemySpawnDelay",
                "LVL" : 0,
                "maxLevel": 3,
                "cost": 50,
                "description": "Increases the delay for enemy spawns."
            },
            {
                "name": "Tampered Boosters",
                "type": "speed",
                "LVL" : 0,
                "maxLevel": 3,
                "cost": 40,
                "description": "Decreases the movement speed of enemies."
            },
            {
                "name": "Weak Ammunition",
                "type": "damage",
                "LVL" : 0,
                "maxLevel": 3,
                "cost": 50,
                "description": "Decreases the damage of enemies."
            },
            {
                "name": "Worthy Scrap",
                "type": "worth",
                "LVL" : 0,
                "maxLevel": 3,
                "cost": 100,
                "description": "Increases the worth of enemies."
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
        if key[pygame.K_w] and key[pygame.K_RSHIFT] and currentTime - self.lastShotTime >= self.shotDelay:
            if not self.charging:
                self.charging = True
                self.chargingStart = currentTime
        elif self.charging and (not key[pygame.K_w] or not key[pygame.K_RSHIFT]):
            self.charging = False 
            chargeDuration = currentTime - self.chargingStart
            fullyCharged = chargeDuration >= self.chargingSpeed
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
    def takeDamage(self, amount, currentTime, collision):
        if self.alive:
            if not self.immune:
                self.immune = True
                self.immuneTime = currentTime
                if collision:
                    self.currentHealth -= max(1, (amount + self.reduction))
                else:
                    self.currentHealth -= amount
                if self.currentHealth <= 0:
                    self.currentHealth = 0
                    self.alive = False
                    #Send to Game Over Screen
    def partCollected(self, part):
        self.parts.append(part)
        self.updateStats()
    def updateStats(self):
        base = self.baseStats
        #Reset all stats
        for category in ["defenses", "combat", "extra", "weaknesses"]:
            for key, value in base[category].items():
                setattr(self, key, value)
        #Apply upgrades from Shop Upgrades
        for upgrade in self.shipUpgrades:
            lvl = upgrade["LVL"]
            if lvl > 0:
                statType = upgrade["statType"]
                statName = upgrade["type"]
                if statName == "maxHealth":
                    self.maxHealth += 10 * (lvl - 1)
                elif statName == "speed":
                    self.speed += 0.5 * (lvl - 1)
                elif statName == "bulletDamage":
                    self.damage += 1 * (lvl - 1)
        #Apply stats from Parts
        for part in self.parts:
            part.upgrade(self)
    def draw(self, gameScreen):
        gameScreen.blit(self.image, self.rect)
    #Enemy Sabotage Calls
    def getSabotageLevel(self, saboType):
        for sabo in self.saboUpgrades:
            if sabo["type"] == saboType:
                return sabo["LVL"]
        return 0
    def getEnemyHealthSabo(self):
        lvl = self.getSabotageLevel("health")
        return -lvl
    def getEnemySpeedSabo(self):
        lvl = self.getSabotageLevel("speed")
        return -lvl
    def getEnemyDamageSabo(self):
        lvl = self.getSabotageLevel("damage")
        return -lvl
    def getEnemyWorthSabo(self):
        lvl = self.getSabotageLevel("worth")
        return lvl
    def getEnemyDelaySabo(self):
        lvl = self.getSabotageLevel("enemySpawnDelay")
        return lvl * 1000