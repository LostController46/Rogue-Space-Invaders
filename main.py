import pygame
import random
import player
import bullets
import attackers

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 860
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
gameScreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Space Invaders")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
smallFont = pygame.font.Font(None, 50)
enemyLeftFont = pygame.font.Font(None, 32)
levelFont = pygame.font.Font(None, 20)

#Bullet code
bullet = []

#Player code
gamer = player.Player(bulletList = bullet)
currentLevel = 1
gameOverTime = None
gameStartTime = pygame.time.get_ticks()
pauseStartTime = None
pausedTimeAccumulated = 0

#Enemy code
enemies = []
enemyBullets = []
bosses = []
bossSpawned = False
enemiesKilled = 0
enemiesLeft = 0
enemiesDecided = False

#Map Control
mapCreated = False
nodePositions = {}

#Game Time
def getGameTime():
    if paused and pauseStartTime is not None:
        return pauseStartTime - pausedTimeAccumulated
    return pygame.time.get_ticks() - pausedTimeAccumulated
#region HUD
def drawLeftHUD(gameScreen, font, health, cash, level, enemiesLeft, enemiesKilled):
    hudRect = pygame.Rect(0, gameScreen.get_height() - 160, 200, 160)
    pygame.draw.rect(gameScreen, (50, 50, 50), hudRect)
    pygame.draw.rect(gameScreen, (200, 200, 200), hudRect, 2)
    textHealth = font.render(f"HP: {health}", True, (255, 0, 0))
    textCash = font.render(f"Cash: {cash}", True, (255, 255, 0))
    textLevel = font.render(f"Level: {level}", True, (0, 255, 0))
    gameScreen.blit(textHealth, (hudRect.x + 5, hudRect.y + 10))
    gameScreen.blit(textCash, (hudRect.x + 5, hudRect.y + 60))
    gameScreen.blit(textLevel, (hudRect.x + 5, hudRect.y + 110))
    #Enemy HUD
    enemiesRemain = enemiesLeft - enemiesKilled
    enemyHudRect = pygame.Rect(0, 0, 200, 50)
    pygame.draw.rect(gameScreen, (50, 50, 50), enemyHudRect)
    pygame.draw.rect(gameScreen, (200, 200, 200), enemyHudRect, 2)
    textEnemiesLeft = enemyLeftFont.render(f"Enemies Left: {enemiesRemain}", True, (255, 255, 255))
    gameScreen.blit(textEnemiesLeft, (enemyHudRect.x + 5, enemyHudRect.y + 10))
def drawMiddleHUD(screen, font):
    hudRect = pygame.Rect(200, screen.get_height() - 160, 960, 160)
    pygame.draw.rect(gameScreen, (50, 50, 50), hudRect)
    pygame.draw.rect(gameScreen, (200, 200, 200), hudRect, 2)
    text = font.render("Parts: [not implemented]", True, (200, 200, 200))
    screen.blit(text, (hudRect.x + 10, hudRect.y + 30))
def drawRightHUD(screen, font, weapons, currentWeaponIndex):
    hudRect = pygame.Rect(gameScreen.get_width() - 200, gameScreen.get_height() - 160, 200, 160)
    pygame.draw.rect(gameScreen, (50, 50, 50), hudRect)
    pygame.draw.rect(gameScreen, (200, 200, 200), hudRect, 2)
    for i, weapon in enumerate(weapons):
        color = (0, 255, 0) if i == currentWeaponIndex else (200,200,200)
        text = font.render(weapon, True, color)
        screen.blit(text, (hudRect.right - text.get_width() - 5, hudRect.y + 10 + i * 50))
#endregion


#region Map Logic
#
#       Boss
#         |
#        L13
#      /     \
#    L11     L12
#   /  \    /   \
#  L7  L8  L9   L10
#   \   |   |   /
#    L3 L4 L5 L6
#     \ |   | /
#      L1   L2
#       \   /
#       Start
MAP_GRAPH = {"Start": ["L1", "L2"],
             "L1":    ["L3", "L4"],
             "L2":    ["L5", "L6"],
             "L3":    ["L7"],
             "L4":    ["L8"],
             "L5":    ["L9"],
             "L6":    ["L10"],
             "L7":    ["L11"],
             "L8":    ["L11"],
             "L9":    ["L12"],
             "L10":   ["L12"],
             "L11":   ["L13"],
             "L12":   ["L13"],
             "L13":   ["Boss"],
             "Boss":  []

}
currentLevel = "Start"

def getNextLevel(node):
    return MAP_GRAPH.get(node, [])
