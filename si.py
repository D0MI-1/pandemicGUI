# si.py
import random
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import networkx as nx
from utils import update_csv_table

# Function to initialize the SI model
def initialize_si_model(graph, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, node_positions=None):
    num_nodes = graph.number_of_nodes()
    num_infected = int(initial_infected_fraction * num_nodes)
    infected_nodes = random.sample(list(graph.nodes), num_infected)
    si_model = {"graph": graph, "infected_nodes": set(infected_nodes), "step": 0, "statistics": [],"node_positions": node_positions if node_positions is not None else nx.spring_layout(graph)}
    update_statistics(si_model, csv_table, model_choice, node_count, infected_count, susceptible_count)
    return si_model

def update_si_model(si_model, canvas, csv_table, model_choice, node_count, infected_count, susceptible_count):
    graph = si_model["graph"]
    infected_nodes = si_model["infected_nodes"]
    new_infected_nodes = set()

    for node in infected_nodes:
        neighbors = set(graph.neighbors(node))
        new_infected_nodes.update(neighbors - infected_nodes)

    infected_nodes.update(new_infected_nodes)
    si_model["step"] += 1
    update_statistics(si_model, csv_table, model_choice, node_count, infected_count, susceptible_count)

    plot_graph(si_model, f"SI-Model on Step {si_model['step']}", canvas)

    return len(infected_nodes) == graph.number_of_nodes()  # Indicate whether the simulation is complete

def plot_graph(si_model, title, canvas):
    graph = si_model["graph"]
    infected_nodes = si_model["infected_nodes"]
    plt.clf()
    pos = si_model["node_positions"]  # Use positions from the model
    nx.draw_networkx_nodes(graph, pos, node_color=['red' if node in infected_nodes else 'blue' for node in graph.nodes], node_size=800)
    nx.draw_networkx_edges(graph, pos)
    for node, (x, y) in pos.items():
        plt.text(x, y, node, fontsize=8, ha='center', va='center', color='white', weight='bold')
    plt.title(title)
    canvas.draw()

def update_statistics(si_model, csv_table, model_choice, node_count, infected_count, susceptible_count):
    graph = si_model["graph"]
    infected_nodes = si_model["infected_nodes"]
    step = si_model["step"]

    statistics = si_model["statistics"]
    statistics.append({
        'timestep': step,
        'susceptible_nodes': len([node for node in graph.nodes if node not in infected_nodes]),
        'infected_nodes': len(infected_nodes)
    })

    # Update statistics display
    node_count.set(f"Node Count: {graph.number_of_nodes()}")
    infected_count.set(f"Infected Nodes: {len(infected_nodes)}")
    susceptible_count.set(f"Susceptible Nodes: {graph.number_of_nodes() - len(infected_nodes)}")

    # Update CSV data
    csv_file = 'SI_Model_Simulation.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestep', 'susceptible_nodes', 'infected_nodes'])
        if not file_exists:
            writer.writeheader()
        for record in statistics[-1:]:
            writer.writerow(record)

    # Update CSV table view
    update_csv_table(csv_table, model_choice)
