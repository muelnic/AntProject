import pygame
import sys

pygame.init()


NODE_RADIUS = 15
NODE_COLOR = (255, 0, 0)
EDGE_COLOR = (255, 255, 255)  
BACKGROUND_COLOR = (0, 0, 0)
num_rows = 5
num_columns = 5
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

def draw_graph(screen, num_rows, num_columns, width, height):
    node_positions = []  
    for i in range(num_rows):
        for j in range(num_columns - 1): 
            x1 = (width / (num_columns + 1)) * (j + 1)
            y1 = (height / (num_rows + 1)) * (i + 1)
            x2 = (width / (num_columns + 1)) * (j + 2)
            y2 = (height / (num_rows + 1)) * (i + 1)
            pygame.draw.line(screen, EDGE_COLOR, (x1, y1), (x2, y2))

    for i in range(num_rows - 1):  
        for j in range(num_columns):
            x1 = (width / (num_columns + 1)) * (j + 1)
            y1 = (height / (num_rows + 1)) * (i + 1)
            x2 = (width / (num_columns + 1)) * (j + 1)
            y2 = (height / (num_rows + 1)) * (i + 2)
            pygame.draw.line(screen, EDGE_COLOR, (x1, y1), (x2, y2))

    for i in range(num_rows):
        for j in range(num_columns):
            x = (width / (num_columns + 1)) * (j + 1)
            y = (height / (num_rows + 1)) * (i + 1)
            pygame.draw.circle(screen, NODE_COLOR, (x, y), NODE_RADIUS)
            node_positions.append((x, y))  

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Graph")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.flip()

pygame.quit()
sys.exit()