def generateLevel():
    global LEVEL_DATA
    LEVEL_DATA = {}
    HORDE_SIZE = ["Small", "Medium", "Large", "Massive"]
    ENEMY_TYPES =["Basic", "Shooter", "Blocker", "Charger", "Combustion"]
    REWARDS = ["Part", "Heal", "Shop"]
    for node in MAP_GRAPH.keys():
        if node == "Start":
            LEVEL_DATA[node] = {"Horde": None, "Enemies": [], "Reward": None}
        elif node == "Boss":
            LEVEL_DATA[node] = {"Horde": "Massive", "enemies": ENEMY_TYPES, "reward": "BOSS_PART"}
        else:
            #Prevents only Blockers from spawning
            levelEnemies = random.sample(ENEMY_TYPES, random.randint(1, len(ENEMY_TYPES)))
            if levelEnemies == ["Blocker"]:
                levelEnemies.append("Shooter")
            LEVEL_DATA[node] = {
                "Horde": random.choice(HORDE_SIZE),
                "Enemies": levelEnemies,
                "Rewards": random.choice(REWARDS)
            }
def loadLevel(node):
    levelInfo = LEVEL_DATA.get(node, {})
    print(f"Level {node}. Horde Size {levelInfo.get('Horde')}. Enemies {levelInfo.get('Enemies')}. Reward: {levelInfo.get('Rewards')}")
def nextLevel(newNode):
    global currentNode
    global selectedLevel
    if newNode in getNextLevel(currentNode):
        currentNode = newNode
        selectedLevel = 0
        loadLevel(currentNode)
def setupMapPositions(screenWidth):
    global nodePositions
    center = screenWidth // 2
    nodePositions ={
        "Start": (center, 700),
        "L1":    (center - 100, 600),
        "L2":    (center + 100, 600),
        "L3":    (center - 350, 500),
        "L4":    (center - 110, 500),
        "L5":    (center + 110, 500),
        "L6":    (center + 350, 500),
        "L7":    (center - 330, 400),
        "L8":    (center - 120, 400),
        "L9":    (center + 120, 400),
        "L10":   (center + 330, 400),
        "L11":   (center - 150, 300),
        "L12":   (center + 150, 300),
        "L13":   (center, 200),
        "Boss":  (center, 100)
    }
#endregion

#region Resetting Game
def reset():
    global gamer, bullet, enemies, enemyBullets, enemiesKilled, bosses, mapCreated, paused, gameOverTime, enemiesDecided, currentNode
    bullet = []
    gamer = player.Player(bulletList = bullet)
    enemies = []
    enemyBullets = []
    enemiesKilled = 0
    bosses = []
    mapCreated = False
    paused = False
    gameOverTime = None
    enemiesDecided = False
    currentNode = "Start"
def softReset():
    global enemies, enemyBullets, enemiesKilled, bosses, enemiesDecided
    enemies = []
    enemyBullets = []
    enemiesKilled = 0
    bosses = []
    enemiesDecided = False
#endregion

#Game States: MainMenu Gameplay, How To Play, Map
state = "MainMenu"  #Where the game starts
selectedOption = 0
menuOptions = ["Start Game", "How To Play", "Quit"]
paused = False

def drawMainMenu(selected):
    gameScreen.fill((0,0,0))

    #Title Screen
    title = font.render("Rogue Space Invaders", True, (255,255,255))
    gameScreen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    #Options
    for i, option in enumerate(menuOptions):
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
        
