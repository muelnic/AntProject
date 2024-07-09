import random
import pygame
import sys

pygame.init()

NODE_RADIUS = 15
NODE_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
num_rows = 5
num_columns = 5
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

def draw_graph(screen, adjacency_list, num_rows, num_columns, width, height):
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
        pygame.draw.circle(screen, NODE_COLOR, (x, y), NODE_RADIUS)

    return node_positions

def generate_adjacency_list(num_rows, num_columns):
    adjacency_list = {}
    for i in range(num_rows):
        for j in range(num_columns):
            node = i * num_columns + j
            neighbors = {}
            if i > 0:  # has top neighbor
                neighbors[(i - 1) * num_columns + j] = 0.1
            if i < num_rows - 1:  # has bottom neighbor
                neighbors[(i + 1) * num_columns + j] = 0.1
            if j > 0:  # has left neighbor
                neighbors[i * num_columns + j - 1] = 0.1
            if j < num_columns - 1:  # has right neighbor
                neighbors[i * num_columns + j + 1] = 0.1
            adjacency_list[node] = neighbors
    return adjacency_list

def ant_algorithm(graph, start, goal):
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        neighbors = list(graph[vertex].items())

        if len(path) > 1:
            previous_node = path[-2]
        else:
            previous_node = None

        if previous_node is not None:
            neighbors = [n for n in neighbors if n[0] != previous_node]

        if not neighbors:
            continue

        total_k = sum(k for _, k in neighbors)

        # If total_k is zero, all k values are zero, we should not divide by zero
        if total_k == 0:
            continue

        # Sort neighbors by their k values
        neighbors.sort(key=lambda x: x[1], reverse=True)

        # Generate a random number between 0 and 1
        p = random.random()

        # Decision based on p and cumulative probabilities
        cumulative_p = 0
        for next, k in neighbors:
            cumulative_p += k / total_k
            if p <= cumulative_p:
                # Increase the k value of the chosen edge
                graph[vertex][next] += 0.2

                if next == goal:
                    return path + [next]
                else:
                    stack.append((next, path + [next]))
                break
    return None

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Graph")

adjacency_list = generate_adjacency_list(num_rows, num_columns)

print(adjacency_list)

# Define start and end nodes for ant algorithm
start_node = 0  # Top-left corner
end_node = num_rows * num_columns - 1  # Bottom-right corner

# Find path from start to end using ant algorithm
path_to_goal = ant_algorithm(adjacency_list, start_node, end_node)
path_back_to_start = ant_algorithm(adjacency_list, end_node, start_node)

# Combine both paths
full_path = path_to_goal + path_back_to_start[1:]
print(f"Complete path: {full_path}")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, adjacency_list, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.flip()

pygame.quit()
sys.exit()
