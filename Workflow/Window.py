import random
import pygame
import sys

pygame.init()

NODE_RADIUS = 1.5
NODE_COLOR = (255, 0, 0)
START_COLOR = (255, 255, 0)  # Gelb für den Startknoten
GOAL_COLOR = (0, 0, 255)      # Blau für die Zielknoten
BACKGROUND_COLOR = (0, 0, 0)
num_rows = 100
num_columns = 100
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
reduction_amount = 0.01
pheromone_increase = 0.1
pheromone_start = 0.1
num_ants = 5000
MIN_PHEROMONE = 0.01
Food1=(num_columns // 4)+((num_rows // 4)*num_rows)
Food2=(num_columns // 4)+((num_rows // 4*3)*num_rows)
Food3=(num_columns // 4*3)+((num_rows //4)*num_rows)

# Neue Definitionen für den Start- und Zielknoten
start_node = (num_rows // 2) * num_columns + (num_columns // 2) # Start in der Mitte
end_nodes = [Food1, Food2, Food3]  # Mehrere Zielknoten (unten rechts, oben links, unten links)

def draw_graph(screen, adjacency_list, num_rows, num_columns, width, height, ants):
    node_positions = []
    for i in range(num_rows):
        for j in range(num_columns):
            x = (width / (num_columns + 1)) * (j + 1)
            y = (height / (num_rows + 1)) * (i + 1)
            node_positions.append((x, y))

    # Draw edges with colors based on k values
    for node, neighbors in adjacency_list.items():
        x1, y1 = node_positions[node]
        for neighbor, k in neighbors.items():
            x2, y2 = node_positions[neighbor]
            intensity = int(min(max(k, 0), 1) * 255)
            edge_color = (255, 255 - intensity, 255 - intensity)
            pygame.draw.line(screen, edge_color, (x1, y1), (x2, y2))

    # Draw nodes
    for x, y in node_positions:
        pygame.draw.circle(screen, NODE_COLOR, (int(x), int(y)), NODE_RADIUS)

    # Draw start node in yellow
    start_x, start_y = node_positions[start_node]
    pygame.draw.circle(screen, START_COLOR, (int(start_x), int(start_y)), NODE_RADIUS)

    # Draw goal nodes in blue
    for goal_node in end_nodes:
        goal_x, goal_y = node_positions[goal_node]
        pygame.draw.circle(screen, GOAL_COLOR, (int(goal_x), int(goal_y)), NODE_RADIUS)

    # Draw ants
    for ant in ants:
        x, y = node_positions[ant.current_node]
        pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), NODE_RADIUS)

    return node_positions

def generate_adjacency_list(num_rows, num_columns, start_node, end_nodes):
    adjacency_list = {}
    for i in range(num_rows):
        for j in range(num_columns):
            node = i * num_columns + j
            neighbors = {}
            if i > 0:  # has top neighbor
                neighbors[(i - 1) * num_columns + j] = pheromone_start
            if i < num_rows - 1:  # has bottom neighbor
                neighbors[(i + 1) * num_columns + j] = pheromone_start
            if j > 0:  # has left neighbor
                neighbors[i * num_columns + j - 1] = pheromone_start
            if j < num_columns - 1:  # has right neighbor
                neighbors[i * num_columns + j + 1] = pheromone_start
            adjacency_list[node] = neighbors

    return adjacency_list

def reduce_k_values(graph, reduction_amount):
    for neighbors in graph.values():
        for neighbor in neighbors:
            neighbors[neighbor] = max(MIN_PHEROMONE, neighbors[neighbor] - reduction_amount)

class Ant:
    def __init__(self, start, goals):
        self.current_node = start
        self.path = [start]
        self.start = start
        self.goals = goals
        self.returning = False

    def move(self, graph):
        neighbors = list(graph[self.current_node].items())

        if len(self.path) > 1:
            previous_node = self.path[-2]
        else:
            previous_node = None

        if previous_node is not None:
        # Filtere die Nachbarn, um den vorherigen Knoten auszuschließen, den die Ameise gerade besucht hat
            filtered_neighbors = []
            for neighbor, k in neighbors:
                if neighbor != previous_node:
                    filtered_neighbors.append((neighbor, k))
            neighbors = filtered_neighbors


        if not neighbors:
            return False

        total_k = 0
        for i, k in neighbors:
            total_k += k


        if total_k == 0:
            return False

        neighbors.sort(key=lambda x: x[1], reverse=True)
        p = random.random()
        cumulative_p = 0
        for next, k in neighbors:
            cumulative_p += k / total_k
            if p <= cumulative_p:
                if self.returning:
                    graph[self.current_node][next] += pheromone_increase
                self.current_node = next
                self.path.append(next)
                #Überprüfe ob der Zielknoten erreicht wurde
                if self.current_node in self.goals:
                    self.returning = True
                #Überprüfe ob der Startknoten erneut erreicht wurde
                elif self.current_node == self.start and self.returning:
                    self.returning = False
                    self.path = [self.start]
                return True
        return False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Graph")

adjacency_list = generate_adjacency_list(num_rows, num_columns, start_node, end_nodes)

# Ausgabe der Adjazenzliste vor der Erstellung der Ameisen
print("Adjazenzliste vor der Erstellung der Ameisen:")
for node, neighbors in adjacency_list.items():
    print(f"Node {node}: {neighbors}")

# Erstelle die Ameisen
# Initialisierung der Ameisenliste
ants = []

# Erzeuge num_ants Ameisen
for i in range(num_ants):
    # Erstelle eine neue Ameise mit dem Startknoten und den Zielknoten
    ant = Ant(start_node, end_nodes)
    
    # Füge die erstellte Ameise zur Ameisenliste hinzu
    ants.append(ant)


print(f"\nStartknoten (Nest der Ameisen): {start_node}")
print(f"Zielknoten (Futterquellen): {end_nodes}")

running = True
while running:
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         running = False
    #     elif event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_SPACE:
    #             for ant in ants:
    #                 moved = ant.move(adjacency_list)
    #             reduce_k_values(adjacency_list, reduction_amount)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for ant in ants:
        moved = ant.move(adjacency_list)
    reduce_k_values(adjacency_list, reduction_amount)
    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, adjacency_list, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT, ants)
    pygame.display.flip()

pygame.quit()
sys.exit()