def gameplay():
    global currentTime
    global enemiesKilled
    global bossSpawned
    global enemiesDecided
    levelInfo = LEVEL_DATA[currentNode]
    spawnWhat = levelInfo["Enemies"]
    howLarge = levelInfo["Horde"]
    rewardType = levelInfo["Rewards"]
    global enemiesLeft
    if howLarge == "Small" and not enemiesDecided:
        enemiesDecided = True
        enemiesLeft = random.randint(10, 15)
    elif howLarge == "Medium" and not enemiesDecided:
        enemiesDecided = True
        enemiesLeft = random.randint(20, 25)
    elif howLarge == "Large" and not enemiesDecided:
        enemiesDecided = True
        enemiesLeft = random.randint(30, 35)
    elif howLarge == "Massive" and not enemiesDecided:
        enemiesDecided = True
        enemiesLeft = 45

    key = pygame.key.get_pressed()
    currentTime = getGameTime()
    
    #Only update if game isn't paused.
    gamer.update(key, currentTime, paused)
    #Update bullets
    for shot in bullet[:]:
            shot.update(paused)
            if shot.rect.bottom < 0:
                bullet.remove(shot)

    #Update enemies
    for enemy in enemies[:]:
        if isinstance(enemy, attackers.Shooter):
            enemy.update(currentTime, enemyBullets, gamer, paused)
        elif isinstance(enemy, attackers.Charger):
            enemy.update(gamer, paused)
            if enemy.rect.colliderect(gamer.rect):
                gamer.takeDamage(enemy.damage, currentTime)
        else:
            enemy.update(paused)
            if enemy.rect.colliderect(gamer.rect):
                gamer.takeDamage(enemy.damage, currentTime)

        if enemy.rect.top > SCREEN_HEIGHT:
            enemy.rect.y = -50
            enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)

    #Enemy & bosses gets hit by a bullet
    for enemy in enemies[:]:
        for shot in bullet[:]:
            if enemy.rect.colliderect(shot.rect):
                bullet.remove(shot)
                if isinstance(enemy, attackers.Blocker):
                    enemy.takeDamage(shot.damage, charged=shot.charged)
                else:
                    enemy.health -= shot.damage
                if enemy.health <= 0:
                    if isinstance(enemy, attackers.Combustion):
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
    if enemiesKilled >= enemiesLeft and not bossSpawned and not paused and currentNode == "Boss":
        boss = attackers.BossShooterBlockerFusion(SCREEN_WIDTH//2 - 75, -150)
        bosses.append(boss)
        bossSpawned = True
    elif currentTime - attackers.lastSpawnTime > attackers.enemySpawnDelay and (enemiesKilled < enemiesLeft) and not paused:
        enemyX = random.randint(0, SCREEN_WIDTH - 50)
        enemyType = random.choice(spawnWhat)
        if enemyType == "Basic":
            #The -50 for the Y makes it so the enemy spawns offscreen before being shown.
            enemies.append(attackers.Enemy(enemyX, -50))
        elif enemyType == "Shooter":
            enemies.append(attackers.Shooter(enemyX, -50))
        elif enemyType == "Charger":
            enemies.append(attackers.Charger(enemyX, -50))
        elif enemyType == "Blocker":
            enemies.append(attackers.Blocker(enemyX, -50))
        elif enemyType == "Combustion":
           enemies.append(attackers.Combustion(enemyX, -50))
        attackers.lastSpawnTime = currentTime

    #Draws the player, bullets, enemies, and their bullets
    gameScreen.fill((0,0,0))
    if gamer.alive:
        gamer.draw(gameScreen)
    for shot in bullet:
        shot.draw(gameScreen)
    for enemy in enemies:
        enemy.draw(gameScreen)
    for enemyBull in enemyBullets[:]:
        if not paused:    
            if isinstance(enemyBull, bullets.Laser):
                enemyBull.update(currentTime, paused)
            else:
                enemyBull.update(paused)
        if getattr(enemyBull, "expired", False):
            enemyBullets.remove(enemyBull)
        if enemyBull.rect.top > SCREEN_HEIGHT or enemyBull.rect.bottom < 0 or enemyBull.rect.right < 0 or enemyBull.rect.left > SCREEN_WIDTH:
            enemyBullets.remove(enemyBull)
        elif enemyBull.rect.colliderect(gamer.rect):
            if isinstance(enemyBull, bullets.Laser):
                gamer.takeDamage(enemyBull.damage, currentTime)
            else:
                gamer.takeDamage(enemyBull.damage, currentTime)
                enemyBullets.remove(enemyBull)
        else:
            enemyBull.draw(gameScreen)
    for boss in bosses:
        if boss.alive:
            boss.update(currentTime, paused, enemyBullets)
            boss.draw(gameScreen)
    drawLeftHUD(gameScreen, font, gamer.health, gamer.cash, currentLevel, enemiesLeft, enemiesKilled)
    drawMiddleHUD(gameScreen, font)
    drawRightHUD(gameScreen, font, ["Bullet", "Laser"], gamer.currentWeapon)

def drawMap(screen):
    global mapCreated 
    
    #Clear the screen when loaded
    gameScreen.fill((0,0,0))

    #Creates the levels first time created
    if not mapCreated:
        generateLevel()
        setupMapPositions(screen.get_width())
        mapCreated = True

    #Connects nodes together
    for node, connections in MAP_GRAPH.items():
        for next in connections:
            pygame.draw.line(screen, (200,200,200), nodePositions[node], nodePositions[next], 2)
    
    nextNodes = getNextLevel(currentNode)

    #Gives nodes their info
    for node, (x, y) in nodePositions.items():
        if node == "Start":
            color = (0, 255, 0)
        elif node == "Boss":
            color = (255, 0, 0)
        elif node == currentNode:
            color = (0, 200, 0)
        elif node in nextNodes:
            color = (200, 200, 0)
        else:
            color = (100, 100, 255)
        
        pygame.draw.circle(screen, color, (x, y), 20)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 20, 2)

        #Text inside node
        text = levelFont.render(node, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

        #Horde, Enemies, Rewards below node
        if node not in ("Start", "Boss"):
            levelInfo = LEVEL_DATA[node]
            enemies = levelInfo["Enemies"]
            symbols = ""
            if "Basic" in enemies: symbols += "B "
            if "Shooter" in enemies: symbols += "S "
            if "Charger" in enemies: symbols += "C "
            if "Blocker" in enemies: symbols += "Bl "
            if "Combustion" in enemies: symbols += "X "
            detail = levelFont.render(f"{levelInfo['Horde']}, {symbols.strip()}, {levelInfo['Rewards']}", True, (255, 255, 0))
            detail_rect = detail.get_rect(center=(x, y + 30))
            screen.blit(detail, detail_rect)
    if nextNodes:
        selectedNode = nextNodes[selectedLevel]
        pos = nodePositions[selectedNode]
        pygame.draw.circle(screen, (255, 0, 0), pos, 26, 3)

#--Main Loop--#
run = True
selectedOption = 0
selectedLevel = 0
currentNode = "Start"

while run:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if state == "MainMenu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    selectedOption = (selectedOption - 1) % len(menuOptions)
                elif event.key == pygame.K_s:
                    selectedOption = (selectedOption + 1) % len(menuOptions)
                elif event.key == pygame.K_RETURN:
                    if selectedOption == 0:
                        reset()
                        state = "Map"      #Change for testing
                    elif selectedOption == 1:
                        state = "How To Play"
                    elif selectedOption == 2:
                        run = False
        elif state == "Gameplay":
            if not gamer.alive:
                state = "GameOver"
                gameOverTime = pygame.time.get_ticks()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not paused:
                    paused = True
                    pauseStartTime = pygame.time.get_ticks()
                else:
                    paused = False
                    pausedTimeAccumulated += pygame.time.get_ticks() - pauseStartTime
                    pauseStartTime = None
            if enemiesKilled >= enemiesLeft:
                softReset()
                state = "Map"
        elif state == "GameOver":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "MainMenu"
                gameOverTime = None
        elif state == "Map":
            if event.type == pygame.KEYDOWN:
                nextNodes = getNextLevel(currentNode)
                if event.key == pygame.K_a and nextNodes:
                    selectedLevel = (selectedLevel - 1) % len(nextNodes)
                elif event.key == pygame.K_d and nextNodes:
                    selectedLevel = (selectedLevel + 1) % len(nextNodes)
                elif event.key == pygame.K_RETURN and nextNodes:
                    nextNode = nextNodes[selectedLevel]
                    nextLevel(nextNode)
                    state = "Gameplay"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = "MainMenu"
    
    #Draw screens
    if state == "MainMenu":
        drawMainMenu(selectedOption)
    elif state == "Gameplay":
        gameplay()
    elif state == "How To Play":
        drawHowToPlay()
    elif state == "Map":
        drawMap(gameScreen)
    elif state == "GameOver":
        gameOverFont = pygame.font.Font(None, 120)
        gameOverText = gameOverFont.render("GAME OVER", True, (255,255,255))
        textRect = gameOverText.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        gameScreen.blit(gameOverText, textRect)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        gameScreen.blit(overlay, (0,0))
        gameScreen.blit(gameOverText, textRect)
        pygame.display.flip()
        if pygame.time.get_ticks() - gameOverTime > 3000:
            reset()
            state = "MainMenu"
            pygame.display.flip()

    #Charge Shot Charging Code
    if gamer.charging:
        if not paused:
            chargeDuration = currentTime - gamer.chargingStart
            progress = min(chargeDuration / bullets.maxChargeTime, 1.0)

        barWidth = gamer.rect.width
        barHeight = 8
        barX = gamer.rect.x
        barY = gamer.rect.bottom + 10

        pygame.draw.rect(gameScreen, (80, 80, 80), (barX, barY, barWidth, barHeight))
        pygame.draw.rect(gameScreen, (0, 200, 255), (barX, barY, int(barWidth * progress), barHeight))
    
    #Paused Game Code
    if state == "Gameplay" and paused:
        pauseFont = pygame.font.Font(None, 120)
        pauseText = pauseFont.render("PAUSED", True, (255,255,255))
        textRect = pauseText.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        gameScreen.blit(pauseText, textRect)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        gameScreen.blit(overlay, (0,0))
        gameScreen.blit(pauseText, textRect)

    #Resizing Window
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