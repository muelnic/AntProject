import random
import pygame
import sys
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import pygame_widgets

pygame.init()

NODE_RADIUS = 1
NODE_COLOR = (255, 255, 255)
START_COLOR = (255, 0, 0)  # Rot für den Startknoten
BACKGROUND_COLOR = (255, 255, 255)  
num_rows = 50
num_columns = 50
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
reduction_amount = 0.005
pheromone_increase = 0.1
pheromone_start = 0.1
num_food_sources = 100  # Anzahl der Nahrungsquellen
MIN_PHEROMONE = 0.01
prob_shortest_path=0.75

def get_var(var_name, min_value, max_value, proposed_value, type):
    while True:
        try:
            if type == int:
                value = int(input(f"Bitte geben Sie {var_name} ein (zwischen {min_value} und {max_value}(standart wäre {proposed_value})): "))
            if type == float:
                value = int(input(f"Bitte geben Sie {var_name} ein (zwischen {min_value} und {max_value}(standart wäre {proposed_value})): "))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"{var_name} muss zwischen {min_value} und {max_value} liegen. Bitte versuchen Sie es erneut.")
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")

num_rows= get_var("num_rows", 10, 100, 50, int)
num_columns= get_var("num_columns", 10, 100, 50, int)
num_food_sources= get_var("num_food_sources", 1, 300, 100, int)




# Neue Definitionen für den Start- und Zielknoten
start_node = (num_rows // 2) * num_columns + (num_columns // 2)  # Start in der Mitte
end_nodes = random.sample(range(num_rows * num_columns), num_food_sources)  # Zufällige Zielknoten
food_sources = {node: random.randint(1, 1000) for node in end_nodes}  # Futterquellen mit zufälliger Größe

def draw_graph(screen, adjacency_list, num_rows, num_columns, width, height, ants, food_sources):
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

    for goal_node, size in food_sources.items():
        goal_x, goal_y = adjacency_list[goal_node]['pos']
        blue_intensity = int(size * 0.255)
        goal_color = (255 - blue_intensity, 255 - blue_intensity, 255)
        pygame.draw.circle(screen, goal_color, (int(goal_x), int(goal_y)), NODE_RADIUS)

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
    def __init__(self, start, goals, food_sources):
        self.current_node = start
        self.path = [start]
        self.start = start
        self.goals = goals
        self.food_sources = food_sources
        self.returning = False

    def move(self, graph):
        p_shortest_path = random.random()
        next_node = None

        if self.returning and p_shortest_path <= prob_shortest_path:
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
                self.current_node = next_node

        if next_node is None:
            neighbors = list(graph[self.current_node]['neighbors'].items())

            if len(self.path) > 1:
                previous_node = self.path[-2]
            else:
                previous_node = None

            if previous_node is not None:
                neighbors = [(neighbor, data) for neighbor, data in neighbors if neighbor != previous_node]

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
                    next_node = next
                    break

            self.current_node = next_node

        self.path.append(self.current_node)

        if self.returning:
            previous_node = self.path[-2]
            graph[previous_node]['neighbors'][self.current_node]['pheromone'] += pheromone_increase
            graph[self.current_node]['neighbors'][previous_node]['pheromone'] += pheromone_increase  # bidirectional update

        if self.current_node in self.goals:
            self.returning = True
            if self.food_sources[self.current_node] > 1:
                self.food_sources[self.current_node] -= 1
            else:
                self.goals.remove(self.current_node)
                del self.food_sources[self.current_node]
        
        if self.current_node == self.start:
            self.returning = False
            self.path = [self.start]

        return True


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Graph")

adjacency_list = generate_adjacency_list(num_rows, num_columns, start_node, end_nodes)

print("Adjazenzliste vor der Erstellung der Ameisen:")
for node, data in adjacency_list.items():
    print(f"Node {node}: {data['neighbors']}")

# Initiale Anzahl der Ameisen basierend auf dem Slider-Wert
slider_value = 50  # Initialer Slider-Wert
ants = [Ant(start_node, end_nodes, food_sources) for _ in range(slider_value)]

print(f"\nStartknoten (Nest der Ameisen): {start_node}")
print(f"Zielknoten (Futterquellen): {end_nodes}")

slider = Slider(screen, 50, SCREEN_HEIGHT - 60, 150, 10, min=0, max=200, step=1)  # Slider unten links positioniert
output_label = TextBox(screen, 50, SCREEN_HEIGHT - 100, 100, 30, fontSize=20)  # Textbox mit Label über dem Slider
output_value = TextBox(screen, 215, SCREEN_HEIGHT - 70, 20, 20, fontSize=10)  # Textbox für den Slider-Wert

output_label.setText("num_ants")  # Textbox als Label verwendet
output_label.disable()  # Act as label instead of textbox
output_value.disable()  # Act as read-only textbox

running = True
while running:
    events = pygame.event.get()  # Alle Ereignisse sammeln
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Update the number of ants based on the slider value
    slider_value = slider.getValue()
    if slider_value != len(ants):
        ants = [Ant(start_node, end_nodes, food_sources) for _ in range(slider_value)]

    output_value.setText(str(slider_value))  # Den aktuellen Slider-Wert anzeigen

    for ant in ants:
        ant.move(adjacency_list)
    reduce_k_values(adjacency_list, reduction_amount)

    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, adjacency_list, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT, ants, food_sources)

    pygame_widgets.update(events)  # Alle Ereignisse an pygame_widgets übergeben
    pygame.display.update()
    pygame.display.flip()

pygame.quit()
sys.exit()
