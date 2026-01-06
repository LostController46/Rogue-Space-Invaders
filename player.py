from resourceLoader import resourcePath
import pygame
import config
import bullets

PLAYER_IMG = pygame.image.load(resourcePath("images/player.png"))

#Sound Control
pygame.mixer.init()
bulletShot = pygame.mixer.Sound(resourcePath("sounds/bulletShot.wav"))
laserShot = pygame.mixer.Sound(resourcePath("sounds/laserShot.wav"))
missileShot = pygame.mixer.Sound(resourcePath("sounds/missileShot.wav"))
playerHurt = pygame.mixer.Sound(resourcePath("sounds/playerHurt.wav"))
playerCollide = pygame.mixer.Sound(resourcePath("sounds/playerCollide.wav"))

class Player():
    def __init__(self, x = 640, y = 700, health = 20, speed = 15, damage = 1, bulletList = []):
        self.image = pygame.transform.scale(PLAYER_IMG, (50, 50))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.currentLevel = 1
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
                "damage": 0,                          #Universal damage increase
                "bulletDamage": damage,
                "chargeShotDamage" : damage * 2,
                "laserDamage": 4,
                "missileDamage": 2,
                "thornsDamage": 0,
                "shotDelay": 300,                     #The lower it is the faster the firing speed
                "chargingSpeed": 800,                #The lower it is the faster the charge
                "laserChargeSpeed": 2000,             #The lower it is the faster the charge speed
                "laserCooldown": 1300,                #The lower it is the faster the cooldown
                "missileCooldown": 2000,              #The lower it is the faster the cooldown
                "missileDuration": 3000,              #The high it is the longer the missiles last
                "missileSpeed": 10,
                "dualLauncher": False,
            },
            "extra": 
            {
                "speed": speed,
                "luck": 0,                            #Increases chances for rarer parts
                "jammed": 0,
                "thorns": False,                     #Enemies, take damage when colliding with you.
                "lifesteal": False
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
        self.damage = 0
        self.bulletDamage = damage
        self.chargeShotDamage = damage * 2
        self.laserDamage = 4
        self.missileDamage = 2
        self.thornsDamage = 0
        #Extra Stats
        self.speed = speed
        self.luck = 0
        self.cash = 5
        self.jammed = 0
        self.thorns = False
        self.lifesteal = False
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
        self.chargingSpeed = 800
        self.charging = False
        self.chargingStart = 0
        self.laserChargeSpeed = 2000
        self.laserCooldown = 1300
        self.missileCooldown = 2000
        self.missileDuration = 3000
        self.missileSpeed = 10
        self.dualLauncher = False
        self.currentWeaponIndex = 0  #Bullet is weapon 0
        self.bulletList = bulletList
        self.weaponList = ["Bullet"]
        self.currentWeapon = self.weaponList[self.currentWeaponIndex]
        self.lastWeaponSwitchTime = 0
        #Currently Paused
        self.pause = False
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
                "description": "Increases damage of laser."
            },
            {
                "name": "Missile Upgrade",
                "statType": "combat",
                "LVL" : 0,
                "maxLevel": 3,
                "cost": 50,
                "type": "missileDamage",
                "description": "Increases damage of missiles."
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

    def update(self, key, currentTime, paused, enemyList = None, bossList = None):
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
        #Swap weapons
        if key[pygame.K_PERIOD] and currentTime - self.lastWeaponSwitchTime > 300:
            if len(self.weaponList) > 1:
                self.currentWeaponIndex = (self.currentWeaponIndex + 1) % len(self.weaponList)
                self.currentWeapon = self.weaponList[self.currentWeaponIndex]
            self.lastWeaponSwitchTime = currentTime

        #Charged Shot
        if self.currentWeapon == "Bullet":
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
                                        bullets.chargedShotSPD, (self.chargeShotDamage + self.damage), color=(235, 180, 52), 
                                        direction = "N", charged=True))
                    self.lastShotTime = currentTime
            #Normal shot
            elif key[pygame.K_w] and currentTime - self.lastShotTime >= self.shotDelay and not key[pygame.K_RSHIFT]:
                bulletX = self.rect.centerx - bullets.bulletWidth
                bulletY = self.rect.top
                self.bulletList.append(bullets.Bullet(bulletX, bulletY, bullets.bulletWidth, bullets.bulletHeight, 
                                    bullets.bulletSPD, (self.bulletDamage + self.damage), color=(255,255,255), direction = "N"))
                bulletShot.play(maxtime = 500)
                self.lastShotTime = currentTime
        elif self.currentWeapon == "Laser":
            if key[pygame.K_w]:
                if not self.charging:
                    self.charging = True
                    self.chargingStart = currentTime
                    #print("Started charging laser")
            else:
                if self.charging:
                    self.charging = False
                    chargeDuration = currentTime - self.chargingStart
                    fullyCharged = chargeDuration >= self.laserChargeSpeed
                    #print("Released laser key", chargeDuration, fullyCharged)
                    if fullyCharged and currentTime - self.lastShotTime >= self.laserCooldown:
                        self.bulletList.append(bullets.Laser(self.rect, damage=(self.laserDamage + self.damage), direction = "N", currentTime = currentTime, charged= True))
                        laserShot.play(maxtime = 1000)
                        self.lastShotTime = currentTime
        elif self.currentWeapon == "Missile":
            if key[pygame.K_w] and currentTime - self.lastShotTime >= self.missileCooldown:
                offset = 10
                missileY = self.rect.top

                #Left Missile
                self.bulletList.append(bullets.Missile(self.rect.centerx - offset, missileY, (enemyList or []) + (bossList or []), speed = self.missileSpeed, damage=(self.missileDamage + self.damage), 
                                    color= (255, 180, 100), duration = self.missileDuration, currentTime = currentTime))
                #Extra Missiles
                if self.dualLauncher:
                    self.bulletList.append(bullets.Missile(self.rect.centerx - (offset * 2), missileY, (enemyList or []) + (bossList or []), speed = self.missileSpeed, damage=(self.missileDamage + self.damage), 
                                    color= (255, 180, 100), duration = self.missileDuration, currentTime = currentTime))
                #Right Missile
                self.bulletList.append(bullets.Missile(self.rect.centerx + offset, missileY, (enemyList or []) + (bossList or []), speed = self.missileSpeed, damage=(self.missileDamage + self.damage), 
                                    color= (255, 180, 100), duration = self.missileDuration, currentTime = currentTime))
                #Extra Missiles
                if self.dualLauncher:
                    self.bulletList.append(bullets.Missile(self.rect.centerx + (offset * 2), missileY, (enemyList or []) + (bossList or []), speed = self.missileSpeed, damage=(self.missileDamage + self.damage), 
                                    color= (255, 180, 100), duration = self.missileDuration, currentTime = currentTime))
                missileShot.play(maxtime = 1500)
                self.lastShotTime = currentTime
        if self.immune and currentTime - self.immuneTime >= self.immuneFrames:
            self.immune = False
    def takeDamage(self, amount, currentTime, collision):
        if self.alive:
            if not self.immune:
                self.immune = True
                self.immuneTime = currentTime
                if collision:
                    #Quick check to not play if taking no damage (After Images of Lasers)
                    if amount > 0:
                        playerCollide.play(maxtime = 1000)
                    self.currentHealth -= max(1, (amount + self.reduction))
                else:
                    #Quick check to not play if taking no damage (After Images of Lasers)
                    if amount > 0:
                        playerHurt.play(maxtime = 1000)
                    self.currentHealth -= amount
                if self.currentHealth <= 0:
                    #If you have a life give half health back to the player
                    if self.extraLife > 0:
                        self.currentHealth = self.maxHealth // 2
                        self.extraLife -= 1

                        #Remove Insert Token if used. Modify for other extra life mechanics
                        for part in self.parts:
                            if part.name == "Insert Token":
                                self.parts.remove(part)
                                break
                    else:
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
                    self.bulletDamage += (lvl - 1)
                elif statName == "laserDamage":
                    self.laserDamage += lvl
                elif statName == "missileDamage":
                    self.missileDamage += lvl
        #print("RESET bulletDamage =", self.bulletDamage)
        #print("RESET laserDamage =", self.laserDamage)
        #print("RESET missileDamage =", self.missileDamage)
        #print("RESET damage =", self.damage)
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