import pygame
import random

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Space Invaders")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
smallFont = pygame.font.Font(None, 50)


#Player code
playerSPD = 15
playerATK = 1
player = pygame.Rect((300, 500, 50, 50))

#Bullet code
bullet = []
bulletSPD = 20
BulletWidth = 10
BulletHeight = 30
shotDelay = 300
lastShotTime = 0

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
            elif self.rect.left <=0:
                self.rect.left = 0
                self.direction = 1
            #Only shoots when the player is near enough with some variance
            if player and abs(self.rect.centerx - player.centerx) < 100 + random.randint(-90,0):
                if currentTime - self.lastShot >= self.cooldown:
                    bullet = pygame.Rect(self.rect.centerx - 5, self.rect.bottom, 10, 20)
                    enemyBullets.append(bullet)
                    self.lastShot = currentTime

#Enemy Types
enemyBasic = 0
enemyShooter = 1
enemyCharger = 2
enemyBlocker = 3
enemyCombustionT = 4
enemyCombustionX = 5
boss = 23


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
    key = pygame.key.get_pressed()
    currentTime = pygame.time.get_ticks()

    #Movement for player
    if key[pygame.K_a] and player.left > 0:
        player.x -= playerSPD
    elif key[pygame.K_d] and player.right < SCREEN_WIDTH:
        player.x += playerSPD
    
    #Action for shooting
    elif key[pygame.K_w] and currentTime - lastShotTime >= shotDelay:
        bulletX = player.centerx - BulletWidth
        bulletY = player.top
        bullet.append(pygame.Rect(bulletX, bulletY, BulletWidth, BulletHeight))
        lastShotTime = currentTime

    #Update bullets
    for shot in bullet[:]:
            shot.y -= bulletSPD
            if shot.bottom < 0:
                bullet.remove(shot)

    #Update enemies
    for enemy in enemies[:]:
        if isinstance(enemy, Shooter):
            enemy.update(currentTime, enemyBullets, player)
        else:
            enemy.update()

        if enemy.rect.top > SCREEN_HEIGHT:
            enemy.rect.y = -50
            enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)

    #Enemy gets hit by a bullet
    for enemy in enemies[:]:
        for shot in bullet[:]:
            if enemy.rect.colliderect(shot):
                bullet.remove(shot)
                enemy.health -= 1
                if enemy.health <= 0:
                    enemies.remove(enemy)
                break

    #Draws the player, bullets, enemies, and their bullets
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (0, 255, 0), player)
    for shot in bullet:
        pygame.draw.rect(screen, (255, 255, 255), shot)
    for enemy in enemies:
        enemy.draw(screen)
    for enemyBull in enemyBullets[:]:
        enemyBull.y += 5
        if enemyBull.top > SCREEN_HEIGHT:
            enemyBullets.remove(enemyBull)
        else:
            pygame.draw.rect(screen, (255, 255, 0), enemyBull)

    #Enemy spawning & which type
    if currentTime - lastSpawnTime > enemySpawnDelay:
        enemyX = random.randint(0, SCREEN_WIDTH - 50)
        enemyType = random.choice(["Basic", "Shooter"])    #add other enemies here

        if enemyType == "Basic":
            #The -50 for the Y makes it so the enemy spawns offscreen before being shown.
            enemies.append(Enemy(enemyX, -50))
        elif enemyType == "Shooter":
            enemies.append(Shooter(enemyX, -50))
        
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
    pygame.display.update()

pygame.quit()