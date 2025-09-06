import pygame

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rogue Space Invaders")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)


#Player code
playerSPD = 15
playerATK = 1
player = pygame.Rect((300, 500, 50, 50))

#Bullet code
bullet = []
bulletSPD = 20
bullet_width = 10
bullet_height = 30
shot_delay = 300
last_shot_time = 0

#Enemy code





#Game States: MainMenu Gameplay, Controls, Pause, Map
state = "MainMenu"  #Where the game starts
selected_option = 0
menu_options = ["Start Game", "Controls", "Quit"]

def drawMainMenu(selected):
    screen.fill((0,0,0))

    #Title Screen
    title = font.render("Rogue Space Invaders", True, (255,255,255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    #Options
    for i, option in enumerate(menu_options):
        color = (255, 255, 0) if i == selected else (255, 255, 255)
        text = small_font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 60))

#def drawControls():

#def drawPause():

def gameplay():
    global last_shot_time
    key = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    #Movement for player
    if key[pygame.K_a] and player.left > 0:
        player.x -= playerSPD
    elif key[pygame.K_d] and player.right < SCREEN_WIDTH:
        player.x += playerSPD
    
    #Action for shooting
    elif key[pygame.K_w] and current_time - last_shot_time >= shot_delay:
        bullet_x = player.centerx - bullet_width
        bullet_y = player.top
        bullet.append(pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height))
        last_shot_time = current_time

    #Update bullets
    for shot in bullet[:]:
            shot.y -= bulletSPD
            if shot.bottom < 0:
                bullet.remove(shot)

    screen.fill((0,0,0))
    pygame.draw.rect(screen, (255, 0, 0), player)
    for shot in bullet:
        pygame.draw.rect(screen, (255, 255, 255), shot)

#def drawMap():


#Main Loop
run = True
selected_option = 0

while run:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if state == "MainMenu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        state = "Gameplay"
                    elif selected_option == 1:
                        state = "Controls"
                    elif selected_option == 2:
                        run = False
            elif state == "Gameplay":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "Pause"
    if state == "MainMenu":
        drawMainMenu(selected_option)
    elif state == "Gameplay":
        gameplay()
    pygame.display.update()

pygame.quit()