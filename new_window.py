import pygame



pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

n=16
Nodes = []
for i in range (1, n+1):
    Nodes.append(i)




run=True
while  run == True:
    screen.fill((0,0,0))
    for i in range(1, n+1):
        if i <= 4:
            x=(SCREEN_WIDTH/5)*i
            y=(SCREEN_HEIGHT/5)
        elif i <=8:
            x=(SCREEN_WIDTH/5)*(i-4)
            y=(SCREEN_HEIGHT/5)*2
        elif i <=12:
            x=(SCREEN_WIDTH/5)*(i-8)
            y=(SCREEN_HEIGHT/5)*3
        else:
            x=(SCREEN_WIDTH/5)*(i-12)
            y=(SCREEN_HEIGHT/5)*4
        pygame.draw.circle(screen, (255, 0, 0), (x,y), 10, 0 )
        print("test")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()

