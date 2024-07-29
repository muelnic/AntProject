import random
import pygame
import sys
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import pygame_widgets
import pandas as pd
import warnings
import os

warnings.filterwarnings('ignore', category=UserWarning)


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

linear_pheromone_update=False
#Wenn linear_pheromone_update=True werden die Pheromonwerte gemäss Ursprünglicher Implementation linar reduziert.
#Wenn linear_pheromone_update=False werden die Pheromonwerte gemäss Literatur mit einem Faktor zwischen 0 und 1 multipliziert und somit reduziert.
pheromone_always=False
#Wenn pheromone_always=True werden Pheromone auf dem Hin- und Rückweg deponiert. -> Die Ameisen werden sich in einen Loop begeben.
#Wenn pheromone_always=False werden Pheromone nur auf dem Rückweg deponiert.

run_name = "test_6"
os.makedirs(run_name, exist_ok=True)

print(f"Directory '{run_name}' created successfully.")

def get_var(var_name, min_value, max_value, proposed_value, type):
    while True:
        try:
            if type == int:
                value = int(input(f"Bitte geben Sie {var_name} ein (zwischen {min_value} und {max_value}(standart wäre {proposed_value})): "))
            if type == float:
                value = float(input(f"Bitte geben Sie {var_name} ein (zwischen {min_value} und {max_value}(standart wäre {proposed_value})): "))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"{var_name} muss zwischen {min_value} und {max_value} liegen. Bitte versuchen Sie es erneut.")
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")



num_rows= get_var("num_rows", 10, 100, 50, int)
num_columns= get_var("num_columns", 10, 100, 50, int)
num_food_sources= get_var("num_food_sources", 1, 300, 100, int)
prob_shortest_path_inital=get_var("prob_shortest_path",0,1,0.75, float)


