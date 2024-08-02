# Hier werden die Resultate einer Simulation in ein Excel-Format gemacht
import pandas as pd
import matplotlib.pyplot as plt
import os

run_name = "test_11"

df_filtered = pd.read_excel(f"{run_name}/filtered_df.xlsx")
food_source_distance = pd.read_excel(f"{run_name}/distance_of_food_source.xlsx")
multiple_food_sources = True # Falls man mehrere Food Sources haben will
if multiple_food_sources:
    max_distance = 400
    min_distance = 0
    filtered_food_sources = list(food_source_distance.loc[((food_source_distance["distance"] <= max_distance) & (food_source_distance["distance"] >= min_distance)), "Unnamed: 0"])
else:
    desired_food_source = 123
    filtered_food_sources = list(desired_food_source)

df_total_food = pd.read_excel(f"{run_name}/run_specifications.xlsx") # Extrahieren der Gesamtmenge an Food der verschiedenen Food_Sources

counter = df_total_food.loc[0,"counter"] # Extrahieren des Counters aus der Simulation
df_total_food.drop(columns=["Unnamed: 0","counter"],inplace=True) # Unnötige Spalten rauslöschen  

##########################################################
##                                                      ##
##       Berechnung für die Gesamtmenge an food         ##
##                                                      ##
##########################################################

# Wir wollen von dem filtered_df auf die Gesamtmengenreduktion schliessen können, dafür muss die kumulative Differenz für jeden Zeitschritt berechnet werden

counter_df_filtered = df_filtered[["food_source",'counter']]

# Umformung des Dataframes df_total_food damit er mit df_filtered gemerged werden kann
df_total_food_transposed = df_total_food.T.reset_index() # neuer df initialisieren, da wir df_total_food weiter unten noch brauchen
df_total_food_transposed.columns = ['food_source', 'start_food_per_source']

df_total_food_transposed['food_source'] = df_total_food_transposed['food_source'].astype(int) # Umwandlung der food_source Spalte in int

# Merge df1 with df2_transposed to bring in the subtraction values
df_merged = pd.merge(df_filtered, df_total_food_transposed, on='food_source', how='left') # Mergen der beiden dfs damit die Subtraktion möglich ist

df_merged['food_subtracted'] = df_merged['food'] - df_merged['start_food_per_source'] # berechnet für jede food_source die Differenz zwischen dem Startwert der Source und dem Wert der Source bei einem beliebigen Zeitschritt
print(df_merged)
df_result = df_merged[['food_source', 'food_subtracted']] # Nur die relevanten Spalten behalten
print(df_result)

# Nun brauchen wir die Differenz zwischen aufeinanderfolgenden Zeitschritten einer Source
# Dies wird in der folgenden Hilfsfunktion berechnet
def calculate_differences(df):
    df_copy = df.copy()
    df_copy['food'] = df_copy.groupby('food_source')['food_subtracted'].transform(lambda x: x.diff().fillna(x))    
    return df_copy

df_result_difference = calculate_differences(df_result)
df_result_difference["counter"] = counter_df_filtered["counter"]

df_aggregated = df_result_difference.groupby('counter', as_index=False)['food'].sum() # Summieren über sämtliche Sources in einem Zeitschritt (weil wir hier die Gesamtmenge pro Zeitschritt wollen)
df_aggregated.rename(columns={'food': 'total_food'}, inplace=True)
df_aggregated['cumulative_food'] = df_aggregated['total_food'].cumsum() # Kumulative Summe bilden

# DataFrame bilden welcher so viele Reihen hat wie Zeitschritte und in jedem die Gesamtstartmenge an Food
df_total_startfood = pd.DataFrame({
    'counter': range(counter + 1), 
    'total_food': [df_total_food.iloc[0].sum()] * (counter + 1)  
})

# Nun müssen wir die kumulative Summe an bereits genommenen Essen nur noch von der Startmenge subtrahieren. Dies wird wieder mit dem mergen gemacht

total_food_per_timestep = pd.merge(df_total_startfood, df_aggregated[['counter', 'cumulative_food']], on='counter', how='left')

total_food_per_timestep['cumulative_food'].fillna(method='ffill', inplace=True) # Zeitschritte bei welchen keine Veränderung im Food geschieht, kriegen denselben Wert wie der Zeitschritt davor

total_food_per_timestep['adjusted_total_food'] = total_food_per_timestep['total_food'] + total_food_per_timestep['cumulative_food'] # Die kumulative Summe wird von der Gesamtmenge abgezogen

print(total_food_per_timestep)
total_food_per_timestep.to_excel("total_food_per_timestep.xlsx")
plt.scatter(total_food_per_timestep["counter"],total_food_per_timestep["adjusted_total_food"]) # Darstellung der Gesamtfoodmenge
plt.show()

##########################################################
##                                                      ##
##       Berechnung für eine spezifische Food_Source    ##
##                                                      ##
##########################################################
print(filtered_food_sources)


for specific_food_source in filtered_food_sources:
    print(specific_food_source)
    df_specific_food_source = df_filtered.loc[df_filtered["food_source"] == specific_food_source]

    df_specific_food_source = df_specific_food_source[["counter","food"]]


    if len(df_specific_food_source["counter"]) > 0:
        # Ensure 'counter' is integer
        df_specific_food_source['counter'] = df_specific_food_source['counter'].astype(int)

        # Step 2: Create a full range of 'counter' values
        min_counter = int(df_specific_food_source['counter'].min())
        max_counter = int(df_specific_food_source['counter'].max())

        full_range = pd.DataFrame({'counter': range(min_counter, max_counter + 1)})

        # Step 3: Merge the full range with the original filtered DataFrame
        df_expanded = full_range.merge(df_specific_food_source, on='counter', how='left')

        # Step 4: Forward-fill the 'food' values
        df_expanded['food'] = df_expanded['food'].ffill()

        # Add rows before the existing data
        start_before = 0
        end_before = min_counter - 1
        food_before = df_total_food.loc[0,specific_food_source]  # Set your desired food value for these rows
        df_before = pd.DataFrame({'counter': range(start_before, end_before + 1), 'food': food_before})

        # Add rows after the existing data
        start_after = max_counter + 1
        end_after = counter  # Specify the end value for the 'counter' column
        food_after = df_expanded['food'].iloc[-1]  # Use the last 'food' value from the existing data
        df_after = pd.DataFrame({'counter': range(start_after, end_after + 1), 'food': food_after})

        # Concatenate all DataFrames
        df_final = pd.concat([df_before, df_expanded, df_after], ignore_index=True)

        df_final.to_excel(f"{run_name}/df_final_{specific_food_source}.xlsx")
    else:
        print("Diese Food Source wurde noch nicht besucht.")

