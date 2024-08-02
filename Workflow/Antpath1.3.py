import random
import pygame
import sys

pygame.init()

NODE_RADIUS = 3
NODE_COLOR = (255, 0, 0)
START_COLOR = (255, 255, 0)  # Gelb für den Startknoten
GOAL_COLOR = (0, 0, 255)      # Blau für die Zielknoten
BACKGROUND_COLOR = (0, 0, 0)
num_rows = 50
num_columns = 50
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
reduction_amount = 0.005
pheromone_increase = 0.1
pheromone_start = 0.1
num_ants = 100
num_food_sources = 3  # Anzahl der Nahrungsquellen
MIN_PHEROMONE = 0.01

# Neue Definitionen für den Start- und Zielknoten
start_node = (num_rows // 2) * num_columns + (num_columns // 2)  # Start in der Mitte
end_nodes = random.sample(range(num_rows * num_columns), num_food_sources)  # Zufällige Zielknoten

def draw_graph(screen, adjacency_list, num_rows, num_columns, width, height, ants):
    for node, data in adjacency_list.items():
        x, y = data['pos']
        for neighbor, n_data in data['neighbors'].items():
            nx, ny = adjacency_list[neighbor]['pos']
            intensity = int(min(max(n_data['pheromone'], 0), 1) * 255)
            edge_color = (255, 255 - intensity, 255 - intensity)
            pygame.draw.line(screen, edge_color, (x, y), (nx, ny))

    for node, data in adjacency_list.items():
        x, y = data['pos']
        pygame.draw.circle(screen, NODE_COLOR, (int(x), int(y)), NODE_RADIUS)

    start_x, start_y = adjacency_list[start_node]['pos']
    pygame.draw.circle(screen, START_COLOR, (int(start_x), int(start_y)), NODE_RADIUS)

    for goal_node in end_nodes:
        goal_x, goal_y = adjacency_list[goal_node]['pos']
        pygame.draw.circle(screen, GOAL_COLOR, (int(goal_x), int(goal_y)), NODE_RADIUS)

    for ant in ants:
        x, y = adjacency_list[ant.current_node]['pos']
        pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), NODE_RADIUS)

def generate_adjacency_list(num_rows, num_columns, start_node, end_nodes):
    adjacency_list = {}
    for i in range(num_rows):
        for j in range(num_columns):
            node = i * num_columns + j
            neighbors = {}
            if i > 0:  # has top neighbor
                neighbors[(i - 1) * num_columns + j] = {'pheromone': pheromone_start}
            if i < num_rows - 1:  # has bottom neighbor
                neighbors[(i + 1) * num_columns + j] = {'pheromone': pheromone_start}
            if j > 0:  # has left neighbor
                neighbors[i * num_columns + j - 1] = {'pheromone': pheromone_start}
            if j < num_columns - 1:  # has right neighbor
                neighbors[i * num_columns + j + 1] = {'pheromone': pheromone_start}
            x = (SCREEN_WIDTH / (num_columns + 1)) * (j + 1)
            y = (SCREEN_HEIGHT / (num_rows + 1)) * (i + 1)
            adjacency_list[node] = {'pos': (x, y), 'neighbors': neighbors}

    return adjacency_list

def reduce_k_values(graph, reduction_amount):
    for node_data in graph.values():
        for data in node_data['neighbors'].values():
            data['pheromone'] = max(MIN_PHEROMONE, data['pheromone'] - reduction_amount)

class Ant:
    def __init__(self, start, goals):
        self.current_node = start
        self.path = [start]
        self.start = start
        self.goals = goals
        self.returning = False

    def move(self, graph):
        p_shortest_path = random.random()
        # Shortest Path will be utilised in 75% of the cases 
        if self.returning and p_shortest_path <= 0.75:
            target_x, target_y = graph[self.start]['pos']
            current_x, current_y = graph[self.current_node]['pos']
            dx = target_x - current_x
            dy = target_y - current_y

            if abs(dx) > abs(dy):
                if dx > 0:
                    next_node = self.current_node + 1
                else:
                    next_node = self.current_node - 1
            else:
                if dy > 0:
                    next_node = self.current_node + num_columns
                else:
                    next_node = self.current_node - num_columns

            if next_node in graph[self.current_node]['neighbors']:
                graph[self.current_node]['neighbors'][next_node]['pheromone'] += pheromone_increase
                graph[next_node]['neighbors'][self.current_node]['pheromone'] += pheromone_increase  # bidirectional update
                self.current_node = next_node
                self.path.append(next_node)

                if self.current_node == self.start:
                    self.returning = False
                    self.path = [self.start]
                return True

        else:
            neighbors = list(graph[self.current_node]['neighbors'].items())

            if len(self.path) > 1:
                previous_node = self.path[-2]
            else:
                previous_node = None

            if previous_node is not None:
                filtered_neighbors = []
                for neighbor, data in neighbors:
                    if neighbor != previous_node:
                        filtered_neighbors.append((neighbor, data))
                neighbors = filtered_neighbors

            if not neighbors:
                return False

            total_k = sum(data['pheromone'] for _, data in neighbors)
            if total_k == 0:
                return False

            neighbors.sort(key=lambda x: x[1]['pheromone'], reverse=True)
            p = random.random()
            cumulative_p = 0
            for next, data in neighbors:
                cumulative_p += data['pheromone'] / total_k
                if p <= cumulative_p:
                    self.current_node = next
                    self.path.append(next)
                    if self.current_node in self.goals:
                        self.returning = True
                    return True
            return False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Graph")

adjacency_list = generate_adjacency_list(num_rows, num_columns, start_node, end_nodes)

print("Adjazenzliste vor der Erstellung der Ameisen:")
for node, data in adjacency_list.items():
    print(f"Node {node}: {data['neighbors']}")

ants = [Ant(start_node, end_nodes) for _ in range(num_ants)]

print(f"\nStartknoten (Nest der Ameisen): {start_node}")
print(f"Zielknoten (Futterquellen): {end_nodes}")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for ant in ants:
        ant.move(adjacency_list)
    reduce_k_values(adjacency_list, reduction_amount)
    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, adjacency_list, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT, ants)
    pygame.display.flip()

pygame.quit()
sys.exit()
