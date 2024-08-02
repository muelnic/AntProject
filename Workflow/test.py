import pygame
import sys
import random

pygame.init()


NODE_RADIUS = 15
NODE_COLOR = (255, 0, 0)
EDGE_COLOR = (255, 255, 255)  # Farbe für die Kanten
BACKGROUND_COLOR = (0, 0, 0)
num_rows = 5
num_columns = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Phäromonwerte für die Kanten
pheromones = [[0.22, 0.3, 0.5] for _ in range(num_rows * (num_columns - 1))]  # Horizontale Kanten
pheromones += [[0.22, 0.3, 0.5] for _ in range((num_rows - 1) * num_columns)]  # Vertikale Kanten


def draw_graph(screen, num_rows, num_columns, width, height):
    node_positions = []  # Eine Liste zum Speichern der Positionen der Knoten
    for i in range(num_rows):
        for j in range(num_columns):
            x = (width / (num_columns + 1)) * (j + 1)
            y = (height / (num_rows + 1)) * (i + 1)
            pygame.draw.circle(screen, NODE_COLOR, (x, y), NODE_RADIUS)
            node_positions.append((x, y))  # Speichere die Position des aktuellen Knotens

    # Zeichne Kanten
    for i in range(num_rows):
        for j in range(num_columns - 1):  # Horizontale Kanten
            x1, y1 = node_positions[i * num_columns + j]
            x2, y2 = node_positions[i * num_columns + j + 1]
            pygame.draw.line(screen, EDGE_COLOR, (x1, y1), (x2, y2))
        if i < num_rows - 1:  # Vertikale Kanten
            for j in range(num_columns):
                x1, y1 = node_positions[i * num_columns + j]
                x2, y2 = node_positions[(i + 1) * num_columns + j]
                pygame.draw.line(screen, EDGE_COLOR, (x1, y1), (x2, y2))


def choose_edge(pheromones):
    total_pheromone = sum(pheromones)
    random_p = random.uniform(0, 1)
    cumulative_p = 0
    for i, p in enumerate(pheromones):
        cumulative_p += p / total_pheromone
        if random_p <= cumulative_p:
            return i
    return len(pheromones) - 1


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Graph")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Ameise bewegt sich von einem Startknoten zu einem Zielknoten
            start_node = random.randint(0, num_rows * num_columns - 1)
            end_node = random.randint(0, num_rows * num_columns - 1)
            while end_node == start_node:
                end_node = random.randint(0, num_rows * num_columns - 1)

            current_node = start_node
            while current_node != end_node:
                neighbors = []
                # Überprüfe horizontale Nachbarn
                if current_node % num_columns != num_columns - 1:
                    neighbors.append(current_node + 1)
                if current_node % num_columns != 0:
                    neighbors.append(current_node - 1)
                # Überprüfe vertikale Nachbarn
                if current_node // num_columns != num_rows - 1:
                    neighbors.append(current_node + num_columns)
                if current_node // num_columns != 0:
                    neighbors.append(current_node - num_columns)

                chosen_edge = choose_edge(pheromones[current_node])
                next_node = neighbors[chosen_edge // 3]
                # Aktualisiere Phäromonwert der überquerten Kante
                pheromones[current_node][chosen_edge % 3] += 0.1
                current_node = next_node

    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.flip()

pygame.quit()
sys.exit()
