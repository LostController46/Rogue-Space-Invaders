from resourceLoader import resourcePath
import pygame
import random
import player
import bullets
import attackers
import parts
import events
import visualize

pygame.init()

PCInfo = pygame.display.Info()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
screen = pygame.display.set_mode((PCInfo.current_w, PCInfo.current_h), pygame.RESIZABLE)
gameScreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Space Invaders")
clock = pygame.time.Clock()

#Fonts
font = pygame.font.Font(None, 74)
smallFont = pygame.font.Font(None, 50)
enemyLeftFont = pygame.font.Font(None, 32)
levelFont = pygame.font.Font(None, 35)
shopDescFont = pygame.font.Font(None, 30)
shopFont = pygame.font.Font(None, 40)

#Bullet code
bullet = []

#Player code
gamer = player.Player(bulletList = bullet)
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
enemiesOnScreen = 15

#Map Control
mapCreated = False
nodePositions = {}
eventManager = events.EventManager()

#Shop Control
shopPartsDecided = False
shopParts = []
currentShopSelection = [0,0]
finishedShopping = False

#Sandbox Control
selectedSandboxPart = 0
totalParts = parts.commonParts + parts.rareParts + parts.legendaryParts + parts.bossParts

#Sound Control
pygame.mixer.init()
enemyDeath = pygame.mixer.Sound(resourcePath("sounds/enemyDeath.wav"))

#Game Time
def getGameTime():
    if paused and pauseStartTime is not None:
        return pauseStartTime - pausedTimeAccumulated
    return pygame.time.get_ticks() - pausedTimeAccumulated

#region Resetting Game
def reset():
    global gamer, bullet, enemies, enemyBullets, enemiesKilled, bosses, mapCreated, paused, gameOverTime, enemiesDecided, currentNode, bossFlag, bossSpawned
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
    bossFlag = False
    bossSpawned = False
    currentNode = "Start"
def softReset(looped):
    global enemies, enemyBullets, enemiesKilled, bosses, enemiesDecided, mapCreated, currentNode, bossFlag, bossSpawned
    enemies = []
    enemyBullets = []
    enemiesKilled = 0
    bosses = []
    enemiesDecided = False
    if looped:
        mapCreated = False
        currentNode = "Start"
        bossFlag = False
        bossSpawned = False
def quitToMainMenu():
    global state, paused, pausedStartTime, pausedTimeAccumulated
    reset()
    state = "MainMenu"
    paused = False
    pausedStartTime = None
    pausedTimeAccumulated = 0
#endregion

#Game States: MainMenu Gameplay, How To Play, Map
state = "MainMenu"  #Where the game starts
selectedOption = 0
menuOptions = ["Start Game", "How To Play", "Sandbox", "Quit"]
paused = False

