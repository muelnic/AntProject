import pygame

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))




run=True
while  run == True:
    screen.fill((0,0,0))
    pygame.draw.circle(screen, (255, 0, 0), (200,200), 100, 0 )
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()

