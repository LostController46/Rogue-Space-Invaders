import pygame
import parts
import textwrap
import random
import events

basicSprite = pygame.image.load("images/Basic.png")
shooterSprite = pygame.image.load("images/Shooter.png")
chargerSprite = pygame.image.load("images/Charger.png")
blockerSprite = pygame.image.load("images/Blocker.png")
combustionSprite = pygame.image.load("images/Combustion.png")
defenderSprite = pygame.image.load("images/Boss.png")
defenderGunsSprite = pygame.image.load("images/BossGun.png")

def textWrapping(surface, text, font, color, rect, length, lineSpacing=5):
    maxChars = length  # adjust to fit your box width
    lines = textwrap.wrap(text, width=maxChars)
    yOffset = rect.y + 15
    for line in lines:
        line_surf = font.render(line, True, color)
        surface.blit(line_surf, (rect.x + 5, yOffset))
        yOffset += font.get_height() + lineSpacing

#region Main Menu
def drawMainMenu(selected, gameScreen, font, font2, menuOptions):
    gameScreen.fill((0,0,0))

    #Title Screen
    title = font.render("Rogue Space Invaders", True, (255,255,255))
    gameScreen.blit(title, (gameScreen.get_width() // 2 - title.get_width() // 2, 100))

    #Options
    for i, option in enumerate(menuOptions):
        color = (255, 255, 0) if i == selected else (255, 255, 255)
        text = font2.render(option, True, color)
        gameScreen.blit(text, (gameScreen.get_width() // 2 - text.get_width() // 2, 250 + i * 60))
#endregion

#region How To Play
def drawHowToPlay(gameScreen, font, font2, currentPage):
    global totalPages
    gameScreen.fill((0,0,0))

    title = font.render("How To Play", True, (255,255,255))
    gameScreen.blit(title, (gameScreen.get_width() // 2 - title.get_width() // 2, 50))
    controls = ["Move Left/Right: A / D", "Focus Movement: Hold RCtrl", "Shoot: Press/Hold W",
                "Charge Shot: Hold W & RShift, Release RShift when charged", 
                "Confirm/Buy: Enter", "Switch Weapons: Period", "Pause: Esc"]
    mapInfo = ["$ means there's a shop at the end of the level.",
               "P means that the player gets a part at the end of the level.",
               "H means that the player heals after the level.",
               "? means unknown reward at the end of the level.",
               "The letters underneath a level mean the enemy types that will appear."]
    enemyInfo = [("Basic", basicSprite, "Moves straight down.", "B"),
                 ("Shooter", shooterSprite, "Patrols and shoots bullets.", "S"),
                 ("Charger", chargerSprite, "Charges towards you quickly.", "C"),
                 ("Blocker", blockerSprite, "Patrols and takes less damage from normal shots.", "Bl"),
                 ("Combustion", combustionSprite, "Explodes into bullets when destroyed.", "X"),
                 ("Defender", defenderSprite, "Only weak point is its guns.", "Unknown")]
    totalPages = 2
    y = 150
    if currentPage == 1:
        text = font.render("Controls", True, (200, 200, 200))
        gameScreen.blit(text, (50, y))
        y += 50
        for line in controls:
            text = font2.render(line, True, (255,255,255))
            gameScreen.blit(text, (50, y))
            y += 50
        y += 30
        text = font.render("Map Information", True, (100, 100, 255))
        gameScreen.blit(text, (50, y))
        y += 50
        for line in mapInfo:
            text = font2.render(line, True, (255,255,255))
            gameScreen.blit(text, (50, y))
            y += 50
        
    else:
        text = font.render("Enemy Types", True, (255,100,100))
        gameScreen.blit(text, (50, y))
        y += 60
        for name, sprite, desc, symbol in enemyInfo:
            gameScreen.blit(sprite, (50, y))
            if name == "Defender":
                gameScreen.blit(defenderGunsSprite, (50, y + 70))
                gameScreen.blit(defenderGunsSprite, (50 + sprite.get_width() - 30, y + 70))
            fullText = f"{name} - Symbol: {symbol} - {desc}"
            descRect = pygame.Rect(
                50 + sprite.get_width() + 40,
                y,
                450,
                sprite.get_height() + 40)
            textWrapping(gameScreen,
                fullText,
                font2,
                (255, 255, 255),
                descRect,
                length = 55)
            y += sprite.get_height() + 50
    backText = font2.render("Press ESC to return                Press A/D to go between pages", True, (255, 255, 0))
    gameScreen.blit(backText, (gameScreen.get_width() // 2 - backText.get_width() // 2, gameScreen.get_height() - 75))
#endregion

#region HUD
def drawLeftHUD(gameScreen, health, cash, level, enemiesLeft, enemiesKilled, font, font2):
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
    textEnemiesLeft = font2.render(f"Enemies Left: {enemiesRemain}", True, (255, 255, 255))
    gameScreen.blit(textEnemiesLeft, (enemyHudRect.x + 5, enemyHudRect.y + 10))

def drawMiddleHUD(screen, player, font, font2):
    hudRect = pygame.Rect(200, screen.get_height() - 160, 960, 160)
    pygame.draw.rect(screen, (50, 50, 50), hudRect)
    pygame.draw.rect(screen, (200, 200, 200), hudRect, 2)
    text = font.render("Parts:", True, (200, 200, 200))
    screen.blit(text, (hudRect.x + 10, hudRect.y + 20))
    xOffset = hudRect.x + 160
    yOffset = hudRect.y + 5
    space = 25
    if not player.parts:
        text = font.render("None", True, (150,150,150))
        screen.blit(text, (xOffset, yOffset + space))
        return
    maxWidth = hudRect.width - 100
    rowX = xOffset
    rowY = yOffset + space
    rowSpacing = 25
    for parts in player.parts:
        partSurface = font2.render(parts.name, True, (200, 200, 200))
        partWidth = partSurface.get_width()
        if rowX + partWidth > hudRect.x + 10 + maxWidth:
            rowX = xOffset
            rowY += rowSpacing
        screen.blit(partSurface, (rowX, rowY))
        rowX += partWidth + 20

def drawRightHUD(screen, weapons, currentWeapon, font):
    hudRect = pygame.Rect(screen.get_width() - 200, screen.get_height() - 160, 200, 160)
    pygame.draw.rect(screen, (50, 50, 50), hudRect)
    pygame.draw.rect(screen, (200, 200, 200), hudRect, 2)
    for i, weapon in enumerate(weapons):
        color = (0, 255, 0) if weapon == currentWeapon else (200,200,200)
        text = font.render(weapon, True, color)
        screen.blit(text, (hudRect.right - text.get_width() - 5, hudRect.y + 10 + i * 50))
#endregion

#region Shop
def randomShopParts(gamer):
    randomPartList = []
    playerPartsList = {part.name for part in gamer.parts}
    usedParts = set(playerPartsList)
    legendaryCount = 0
    for _ in range(5):
        roll = random.random() + (gamer.luck / 200)
        #Chance for common
        if roll < 0.6:
            part = parts.commonParts
        #Chance for rare
        elif roll < 0.95:
            part = parts.rareParts
        #Chance for legendary
        else:
            if legendaryCount == 0:
                part = parts.legendaryParts
                legendaryCount += 1
            #If a legendary is already generated, give a rare part
            else:
                part = parts.rareParts
        #Filters the parts that the player/shop has
        available = [p for p in part if p.name not in usedParts]
        #Just adds the first common part if nothing is available
        if not available:
            newPart = parts.commonParts[0]
        else:
            newPart = random.choice(available)
        usedParts.add(newPart.name)
        randomPartList.append(newPart)
    return randomPartList

def drawShop(gameScreen, gamer, font, smallFont, enemiesLeft, enemiesKilled, enemyLeftFont, currentShopSelection, shopDescFont, shopFont, shopPartsDecided, shopParts):
    drawLeftHUD(gameScreen, gamer.currentHealth, gamer.cash, gamer.currentLevel, enemiesLeft, enemiesKilled, smallFont, enemyLeftFont)
    drawMiddleHUD(gameScreen, gamer, font, smallFont)
    
    #Makes a leave prompt where the weapons would be
    hudRect = pygame.Rect(gameScreen.get_width() - 200, gameScreen.get_height() - 160, 200, 160)
    pygame.draw.rect(gameScreen, (50, 50, 50), hudRect)
    pygame.draw.rect(gameScreen, (200, 200, 200), hudRect, 2)
    leaveTextRect = pygame.Rect(hudRect.x + 5, hudRect.y + 5, hudRect.width - 10,  hudRect.height - 10)
    leaveText = "Press Space to Leave"
    textWrapping(gameScreen, leaveText, smallFont, (255, 255, 255), leaveTextRect, length = 10)
    
    selectedCol, selectedRow = currentShopSelection
    selectedPart = None
    if not shopPartsDecided:
        shopParts = randomShopParts(gamer)
        shopPartsDecided = True

    #Left Section: Parts
    partsRect = pygame.Rect(0, 100, 426, 700)
    pygame.draw.rect(gameScreen, (50, 50, 50), partsRect)
    pygame.draw.rect(gameScreen, (235, 227, 4), partsRect, 2)
    partDesc = pygame.Rect(0, 0, 426, 100)
    pygame.draw.rect(gameScreen, (50, 50, 50), partDesc)
    pygame.draw.rect(gameScreen, (235, 227, 4), partDesc, 2)
    yOffset = 160
    if shopParts:
        if selectedCol == 0:
            selectedPart = shopParts[selectedRow]
            textWrapping(
                gameScreen,
                f"{selectedPart.name}: {selectedPart.desc}",
                shopDescFont,
                (225, 225, 225),
                partDesc,
                40
            )
        for i, part in enumerate(shopParts):
            itemRect = pygame.Rect(partsRect.x + 5, yOffset + i * 120, partsRect.width - 10, 100)
            if currentShopSelection == [0, i]:
                pygame.draw.rect(gameScreen, (255, 255, 0), itemRect, 3)
            nameText = shopFont.render(part.name, True, (255, 255, 255))
            priceText = shopFont.render(f"${part.cost}", True, (255, 255, 0))
            gameScreen.blit(nameText, (partsRect.x + 10, yOffset + i * 120))
            gameScreen.blit(priceText, (partsRect.x + 10, yOffset + i * 120 + 40))

    #Middle
    shipRect = pygame.Rect(426, 100, 426, 700)
    pygame.draw.rect(gameScreen, (50, 50, 50), shipRect)
    pygame.draw.rect(gameScreen, (32, 183, 247), shipRect, 2)
    shipDesc = pygame.Rect(426, 0, 426, 100)
    pygame.draw.rect(gameScreen, (50, 50, 50), shipDesc)
    pygame.draw.rect(gameScreen, (32, 183, 247), shipDesc, 2)
    
    if selectedCol == 1:
        selectedUpgrade = gamer.shipUpgrades[selectedRow]
        textWrapping(
            gameScreen,
            f"{selectedUpgrade['name']}: {selectedUpgrade['description']}",
            shopDescFont,
            (225, 225, 225),
            shipDesc,
            40
        )
    for i, upgrade in enumerate(gamer.shipUpgrades):
        name = upgrade["name"]
        lvl = upgrade["LVL"]
        maxLvl = upgrade["maxLevel"]
        if lvl == 0:
            cost = (int) (upgrade["cost"] / 2)
        else:
            cost = upgrade["cost"] * lvl
        itemRect = pygame.Rect(shipRect.x + 5, yOffset + i * 120, shipRect.width - 10, 100)
        if currentShopSelection == [1, i]:
            pygame.draw.rect(gameScreen, (32, 183, 247), itemRect, 3)
        nameText = shopFont.render(f"{name} (Lv {lvl}/{maxLvl})", True, (255, 255, 255))
        if lvl >= maxLvl:
            priceText = shopFont.render("MAXED", True, (100, 255, 100))
        else:
            priceText = shopFont.render(f"${cost}", True, (32, 183, 247))
        gameScreen.blit(nameText, (shipRect.x + 10, yOffset + i * 120))
        gameScreen.blit(priceText, (shipRect.x + 10, yOffset + i * 120 + 40))

    #Right
    saboRect = pygame.Rect(852, 100, 426, 700)
    pygame.draw.rect(gameScreen, (50, 50, 50), saboRect)
    pygame.draw.rect(gameScreen, (208, 25, 25), saboRect, 2)
    saboDesc = pygame.Rect(852, 0, 426, 100)
    pygame.draw.rect(gameScreen, (50, 50, 50), saboDesc)
    pygame.draw.rect(gameScreen, (208, 25, 25), saboDesc, 2)

    if selectedCol == 2:
        selectedSabo = gamer.saboUpgrades[selectedRow]
        textWrapping(
            gameScreen,
            f"{selectedSabo['name']}: {selectedSabo['description']}",
            shopDescFont,
            (225, 225, 225),
            saboDesc,
            40
        )
    for i, upgrade in enumerate(gamer.saboUpgrades):
        name = upgrade["name"]
        lvl = upgrade["LVL"]
        maxLvl = upgrade["maxLevel"]
        if lvl == 0:
            cost = (int) (upgrade["cost"] / 2)
        else:
            cost = upgrade["cost"] * lvl
        itemRect = pygame.Rect(saboRect.x + 5, yOffset + i * 120, saboRect.width - 10, 100)
        if currentShopSelection == [2, i]:
            pygame.draw.rect(gameScreen, (208, 25, 25), itemRect, 3)
        nameText = shopFont.render(f"{name} (Lv {lvl}/{maxLvl})", True, (255, 255, 255))
        if lvl >= maxLvl:
            priceText = shopFont.render("MAXED", True, (100, 255, 100))
        else:
            priceText = shopFont.render(f"${cost}", True, (208, 25, 25))
        gameScreen.blit(nameText, (saboRect.x + 10, yOffset + i * 120))
        gameScreen.blit(priceText, (saboRect.x + 10, yOffset + i * 120 + 40))
    return shopPartsDecided, shopParts
#endregion

eventManager = events.EventManager()
#region Map
#
#                  __ Boss __
#                 /    |     \
#               L15   L16   L17
#                 \  / |  \  /
#                 L12 L13  L14      <-Force Large/Massive pass this point
#                  \__ | __/
#                ____ L11 ____      <-Forced Shop
#               /   |  |  |   \
#              L6 L7  L8  L9 L10
#               \ |    |   | /
#                L3   L4   L5
#                 \  / \  /
#                  L1   L2          <-Forced Basic/Shooter/Both, Small/Medium, and Part
#                   \   /
#                   Start
MAP_GRAPH = {"Start": ["L1", "L2"],
             "L1":    ["L3", "L4"],
             "L2":    ["L4", "L5"],
             "L3":    ["L6", "L7"],
             "L4":    ["L8"],
             "L5":    ["L9", "L10"],
             "L6":    ["L11"],
             "L7":    ["L11"],
             "L8":    ["L11"],
             "L9":    ["L11"],
             "L10":   ["L11"],
             "L11":   ["L12", "L13", "L14"],
             "L12":   ["L15", "L16"],
             "L13":   ["L16"],
             "L14":   ["L16", "L17"],
             "L15":   ["Boss"],
             "L16":   ["Boss"],
             "L17":   ["Boss"],
             "Boss":  []

}

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
            LEVEL_DATA[node] = {"Horde": None, "Enemies": [], "Rewards": None, "Event": None}
        elif node == "L1" or node == "L2":
            levelEnemies = random.sample(["Basic", "Shooter"], random.randint(1, 2))
            eventManager.triggerRandomEvent()
            LEVEL_DATA[node] = {
                "Horde": random.choice(["Small", "Medium"]),
                "Enemies": levelEnemies,
                "Rewards": "Part",
                "Event": eventManager.currentEvent
            }
        #Always has a shop
        elif node == "L11":
            #Prevents only Blockers from spawning
            levelEnemies = random.sample(ENEMY_TYPES, random.randint(1, len(ENEMY_TYPES)))
            if levelEnemies == ["Blocker"]:
                levelEnemies.append("Shooter")
            eventManager.triggerRandomEvent()
            LEVEL_DATA[node] = {
                "Horde": random.choice(HORDE_SIZE),
                "Enemies": levelEnemies,
                "Rewards": "Shop",
                "Event": eventManager.currentEvent
            }
        #Always has large/massive hordes
        elif node == "L12" or node == "L13" or node == "L14" or node == "L15" or node == "L16" or node == "L17":
            #Prevents only Blockers from spawning
            levelEnemies = random.sample(ENEMY_TYPES, random.randint(1, len(ENEMY_TYPES)))
            if levelEnemies == ["Blocker"]:
                levelEnemies.append("Shooter")
            eventManager.triggerRandomEvent()
            LEVEL_DATA[node] = {
                "Horde": random.choice(["Large", "Massive"]),
                "Enemies": levelEnemies,
                "Rewards": random.choice(REWARDS),
                "Event": eventManager.currentEvent
            }
        elif node == "Boss":
            LEVEL_DATA[node] = {"Horde": "Massive", "Enemies": ENEMY_TYPES, "Rewards": "BOSS_PART", "Event": None}
        else:
            #Prevents only Blockers from spawning
            levelEnemies = random.sample(ENEMY_TYPES, random.randint(1, len(ENEMY_TYPES)))
            if levelEnemies == ["Blocker"]:
                levelEnemies.append("Shooter")
            eventManager.triggerRandomEvent()
            LEVEL_DATA[node] = {
                "Horde": random.choice(HORDE_SIZE),
                "Enemies": levelEnemies,
                "Rewards": random.choice(REWARDS),
                "Event": eventManager.currentEvent
            }
    return LEVEL_DATA
def loadLevel(node):
    levelInfo = LEVEL_DATA.get(node, {})
    #Debug Line
    #print(f"Level {node}. Horde Size {levelInfo.get('Horde')}. Enemies {levelInfo.get('Enemies')}. Reward: {levelInfo.get('Rewards')}")
def nextLevel(newNode, currentNode):
    global selectedLevel
    if newNode in getNextLevel(currentNode):
        currentNode = newNode
        selectedLevel = 0
        loadLevel(currentNode)
    return currentNode
def setupMapPositions(screenWidth):
    global nodePositions
    center = screenWidth // 2
    nodePositions ={
        "Start": (center, 900),
        "L1":    (center - 150, 800),
        "L2":    (center + 150, 800),
        "L3":    (center - 250, 700),
        "L4":    (center, 700),
        "L5":    (center + 250, 700),
        "L6":    (center - 450, 600),
        "L7":    (center - 250, 600),
        "L8":    (center, 600),
        "L9":    (center + 250, 600),
        "L10":   (center + 450, 600),
        "L11":   (center, 500),
        "L12":   (center - 200, 400),
        "L13":   (center, 400),
        "L14":   (center + 200, 400),
        "L15":   (center - 350, 300),
        "L16":   (center, 300),
        "L17":   (center + 350, 300),
        "Boss":  (center, 100)
    }
def drawMap(gameScreen, font, mapCreated, currentNode, selectedLevel):
    
    #Clear the screen when loaded
    gameScreen.fill((0,0,0))

    #Creates the levels first time created
    if not mapCreated:
        generateLevel()
        setupMapPositions(gameScreen.get_width())
        mapCreated = True

    #Connects nodes together
    for node, connections in MAP_GRAPH.items():
        for next in connections:
            pygame.draw.line(gameScreen, (200,200,200), nodePositions[node], nodePositions[next], 2)
    
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
        
        pygame.draw.circle(gameScreen, color, (x, y), 30)
        pygame.draw.circle(gameScreen, (255, 255, 255), (x, y), 30, 2)

        #Text inside node
        if node in ("Start", "Boss"):
            text = node
        else:
            levelInfo = LEVEL_DATA[node]
            reward = levelInfo["Rewards"]
            specialEvent = levelInfo["Event"]
            if specialEvent == "unknownRewards":
                text = "?"
            elif reward == "Shop" :
                text = "$"
            elif reward == "Part":
                text = "P"
            elif reward == "Heal":
                text = "H"
        textSurf = font.render(text, True, (255, 255, 255))
        textRect = textSurf.get_rect(center=(x, y))
        gameScreen.blit(textSurf, textRect)

        #Horde, Enemies, Rewards below node
        if node not in ("Start", "Boss"):
            levelInfo = LEVEL_DATA[node]
            enemies = levelInfo["Enemies"]
            specialEvent = levelInfo["Event"]
            symbols = ""
            if specialEvent != "unknownEnemies":
                if "Basic" in enemies: symbols += "B "
                if "Shooter" in enemies: symbols += "S "
                if "Charger" in enemies: symbols += "C "
                if "Blocker" in enemies: symbols += "Bl "
                if "Combustion" in enemies: symbols += "X "
            else:
                symbols += "?"
            detail = font.render(symbols.strip(), True, (255, 0, 255))
            detailRect = detail.get_rect(center=(x, y + 45))
            gameScreen.blit(detail, detailRect)
    if nextNodes:
        if selectedLevel >= len(nextNodes):
            selectedLevel = 0
        elif selectedLevel < 0:
            selectedLevel = 0
        selectedNode = nextNodes[selectedLevel]
        pos = nodePositions[selectedNode]
        pygame.draw.circle(gameScreen, (255, 0, 0), pos, 26, 3)
    return mapCreated, LEVEL_DATA, currentNode, selectedNode, nodePositions, selectedLevel
#endregion

#region Reward
def drawReward(gameScreen, rewardText, font, font2, rewardBackground = None):
    if rewardBackground:
        gameScreen.blit(rewardBackground, (0,0))
    overlay = pygame.Surface((gameScreen.get_width(), gameScreen.get_height()), flags=pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    gameScreen.blit(overlay, (0, 0))
    text = font.render(rewardText, True, (255, 255, 255))
    rect = text.get_rect(center=(gameScreen.get_width() // 2, 300))
    gameScreen.blit(text, rect)
    continueText = font2.render("Press SPACE to continue", True, (220, 220, 220))
    continueRect = continueText.get_rect(center=(gameScreen.get_width() // 2, 420))
    gameScreen.blit(continueText, continueRect)
#endregion

#region Game Over
def drawGameOver(gameScreen):
    gameOverFont = pygame.font.Font(None, 120)
    gameOverText = gameOverFont.render("GAME OVER", True, (255,255,255))
    textRect = gameOverText.get_rect(center=(gameScreen.get_width()//2, gameScreen.get_height()//2))
    gameScreen.blit(gameOverText, textRect)
    overlay = pygame.Surface((gameScreen.get_width(), gameScreen.get_height()), flags=pygame.SRCALPHA)
    overlay.fill((0,0,0,150))
    gameScreen.blit(overlay, (0,0))
    gameScreen.blit(gameOverText, textRect)
#endregion

#region Endgame
def drawEndScreen(gameScreen, font, font2):
    gameScreen.fill((0, 0, 0))

    text = font.render("Boss Defeated!", True, (255, 255, 0))
    gameScreen.blit(text, (gameScreen.get_width() // 2 - text.get_width() // 2, 200))

    msg = font2.render("What would you like to do?", True, (255, 255, 255))
    gameScreen.blit(msg, (gameScreen.get_width() // 2 - msg.get_width() // 2, 300))

    choice1 = font2.render("1. Continue Looping", True, (0, 255, 0))
    choice2 = font2.render("2. Finish Run (Return to Menu)", True, (255, 100, 100))

    gameScreen.blit(choice1, (gameScreen.get_width() // 2 - choice1.get_width() // 2, 400))
    gameScreen.blit(choice2, (gameScreen.get_width() // 2 - choice2.get_width() // 2, 460))
#endregion