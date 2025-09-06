import pygame

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900
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
enemySPD = 3
lastSpawnTime = 0




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

    screen.fill((0,0,0))
    pygame.draw.rect(screen, (0, 255, 0), player)
    for shot in bullet:
        pygame.draw.rect(screen, (255, 255, 255), shot)

#def drawMap():


#Main Loop
run = True
selectedOption = 0

while run:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if state == "MainMenu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selectedOption = (selectedOption - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
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