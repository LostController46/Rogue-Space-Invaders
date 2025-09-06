import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

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

run = True
while run:
    dt = clock.tick(60)
    screen.fill((0, 0, 0))
    current_time = pygame.time.get_ticks()

    pygame.draw.rect(screen, (255, 0, 0), player)
    #pygame.draw.rect(screen, (255, 255, 255), bullet)

    key = pygame.key.get_pressed()
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

    for shot in bullet[:]:
        shot.y -= bulletSPD
        if shot.bottom < 0:
            bullet.remove(shot)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    for shot in bullet:
        pygame.draw.rect(screen, (255, 255, 255), shot)
    pygame.display.update()

pygame.quit()