#region Gameplay
def gameplay():
    global currentTime
    global enemiesKilled
    global bossSpawned
    global enemiesDecided
    global enemiesLeft
    global enemiesOnScreen
    global bossFlag
    levelInfo = LEVEL_DATA[currentNode]
    spawnWhat = levelInfo["Enemies"]
    howLarge = levelInfo["Horde"]
    whichEvent = levelInfo["Event"]
    if not enemiesDecided:
        if howLarge == "Small":
            enemiesDecided = True
            enemiesLeft = random.randint(10, 15)
        elif howLarge == "Medium":
            enemiesDecided = True
            enemiesLeft = random.randint(20, 25)
        elif howLarge == "Large":
            enemiesDecided = True
            enemiesLeft = random.randint(30, 35)
        elif howLarge == "Massive":
            enemiesDecided = True
            enemiesLeft = 45
        if whichEvent == "extraEnemies":
            enemiesLeft += random.randint(5,10)
        if hasattr(gamer, "regain") and gamer.regain > 0:
            gamer.currentHealth = min(gamer.currentHealth + gamer.regain, gamer.maxHealth)

    key = pygame.key.get_pressed()
    currentTime = getGameTime()
    
    #Only update if game isn't paused.
    gamer.update(key, currentTime, paused, (enemies or []) + (bosses or []))
    #Update bullets
    for shot in bullet[:]:
        if isinstance(shot, bullets.LaserAfterimage):
            shot.update(currentTime, paused)
            if shot.timer <= 0:
                bullet.remove(shot)
        elif isinstance(shot, bullets.Laser):
            shot.update(currentTime, paused)
            if shot.expired:
                bullet.remove(shot)
        elif isinstance(shot, bullets.Missile):
            shot.target = (enemies or []) + (bosses or [])
            shot.update(currentTime, paused)
            if shot.expired:
                bullet.remove(shot)
        else:
            shot.update(currentTime, paused)
            if shot.rect.bottom < 0:
                bullet.remove(shot)


    #Update enemies & bosses
    for enemy in enemies[:]:
        if isinstance(enemy, attackers.Shooter):
            enemy.update(currentTime, enemyBullets, gamer, paused)
        elif isinstance(enemy, attackers.Charger):
            enemy.update(gamer, paused)
        else:
            enemy.update(paused)
        if enemy.rect.colliderect(gamer.rect):
            if gamer.thorns:
                enemy.takeDamage(gamer, "thorns", None)
            gamer.takeDamage(enemy.damage, currentTime, True)
        if enemy.rect.top > SCREEN_HEIGHT:
            enemy.rect.y = -50
            enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)
    #Enemy & bosses take damage
    for enemy in enemies[:]:
        if enemy.health <= 0:
            if gamer.basicWeak and isinstance(enemy, attackers.Basic):
                gamer.cash += enemy.worth + 3
            else:
                gamer.cash += enemy.worth
            if gamer.lifesteal:
                gamer.currentHealth += gamer.regain
                if gamer.currentHealth >= gamer.maxHealth:
                    gamer.currentHealth = gamer.maxHealth
            if isinstance(enemy, attackers.Combustion):
                enemy.onDeath(enemyBullets, gamer.combustionWeak, bullet)
                enemies.remove(enemy)
            else:
                enemies.remove(enemy)
            enemyDeath.play()
            if enemy.countsTowardsKills:
                enemiesKilled += 1
        for shot in bullet[:]:
            if enemy.rect.colliderect(shot.rect) and not isinstance(shot, bullets.LaserAfterimage):
                if isinstance(shot, bullets.Laser):
                    bullet.append(bullets.LaserAfterimage(shot, duration = 3000, charged = False))
                enemy.takeDamage(gamer, "bullet", shot)
                bullet.remove(shot)
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
        boss = attackers.Defender(SCREEN_WIDTH//2 - 75, -150)
        bosses.append(boss)
        bossSpawned = True
    elif currentTime - attackers.lastSpawnTime > (attackers.enemySpawnDelay + gamer.getEnemyDelaySabo()) + gamer.jammed and (enemiesKilled < enemiesLeft) and not paused and len(enemies) < enemiesOnScreen:
        groupSize = random.randint(1, 5)
        groupSize = min(groupSize, enemiesLeft - enemiesKilled, enemiesOnScreen - len(enemies))
        for _ in range(groupSize):
            enemyX = random.randint(0, SCREEN_WIDTH - 50)
            if whichEvent == "asteroidsFalling":
                enemies.append(attackers.Asteroid(enemyX, -120, scaling = gamer.currentLevel))
            enemyType = random.choice(spawnWhat)
            #Prepare the enemy to spawn
            if enemyType == "Basic":
                #The -50 for the Y makes it so the enemy spawns offscreen before being shown.
                prepEnemy = attackers.Basic(enemyX, -50, scaling = gamer.currentLevel)
            elif enemyType == "Shooter":
                prepEnemy = attackers.Shooter(enemyX, -50, scaling = gamer.currentLevel)
            elif enemyType == "Charger":
                prepEnemy = attackers.Charger(enemyX, -50, scaling = gamer.currentLevel)
            elif enemyType == "Blocker":
                prepEnemy = attackers.Blocker(enemyX, -50, scaling = gamer.currentLevel)
            elif enemyType == "Combustion":
                prepEnemy = attackers.Combustion(enemyX, -50, scaling = gamer.currentLevel)
            #Apply sabotage effects
            prepEnemy.health = max(1, prepEnemy.health + gamer.getEnemyHealthSabo())
            prepEnemy.speed = max(1, prepEnemy.speed + gamer.getEnemySpeedSabo())
            prepEnemy.damage = max(1, prepEnemy.damage + gamer.getEnemyDamageSabo())
            prepEnemy.worth = max(1, prepEnemy.worth + gamer.getEnemyWorthSabo())
            #Add enemy to list
            enemies.append(prepEnemy)
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
                enemyBull.update(currentTime, paused)
        if getattr(enemyBull, "expired", False):
            enemyBullets.append(bullets.LaserAfterimage(enemyBull, duration= 3000, charged = False))
            enemyBullets.remove(enemyBull)
            continue
        if enemyBull.rect.top > SCREEN_HEIGHT or enemyBull.rect.bottom < 0 or enemyBull.rect.right < 0 or enemyBull.rect.left > SCREEN_WIDTH:
            enemyBullets.remove(enemyBull)
            continue
        elif enemyBull.rect.colliderect(gamer.rect):
            gamer.takeDamage(enemyBull.damage, currentTime, False)
            if not isinstance(enemyBull, bullets.Laser):
                enemyBullets.remove(enemyBull)
            continue
        enemyBull.draw(gameScreen)
    for boss in bosses:
        if boss.alive:
            boss.update(currentTime, paused, enemyBullets, gamer)
            boss.draw(gameScreen)
        else:
            bossFlag = True
    visualize.drawLeftHUD(gameScreen, gamer.currentHealth, gamer.cash, gamer.currentLevel, enemiesLeft, enemiesKilled, smallFont, enemyLeftFont)
    visualize.drawMiddleHUD(gameScreen, gamer, font, smallFont)
    visualize.drawRightHUD(gameScreen, gamer.weaponList, gamer.currentWeapon, font)
#endregion

def giveReward(rewardType):
    global state, rewardText, rewardDesc
    global rewardBackground
    rewardBackground= gameScreen.copy()
    rewardText = ""
    rewardDesc = ""
    
    if rewardType == "Part":
        #Have a base of 60% for common and 40% for rare
        #Luck skews the odds to be 30% for common and 70% for rare with 60 luck
        #and the luck can't be skewed past this point.
        rarityOdds = max(0.6 - (gamer.luck / 200), 0.3)
        roll = random.random()
        if roll < rarityOdds:
            part = random.choice(parts.commonParts)
        else:
            part = random.choice(parts.rareParts)
        gamer.partCollected(part)
        ##Debug code: print(f"You got: {part}!")
        rewardText = f"You got: {part.name}!"
        rewardDesc = f"{part.desc}"
        state = "Reward"
    elif rewardType == "Heal":
        healAmount = 10
        gamer.currentHealth = gamer.currentHealth + healAmount
        if gamer.currentHealth > gamer.maxHealth:
            gamer.currentHealth = gamer.maxHealth
        rewardText = "You were healed!"
        state = "Reward"
    elif rewardType == "Shop":
        rewardText = "You found a Shop!"
        state = "Reward"
    elif rewardType == "BOSS_PART":
        part = random.choice(parts.bossParts)
        gamer.parts.append(part)
        rewardText = f"You stole {part.name} from the Boss!"
#--Main Loop--#
run = True
selectedOption = 0
selectedLevel = 0
currentPage = 1
totalPages = 0
currentNode = "Start"
bossFlag = False

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
                        state = "Sandbox"
                    elif selectedOption == 3:
                        run = False
        elif state == "Gameplay":
            if not gamer.alive:
                state = "GameOver"
                gameOverTime = pygame.time.get_ticks()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not paused:
                        paused = True
                        pauseStartTime = pygame.time.get_ticks()
                    else:
                        paused = False
                        pausedTimeAccumulated += pygame.time.get_ticks() - pauseStartTime
                        pauseStartTime = None
                elif event.key == pygame.K_q and paused:
                    quitToMainMenu()
            if enemiesKilled >= enemiesLeft:
                if currentNode != "Boss" or (currentNode == "Boss" and not bosses):
                    rewardType = LEVEL_DATA[currentNode]["Rewards"]
                    gamer.currentLevel += 1
                    giveReward(rewardType)
                    softReset(False)
            if bossFlag:
                rewardType = LEVEL_DATA[currentNode]["Rewards"]
                gamer.currentLevel += 1
                giveReward(rewardType)
                state = "EndScreen"
            #Debug Code for the Boss.
            #if event.type == pygame.KEYDOWN and event.key == pygame.K_INSERT:
            #    bosses.append(attackers.Defender(SCREEN_WIDTH//2 - 75, -150))
        elif state == "GameOver":
            if event.type == pygame.KEYDOWN:
                state = "MainMenu"
                gameOverTime = None
        elif state == "Map":
            if event.type == pygame.KEYDOWN:
                nextNodes = visualize.getNextLevel(currentNode)
                if event.key == pygame.K_a and nextNodes:
                    selectedLevel = (selectedLevel - 1) % len(nextNodes)
                elif event.key == pygame.K_d and nextNodes:
                    selectedLevel = (selectedLevel + 1) % len(nextNodes)
                elif event.key == pygame.K_RETURN and nextNodes:
                    #Debug code for parts
                    #gamer.parts.append(parts.Part())
                    nextNode = nextNodes[selectedLevel]
                    visualize.nextLevel(nextNode, currentNode)
                    currentNode = nextNode
                    state = "Gameplay"
                elif event.key == pygame.K_DELETE:
                    state = "MainMenu"
                #Debug code for Testing Boss
                #elif event.key == pygame.K_END:
                #    gamer.damage += 50
                #    gamer.updateStats()
                #    currentNode = "Boss"
                #    nextNode = []
                #    nextLevel(currentNode)
                #    state = "Gameplay"
            
        elif state == "Shop":
            if finishedShopping == False:    
                if event.type == pygame.KEYDOWN:
                    col, row = currentShopSelection
                    
                    #Movement through shop
                    if event.key == pygame.K_w:
                        currentShopSelection[1] = max(0, row - 1)
                    elif event.key == pygame.K_s:
                        if col == 0:
                            currentShopSelection[1] = min(len(shopParts) - 1, row + 1)
                        elif col == 1:
                            currentShopSelection[1] = min(len(gamer.shipUpgrades) - 1, row + 1)
                        elif col == 2:
                            currentShopSelection[1] = min(len(gamer.saboUpgrades) - 1, row + 1)
                    elif event.key == pygame.K_a:
                        currentShopSelection[0] = max(0, col - 1)
                        if currentShopSelection[0] == 0:
                            currentShopSelection[1] = min(currentShopSelection[1], len(shopParts) - 1)
                        elif currentShopSelection[0] == 1:
                            currentShopSelection[1] = min(currentShopSelection[1], len(gamer.shipUpgrades) - 1)
                        elif currentShopSelection[0] == 2:
                            currentShopSelection[1] = min(currentShopSelection[1], len(gamer.saboUpgrades) - 1)
                    elif event.key == pygame.K_d:
                        currentShopSelection[0] = min(2, col + 1)
                        if currentShopSelection[0] == 0:
                            currentShopSelection[1] = min(currentShopSelection[1], len(shopParts) - 1)
                        elif currentShopSelection[0] == 1:
                            currentShopSelection[1] = min(currentShopSelection[1], len(gamer.shipUpgrades) - 1)
                        elif currentShopSelection[0] == 2:
                            currentShopSelection[1] = min(currentShopSelection[1], len(gamer.saboUpgrades) - 1)
                    
                    #Purchases
                    elif event.key == pygame.K_RETURN:
                        col, row = currentShopSelection

                        #Parts Purchase
                        if col == 0:
                            selectedPart = shopParts[row]
                            if gamer.cash >= selectedPart.cost:
                                gamer.cash -= selectedPart.cost
                                gamer.parts.append(selectedPart)
                                gamer.updateStats()

                                #Remove part from shop
                                shopParts.remove(selectedPart)
                                if len(shopParts) > 0:
                                    if row >= len(shopParts):
                                        row = max(0, len(shopParts) - 1)
                                    currentShopSelection = [col, row]
                                else:
                                    #Move to ship purchases once parts are gone.
                                    currentShopSelection = [1,0]

                        #Ship Purchase
                        elif col == 1: 
                            selectedUpgrade = gamer.shipUpgrades[row]
                            if selectedUpgrade["LVL"] == 0:
                                cost = (int) (selectedUpgrade["cost"] / 2)
                            else:
                                cost = selectedUpgrade["cost"] * selectedUpgrade["LVL"]
                            if gamer.cash >= cost and selectedUpgrade["LVL"] < selectedUpgrade["maxLevel"]:
                                gamer.cash -= cost
                                selectedUpgrade["LVL"] += 1
                                gamer.updateStats()
                                if selectedUpgrade["name"] == "Ship Max Health":
                                    gamer.currentHealth += 10
                                if selectedUpgrade["name"] == "Laser Upgrade" and "Laser" not in gamer.weaponList:
                                    gamer.weaponList.append("Laser")
                                if selectedUpgrade["name"] == "Missile Upgrade" and "Missile" not in gamer.weaponList:
                                    gamer.weaponList.append("Missile")

                        #Sabotages Purchase
                        elif col == 2:
                            selectedSabo = gamer.saboUpgrades[row]
                            if selectedSabo["LVL"] == 0:
                                cost = (int) (selectedSabo["cost"] / 2)
                            else:
                                cost = selectedSabo["cost"] * selectedSabo["LVL"]
                            if gamer.cash >= cost and selectedSabo["LVL"] < selectedSabo["maxLevel"]:
                                gamer.cash -= cost
                                selectedSabo["LVL"] += 1

                    elif event.key == pygame.K_SPACE:
                        finishedShopping = True
                        shopPartsDecided = False
            else:
                state = "Map"
                finishedShopping = False
        elif state == "Reward":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if rewardText == "You found a Shop!":
                    state = "Shop"
                else:
                    state = "Map"
        elif state == "How To Play":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                currentPage = min(currentPage + 1, totalPages)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                currentPage = max(currentPage - 1, 1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "MainMenu"
        elif state == "Sandbox":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    selectedSandboxPart = (selectedSandboxPart + 1) % len(totalParts)
                elif event.key == pygame.K_a:
                    selectedSandboxPart = (selectedSandboxPart - 1) % len(totalParts)
                if event.key == pygame.K_RETURN:
                    gamer.parts.append(totalParts[selectedSandboxPart])
                if event.key == pygame.K_q:
                    quitToMainMenu()
        elif state == "EndScreen":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    softReset(True)
                    state = "Map"
                elif event.key == pygame.K_2:
                    reset()
                    state = "MainMenu"
    
    #Draw screens
    if state == "MainMenu":
        visualize.drawMainMenu(selectedOption, gameScreen, font, smallFont, menuOptions)
    elif state == "Gameplay":
        gameplay()
    elif state == "How To Play":
        visualize.drawHowToPlay(gameScreen, font, smallFont, currentPage,)
    elif state == "Map":
        mapCreated, LEVEL_DATA, currentNode, selectedNode, nodePositions, selectedLevel = visualize.drawMap(gameScreen, levelFont, mapCreated, currentNode, selectedLevel)
    elif state == "Shop":
        shopPartsDecided, shopParts = visualize.drawShop(gameScreen, gamer, font, smallFont, 
                                                         enemiesLeft, enemiesKilled, enemyLeftFont, 
                                                         currentShopSelection, shopDescFont, shopFont, shopPartsDecided, shopParts)
    elif state == "Reward":
        visualize.drawReward(gameScreen, rewardText, rewardDesc, font, smallFont, rewardBackground)
    elif state == "Sandbox":
        visualize.drawSandboxPartsSelection(gameScreen, font, smallFont, totalParts, selectedSandboxPart, gamer)
    elif state == "GameOver":
        visualize.drawGameOver(gameScreen)
        if pygame.time.get_ticks() - gameOverTime > 3000:
            reset()
            state = "MainMenu"
            pygame.display.flip()
    elif state == "EndScreen":
        visualize.drawEndScreen(gameScreen, font, smallFont)

    #Charge Shot Charging Code
    if gamer.charging:
        if not paused:
            if gamer.currentWeapon == "Bullet":
                chargeDuration = currentTime - gamer.chargingStart
                progress = min(chargeDuration / gamer.chargingSpeed, 1.0)
            elif gamer.currentWeapon == "Laser":
                chargeDuration = currentTime - gamer.chargingStart
                progress = min(chargeDuration / gamer.laserChargeSpeed, 1.0)

        barWidth = gamer.rect.width
        barHeight = 8
        barX = gamer.rect.x
        barY = gamer.rect.bottom + 10

        pygame.draw.rect(gameScreen, (80, 80, 80), (barX, barY, barWidth, barHeight))
        pygame.draw.rect(gameScreen, (0, 200, 255), (barX, barY, int(barWidth * progress), barHeight))
    
    #Paused Game Code
    if state == "Gameplay" and paused:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        gameScreen.blit(overlay, (0,0))
        
        #Pause Text
        pauseFont = pygame.font.Font(None, 120)
        pauseText = pauseFont.render("PAUSED", True, (255,255,255))
        textRect = pauseText.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        gameScreen.blit(pauseText, textRect)
        
        #Return to Game Text
        returnText = smallFont.render("Press ESC to return to game", True, (255,255,255))
        returnRect = returnText.get_rect(center=(SCREEN_WIDTH//4, SCREEN_HEIGHT - SCREEN_HEIGHT//4))
        gameScreen.blit(returnText, returnRect)

        #Return to Main Menu Text
        returnText = smallFont.render("Press Q to return to Main Menu", True, (255,255,255))
        returnRect = returnText.get_rect(center=(SCREEN_WIDTH - SCREEN_WIDTH//4, SCREEN_HEIGHT - SCREEN_HEIGHT//4))
        gameScreen.blit(returnText, returnRect)

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