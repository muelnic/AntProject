# AntProject
## Analyse und Simulation der Ameisenstrassenbildung

### Einleitung
In dieser Maturaarbeit wird die Bildung von Ameisenstrassen mithilfe eines programmierten Modells analysiert, das auf dem natürlichen Verhalten von Ameisen basiert. Um die Effizienz der Ameisen bei der Futtersuche zu untersuchen, wurde das Programm mit verschiedenen Parametereinstellungen getestet. Zu den untersuchten Parametern gehören die Anzahl der Ameisen, die Pheromondeponierungsrate, die Verdunstungsrate der Pheromone und die Methode der Wegfindung. Mithilfe eines Auswertungsprogrammes konnten diese Auswirkungen verglichen werden. Dabei stellte sich heraus, dass von den untersuchten Parametern die Ameisenanzahl am meisten Einfluss auf die Effizienz der Futtersuche hatte.

### Bedienungsanleitung
Um das Programm korrekt zu nutzen, beachten Sie bitte die folgenden Hinweise:

Simulation anhalten und fortsetzen: Drücken Sie die Taste T, um die Simulation zu pausieren oder fortzusetzen.

Zeitpunkt in der Simulation ändern: Um gezielt einen bestimmten Zeitpunkt in der Simulation zu betrachten, tragen Sie den gewünschten Zeitpunkt in die Variable list_of_timesteps ein.

Ändern der Widgets: Drücken Sie die Leertaste, um die verschiedenen Widgets anzuzeigen oder auszublenden. Mit den Widgets können Sie zudem wichtige Parameter wie prob_shortest_path, pheromone_increase, reduction_amount und num_ants während der Simulation anpassen.

Auswertung der Simulation: Achten Sie darauf, dass der gleiche run_name verwendet wird, um die Simulation korrekt auszuwerten.

Mehrere Futterquellen untersuchen: Aktivieren Sie die Option multiple_food_sources = True, um die Simulation so zu konfigurieren, dass mehrere Futterquellen untersucht werden.

Eingrenzen der Futterquellen-Distanzen: Nutzen Sie die Parameter max_distance und min_distance, um die Distanzen der zu untersuchenden Futterquellen zu definieren.