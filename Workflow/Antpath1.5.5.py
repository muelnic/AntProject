import random
import pygame
import sys
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import pygame_widgets
import pandas as pd
import warnings

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
prob_shortest_path=0.75

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
            data['pheromone'] = max(MIN_PHEROMONE, data['pheromone'] - reduction_amount)

class Ant:
    def __init__(self, start, goals, food_sources):
        self.current_node = start
        self.path = [start]
        self.start = start
        self.goals = goals
        self.food_sources = food_sources
        self.returning = False
        self.return_steps = 0  # Zähler für Schritte während des Rückwegs

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
            self.returning = False
            self.path = [self.start]
        
        #df_distance = pd.DataFrame(columns=["distance"]) # Dataframe erstellen zur Speicherung der Distanz von einer Food Source zum Nest
        #for node in self.goals:
        #    target_x_fs, target_y_fs = graph[self.start]['pos']
        #    current_x_fs, current_y_fs = graph[node]['pos']
        #    dx_fs = target_x_fs - current_x_fs
        #    dy_fs = target_y_fs - current_y_fs
        #    distance = abs(dx_fs) + abs(dy_fs)
        #    df_distance.loc[node] = distance # berechnete Distanz in der dazugehörigen Reihe und Spalte des Dataframe speichern

        return food, self.current_node#,df_distance

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

# Slider und Textboxen für verschiedene Variablen
slider_num_ants = Slider(screen, 50, SCREEN_HEIGHT - 60, 150, 10, min=0, max=200, step=1,initial=100)
output_label_num_ants = TextBox(screen, 50, SCREEN_HEIGHT - 100, 100, 30, fontSize=20)
output_value_num_ants = TextBox(screen, 215, SCREEN_HEIGHT - 70, 50, 20, fontSize=10)

slider_reduction_amount = Slider(screen, 50, SCREEN_HEIGHT - 160, 150, 10, min=0, max=0.1, step=0.001, initial=0.005)
output_label_reduction_amount = TextBox(screen, 50, SCREEN_HEIGHT - 200, 180, 30, fontSize=20)
output_value_reduction_amount = TextBox(screen, 215, SCREEN_HEIGHT - 170, 50, 20, fontSize=10)

slider_pheromone_increase = Slider(screen, 50, SCREEN_HEIGHT - 260, 150, 10, min=0, max=0.5, step=0.01, initial=0.1)
output_label_pheromone_increase = TextBox(screen, 50, SCREEN_HEIGHT - 300, 180, 30, fontSize=20)
output_value_pheromone_increase = TextBox(screen, 215, SCREEN_HEIGHT - 270, 50, 20, fontSize=10)

slider_prob_shortest_path = Slider(screen, 50, SCREEN_HEIGHT - 360, 150, 10, min=0, max=1, step=0.01, initial=0.75)
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
        # food, food_source, df_distance = ant.move(adjacency_list,counter=counter,ant_number=ant)
        food, food_source = ant.move(adjacency_list,counter=counter,ant_number=ant)

        temp_list = [counter, ant, food_source, food]
        list_of_rows.append(temp_list)
    
    reduce_k_values(adjacency_list, reduction_amount)

    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, adjacency_list, num_rows, num_columns, SCREEN_WIDTH, SCREEN_HEIGHT, ants, food_sources)

    pygame_widgets.update(events)  # Alle Ereignisse an pygame_widgets übergeben
    pygame.display.update()
    pygame.display.flip()

#df_distance.to_excel("distance_of_food_source.xlsx")

df = pd.DataFrame(list_of_rows,columns=["counter", "ant", "food_source", "food"])
df_with_food = df[df["food"] != 0] # Filtert Einträge raus wo Food = 0 ist

# Dataframe sortieren zur Eliminierung von mehreren Ameisen in einem Zeitschritt bei einer Food Source (soll zusammengefasst werden)
df_sorted = df_with_food.sort_values(by=["counter","food_source"], ascending=[True,True])

# Duplikate löschen und nur den letzten Wert (d.h. die letzte Ameise pro Zeitschritt) behalten
df_filtered = df_sorted.drop_duplicates(subset=['counter', 'food_source'], keep='last')

print(df_filtered)

for index in range(max(df_filtered["counter"])): # Iteration über alle Zeitschritte
    for food_source in df_total_food.columns: # Iteration über alle Food Sources
            temp_df_list = df_filtered.loc[df_filtered["counter"] == index,"food_source"].tolist() # für den jeweiligen Zeitschritt, machen wir eine Liste von allen Food Sources, welche sich darin verändert haben
            if food_source in temp_df_list:
                filtered_rows = df_filtered[(df_filtered['counter'] == index) & (df['food_source'] == food_source)] # Filtern nach Wert basierend auf Zeitschritt und Food Source
                food_value = filtered_rows['food'].values[0] # Extrahieren des Wertes
                df_total_food.loc[index,food_source] = food_value # Speichern des Wertes in der entsprechenden Zeile und Spalte des finalen Dataframes
            else:
                if index > 0:
                    df_total_food.loc[index,food_source] = df_total_food.loc[index-1,food_source] # falls die Food Source nicht in der Liste der Food Sources ist, die sich in dem Zeitschritt ändert, wird der Wert vom vorherigen Zeitschritt übernommen
                else:
                    df_total_food.loc[index,food_source] = df_total_food.loc[0,food_source] # Spezialfall für Index = 0, dann entspricht der Wert im Dataframe einfach dem Startwert für die Food Source


print(df_total_food)
df_total_food.to_excel("food_over_time.xlsx")

pygame.quit()
sys.exit()