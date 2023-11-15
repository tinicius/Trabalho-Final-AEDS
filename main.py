# from google.colab import drive
import pandas as pd
import random
from datetime import datetime
import uuid
import networkx as nx
import matplotlib.pyplot as plt

HOUR_IN_SECONDS = 3600

a = dict()

# drive.mount('/content/drive')

def read_csv(path: str, sep: str):
#   return pd.read_csv("/content/drive/MyDrive/AEDS/{}".format(path), sep=sep)
  return pd.read_csv("./{}".format(path), sep=sep)

airport_acronym = "SBGR" # Sigla ICAO do Aeroporto que vamos analisar

br = read_csv("database/aerodromospublicosv1.csv", sep=";")
brazilian_airports = br["CÓDIGO OACI"].tolist()

df = read_csv("database/VRA_2023_01.csv", sep=';')

isOrigin = df['Sigla ICAO Aeroporto Origem'] == airport_acronym
isDest = df['Sigla ICAO Aeroporto Destino'] == airport_acronym

hasLadingData = ~pd.isna(df['Partida Prevista'])
hasTakeOffData = ~pd.isna(df['Chegada Prevista'])

mask = (isOrigin | isDest) & hasLadingData & hasTakeOffData 

df = df[mask] 

df = df[df['Sigla ICAO Aeroporto Origem'].isin(brazilian_airports)]
df = df[df['Sigla ICAO Aeroporto Destino'].isin(brazilian_airports)]

dados = {
    'origin': df['Sigla ICAO Aeroporto Origem'],
    'destination': df['Sigla ICAO Aeroporto Destino'],
    'landing_data': df['Chegada Prevista'],
    'takeoff_data': df['Chegada Prevista']
}

data_frame = pd.DataFrame(data = dados)
data_frame.to_csv('{}.csv'.format(airport_acronym), index=False)

nodes = {
    "Id": [],
    "Label": [],
}

nodes['Id'] = list(range(0, len(data_frame)))
nodes['Label'] = list(range(0, len(data_frame)))

df = pd.read_csv("{}.csv".format(airport_acronym))

edges = {
    "Source": [],
    "Target": [],
    "Type": [],
    "Id": [],
    "Label": [],
}

def add_edge(source, target, label):
    edges['Id'].append(uuid.uuid4())
    edges['Label'].append(label)
    edges['Source'].append(source)
    edges['Target'].append(target)
    edges['Type'].append("Undirected")

def different_in_seconds(date1, date2):
    time1 = datetime.strptime(date1, "%d/%m/%Y %H:%M")
    time2 = datetime.strptime(date2, "%d/%m/%Y %H:%M")
    return abs((time1 - time2).total_seconds())

for i, f1 in df.iterrows():

    if i == 100:
      break

    for j, f2 in df.iterrows():

        if i == 100:
          break

        if i == j:
            continue

        if f1['origin'] == airport_acronym and f2['origin'] == airport_acronym:
            diff_in_seconds = different_in_seconds(f1["landing_data"], f2["landing_data"])
            if diff_in_seconds <= HOUR_IN_SECONDS:
                add_edge(i, j, diff_in_seconds)

        elif f1['destination'] == airport_acronym and f2['destination'] == airport_acronym:
            diff_in_seconds = different_in_seconds(f1["takeoff_data"], f2["takeoff_data"])
            if diff_in_seconds <= HOUR_IN_SECONDS:
                add_edge(i, j, diff_in_seconds)

        elif f1['origin'] == airport_acronym and f2['destination'] == airport_acronym:
            diff_in_seconds = different_in_seconds(f1["landing_data"], f2["takeoff_data"])
            if diff_in_seconds <= HOUR_IN_SECONDS:
                add_edge(i, j, diff_in_seconds)

        elif f1['destination'] == airport_acronym and f2['origin'] == airport_acronym:
            diff_in_seconds = different_in_seconds(f1["takeoff_data"], f2["landing_data"])
            if diff_in_seconds <= HOUR_IN_SECONDS:
                add_edge(i, j, diff_in_seconds)

nodes_df = pd.DataFrame(nodes)
nodes_df.to_csv('./graph/nodes.csv', index=False)

edges_df = pd.DataFrame(edges)
edges_df.to_csv('./graph/edges.csv', index=False)

vertices = list(nodes_df.columns)[2:]

edge_labels = {(edge['Source'], edge['Target']): edge['Label'] for idx, edge in edges_df.iterrows()}

graph = nx.from_pandas_edgelist(edges_df, "Source", "Target")

def greedy_coloring(graph):
    # Create a dictionary to store the color assigned to each node
    color_dict = {}

    # Iterate through each node in the graph
    for node in graph.nodes():
        
        # Get the colors used by adjacent nodes
        neighbor_colors = {color_dict[neighbor] for neighbor in graph.neighbors(node) if neighbor in color_dict}

        # Find the smallest available color (not used by any adjacent node)
        color = 0
        while color in neighbor_colors:
            color += 1

        # Assign the color to the current node
        color_dict[node] = color

    return color_dict

coloring = greedy_coloring(graph)

# Assign colors to nodes and update labels
for node, color in coloring.items():
    graph.nodes[node]['color'] = color
    graph.nodes[node]['label'] = str(color)

# Draw the graph with node colors and labels
pos = nx.kamada_kawai_layout(graph, scale=10)
node_colors = [graph.nodes[node]['color'] for node in graph.nodes]
node_labels = {node: graph.nodes[node]['label'] for node in graph.nodes}

nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

nx.draw(graph, pos, with_labels=True, labels=node_labels, node_size=700, node_color=node_colors, cmap=plt.cm.rainbow, font_size=10, font_color='black')

plt.show()

edge_data = [(source, target, graph[source][target].get('Type', ''), graph[source][target].get('Id', ''), graph[source][target].get('Label', '')) for source, target in graph.edges]
df = pd.DataFrame(edge_data, columns=['Source', 'Target', 'Type', 'Id', 'Label'])

# Save the DataFrame to a CSV file
df.to_csv('graph_data.csv', index=False)

# Create a DataFrame for the graph nodes
node_data = [(node, graph.nodes[node].get('color', '')) for node in graph.nodes]
node_df = pd.DataFrame(node_data, columns=['Node', 'Color'])

# Save the DataFrame to a CSV file
node_df.to_csv('nodes_data.csv', index=False)