standard_case = True # Definiere, ob Startpunkt in der Mitte ist (standard) oder an einer beliebigen Position
# Neue Definitionen für den Start- und Zielknoten
if standard_case:
    start_node = (num_rows // 2) * num_columns + (num_columns // 2)  # Start in der Mitte
else:
    start_node = 1
end_nodes = random.sample(range(num_rows * num_columns), num_food_sources)  # Zufällige Zielknoten

food_sources = {node: random.randint(1, 1000) for node in end_nodes}  # Futterquellen mit zufälliger Größe
start_food_sources = food_sources # Speichern in separater Variable
df_total_food = pd.DataFrame([start_food_sources]) # Aus Dict einen Dataframe machen
total_sum_of_food = sum(food_sources.values()) # Gesamtmenge an Food in den Food Sources zu Beginn bestimmen

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
        if standard_case:
            x, y = adjacency_list[ant.current_node]['pos']
            pygame.draw.circle(screen, (0,255,0), (int(x), int(y)), NODE_RADIUS)
        else:
            ant_of_interest = 0 # Nummer der Ameise, die man beobachten will, einstellen
            if ant != ants[ant_of_interest]:
                x, y = adjacency_list[ant.current_node]['pos']
                pygame.draw.circle(screen, (0,255,0), (int(x), int(y)), NODE_RADIUS)
            else:
                x, y = adjacency_list[ant.current_node]['pos']
                pygame.draw.circle(screen, (255,0,255), (int(x), int(y)), 15)

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
            if linear_pheromone_update:
                data['pheromone'] = max(MIN_PHEROMONE, data['pheromone'] - reduction_amount)
            else:
                data['pheromone'] = max(MIN_PHEROMONE, data['pheromone'] * (1-reduction_amount))

class Ant:
    def __init__(self, start, goals, food_sources):
        self.current_node = start
        self.path = [start]
        self.start = start
        self.goals = goals
        self.food_sources = food_sources
        self.return_steps = 0  # Zähler für Schritte während des Rückwegs
        if pheromone_always:
            self.returning = True
        else:
            self.returning = False

    def move(self, graph,counter,ant_number):
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
            self.return_steps += 1  # Zähler erhöhen
            previous_node = self.path[-2]
            graph[previous_node]['neighbors'][self.current_node]['pheromone'] += pheromone_increase
            graph[self.current_node]['neighbors'][previous_node]['pheromone'] += pheromone_increase  # bidirectional update

            # Überprüfen, ob die maximale Anzahl an Schritten erreicht ist
            if self.return_steps >= num_rows + num_columns:
                if not pheromone_always:
                    self.returning = False
                self.return_steps = 0  # Zähler zurücksetzen
        food = 0 # Variable intialisieren, um die Menge an Food in einer Food Source zu speichern
        if self.current_node in self.goals:
            self.returning = True
            if self.food_sources[self.current_node] > 1:
                self.food_sources[self.current_node] -= 1
                food = self.food_sources[self.current_node] # neuer Wert von Food speichern, falls er sich verändert hat
            else:
                food = 0
                self.goals.remove(self.current_node)
                del self.food_sources[self.current_node]
        
        if self.current_node == self.start:
            if not pheromone_always:
                self.returning = False
            self.path = [self.start]

        return food, self.current_node


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Graph")

adjacency_list = generate_adjacency_list(num_rows, num_columns, start_node, end_nodes)
df_distance = pd.DataFrame(columns=["distance"]) # Dataframe erstellen zur Speicherung der Distanz von einer Food Source zum Nest
for node in end_nodes:
    target_x_fs, target_y_fs = adjacency_list[start_node]['pos']
    current_x_fs, current_y_fs = adjacency_list[node]['pos']
    dx_fs = target_x_fs - current_x_fs
    dy_fs = target_y_fs - current_y_fs
    distance = abs(dx_fs) + abs(dy_fs)
    df_distance.loc[node] = distance # berechnete Distanz in der dazugehörigen Reihe und Spalte des Dataframe speichern
df_distance.to_excel(f"{run_name}/distance_of_food_source.xlsx")

print("Adjazenzliste vor der Erstellung der Ameisen:")
for node, data in adjacency_list.items():
    print(f"Node {node}: {data['neighbors']}")

# Initiale Anzahl der Ameisen basierend auf dem Slider-Wert
slider_value = 50  # Initialer Slider-Wert
ants = [Ant(start_node, end_nodes, food_sources) for _ in range(slider_value)]

print(f"\nStartknoten (Nest der Ameisen): {start_node}")
print(f"Zielknoten (Futterquellen): {end_nodes}")

# Slider und Textboxen für verschiedene Variablen
slider_num_ants = Slider(screen, 50, SCREEN_HEIGHT - 60, 150, 10, min=0, max=500, step=1,initial=0)
output_label_num_ants = TextBox(screen, 50, SCREEN_HEIGHT - 100, 100, 30, fontSize=20)
output_value_num_ants = TextBox(screen, 215, SCREEN_HEIGHT - 70, 50, 20, fontSize=10)


if linear_pheromone_update:
    reduce_k_values_step=0.001
    reduce_k_values_initial=0.005
    reduce_k_values_max=0.1
    pheromone_increase_initial=0.1
else:
    reduce_k_values_step=0.01
    reduce_k_values_initial=0.05
    reduce_k_values_max=1
    pheromone_increase_initial=0.25

slider_reduction_amount = Slider(screen, 50, SCREEN_HEIGHT - 160, 150, 10, min=0, max=reduce_k_values_max, step=reduce_k_values_step, initial=reduce_k_values_initial)
output_label_reduction_amount = TextBox(screen, 50, SCREEN_HEIGHT - 200, 180, 30, fontSize=20)
output_value_reduction_amount = TextBox(screen, 215, SCREEN_HEIGHT - 170, 50, 20, fontSize=10)

slider_pheromone_increase = Slider(screen, 50, SCREEN_HEIGHT - 260, 150, 10, min=0, max=0.5, step=0.01, initial=pheromone_increase_initial)
output_label_pheromone_increase = TextBox(screen, 50, SCREEN_HEIGHT - 300, 180, 30, fontSize=20)
output_value_pheromone_increase = TextBox(screen, 215, SCREEN_HEIGHT - 270, 50, 20, fontSize=10)

slider_prob_shortest_path = Slider(screen, 50, SCREEN_HEIGHT - 360, 150, 10, min=0, max=1, step=0.01, initial=prob_shortest_path_inital)
output_label_prob_shortest_path = TextBox(screen, 50, SCREEN_HEIGHT - 400, 180, 30, fontSize=20)
output_value_prob_shortest_path = TextBox(screen, 215, SCREEN_HEIGHT - 370, 50, 20, fontSize=10)

output_label_num_ants.setText("num_ants")
output_label_num_ants.disable()
output_value_num_ants.disable()

output_label_reduction_amount.setText("reduction_amount")
output_label_reduction_amount.disable()
output_value_reduction_amount.disable()

output_label_pheromone_increase.setText("pheromone_increase")
output_label_pheromone_increase.disable()
output_value_pheromone_increase.disable()

output_label_prob_shortest_path.setText("prob_shortest_path")
output_label_prob_shortest_path.disable()
output_value_prob_shortest_path.disable()

running = True
counter = 0
list_of_rows = []
while running:
    counter = counter + 1
    events = pygame.event.get()  # Alle Ereignisse sammeln
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Update the number of ants based on the slider value
    slider_value = slider_num_ants.getValue()
    if slider_value != len(ants):
        ants = [Ant(start_node, end_nodes, food_sources) for _ in range(slider_value)]

    reduction_amount = slider_reduction_amount.getValue()
    pheromone_increase = slider_pheromone_increase.getValue()
    prob_shortest_path = slider_prob_shortest_path.getValue()

    output_value_num_ants.setText(str(slider_value))
    output_value_reduction_amount.setText(str(reduction_amount))
    output_value_pheromone_increase.setText(str(pheromone_increase))
    output_value_prob_shortest_path.setText(str(prob_shortest_path))

    list_of_timesteps = [1000, 2000, 3000, 4000]
    if counter in list_of_timesteps:
        # save image
        print("This is an important time step. We need to save it.") 

    for ant in ants:
        food, food_source = ant.move(adjacency_list,counter=counter,ant_number=ant)
        temp_list = [counter, ant, food_source, food]
        list_of_rows.append(temp_list)
    
    reduce_k_values(adjacency_list, reduction_amount)

    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, adjacency_list, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT, ants, food_sources)

    pygame_widgets.update(events)  # Alle Ereignisse an pygame_widgets übergeben
    pygame.display.update()
    pygame.display.flip()


df = pd.DataFrame(list_of_rows,columns=["counter", "ant", "food_source", "food"])
df_with_food = df[df["food"] != 0] # Filtert Einträge raus wo Food = 0 ist

# Dataframe sortieren zur Eliminierung von mehreren Ameisen in einem Zeitschritt bei einer Food Source (soll zusammengefasst werden)
df_sorted = df_with_food.sort_values(by=["counter","food_source"], ascending=[True,True])

# Duplikate löschen und nur den letzten Wert (d.h. die letzte Ameise pro Zeitschritt) behalten
df_filtered = df_sorted.drop_duplicates(subset=['counter', 'food_source'], keep='last')

df_filtered.to_excel(f"{run_name}/filtered_df.xlsx")

run_specifications = df_total_food

run_specifications["counter"] = counter

run_specifications.to_excel(f"{run_name}/run_specifications.xlsx")

pygame.quit()
sys.exit()
