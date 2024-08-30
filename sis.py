import random
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import networkx as nx
from si import plot_graph, update_statistics
from utils import update_csv_table

# Function to initialize the SIS model
def initialize_sis_model(graph, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, node_positions=None):
    num_nodes = graph.number_of_nodes()
    num_infected = int(initial_infected_fraction * num_nodes)
    infected_nodes = random.sample(list(graph.nodes), num_infected)
    susceptible_nodes = set(graph.nodes) - set(infected_nodes)
    sis_model = {"graph": graph, "infected_nodes": set(infected_nodes), "susceptible_nodes": set(susceptible_nodes), "step": 0, "statistics": [], "node_positions": node_positions if node_positions is not None else nx.spring_layout(graph)}
    update_statistics(sis_model, csv_table, model_choice, node_count, infected_count, susceptible_count)
    return sis_model

# Function to update the SIS model by one step
def update_sis_model(sis_model, beta, gamma, canvas, csv_table, model_choice, node_count, infected_count, susceptible_count):
    graph = sis_model["graph"]
    infected_nodes = sis_model["infected_nodes"]
    susceptible_nodes = sis_model["susceptible_nodes"]
    new_infected_nodes = set()
    new_susceptible_nodes = set()

    for node in infected_nodes:
        if random.random() <= gamma:
            new_susceptible_nodes.add(node)
        else:
            neighbors = set(graph.neighbors(node))
            num_neighbors_to_infect = min(int(beta), len(neighbors))
            neighbors_to_infect = random.sample(neighbors, num_neighbors_to_infect)
            new_infected_nodes.update(neighbors_to_infect)

    infected_nodes.update(new_infected_nodes)
    infected_nodes -= new_susceptible_nodes

    sis_model["step"] += 1
    sis_model["statistics"].append({
        'timestep': sis_model["step"],
        'susceptible_nodes': len([node for node in graph.nodes if node not in infected_nodes]),
        'infected_nodes': len(infected_nodes),
    })
    update_statistics(sis_model, csv_table, model_choice, node_count, infected_count, susceptible_count)

    plot_graph(sis_model, f"SIS-Model on Step {sis_model['step']}", canvas)

def update_statistics(sis_model, csv_table, model_choice, node_count, infected_count, susceptible_count):
    graph = sis_model["graph"]
    infected_nodes = sis_model["infected_nodes"]
    step = sis_model["step"]

    statistics = sis_model["statistics"]
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
    csv_file = 'SIS_Model_Simulation.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestep', 'susceptible_nodes', 'infected_nodes'])
        if not file_exists:
            writer.writeheader()
        for record in statistics[-1:]:
            writer.writerow(record)

    # Update CSV table view
    update_csv_table(csv_table, model_choice)
