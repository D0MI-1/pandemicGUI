import random
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import networkx as nx
from si import plot_graph, update_csv_table

def initialize_sir_model(graph, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count, node_positions=None):
    num_nodes = graph.number_of_nodes()
    num_infected = int(initial_infected_fraction * num_nodes)
    infected_nodes = random.sample(list(graph.nodes), num_infected)
    susceptible_nodes = set(graph.nodes) - set(infected_nodes)
    recovered_nodes = set()
    sir_model = {
        "graph": graph,
        "infected_nodes": set(infected_nodes),
        "susceptible_nodes": set(susceptible_nodes),
        "recovered_nodes": set(recovered_nodes),
        "step": 0,
        "statistics": [],
        "node_positions": node_positions if node_positions is not None else nx.spring_layout(graph)  # Generate positions if not provided
    }
    update_statistics(sir_model, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count)
    return sir_model

def update_sir_model(sir_model, beta, gamma, canvas, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count):
    graph = sir_model["graph"]
    infected_nodes = sir_model["infected_nodes"]
    susceptible_nodes = sir_model["susceptible_nodes"]
    recovered_nodes = sir_model["recovered_nodes"]

    new_infected_nodes = set()
    new_recovered_nodes = set()

    for node in infected_nodes:
        if random.random() <= gamma:
            new_recovered_nodes.add(node)
            recovered_nodes.update(new_recovered_nodes)
            continue

        neighbors = set(graph.neighbors(node)) - recovered_nodes
        num_neighbors_to_infect = min(int(beta), len(neighbors))
        neighbors_to_infect = random.sample(neighbors, num_neighbors_to_infect)
        new_infected_nodes.update(neighbors_to_infect)

    infected_nodes.update(new_infected_nodes)
    infected_nodes -= new_recovered_nodes
    sir_model["step"] += 1
    sir_model["statistics"].append({
        'timestep': sir_model["step"],
        'susceptible_nodes': len([node for node in graph.nodes if node not in infected_nodes and node not in recovered_nodes]),
        'infected_nodes': len(infected_nodes),
        'recovered_nodes': len(recovered_nodes)
    })
    update_statistics(sir_model, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count)
    plot_sir_graph(sir_model, f"SIR-Model on Step {sir_model['step']}", canvas)

def update_statistics(sir_model, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count):
    graph = sir_model["graph"]
    infected_nodes = sir_model["infected_nodes"]
    recovered_nodes = sir_model["recovered_nodes"]
    step = sir_model["step"]

    statistics = sir_model["statistics"]
    statistics.append({
        'timestep': step,
        'susceptible_nodes': len([node for node in graph.nodes if node not in infected_nodes and node not in recovered_nodes]),
        'infected_nodes': len(infected_nodes),
        'recovered_nodes': len(recovered_nodes)
    })

    # Update statistics display
    node_count.set(f"Node Count: {graph.number_of_nodes()}")
    infected_count.set(f"Infected Nodes: {len(infected_nodes)}")
    susceptible_count.set(f"Susceptible Nodes: {graph.number_of_nodes() - len(infected_nodes) - len(recovered_nodes)}")
    recovered_count.set(f"Recovered Nodes: {len(recovered_nodes)}")

    # Update CSV data
    csv_file = 'SIR_Model_Simulation.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestep', 'susceptible_nodes', 'infected_nodes', 'recovered_nodes'])
        if not file_exists:
            writer.writeheader()
        for record in statistics[-1:]:
            writer.writerow(record)

    # Update CSV table view
    update_csv_table(csv_table, model_choice)

def plot_sir_graph(sir_model, title, canvas):
    graph = sir_model["graph"]
    infected_nodes = sir_model["infected_nodes"]
    recovered_nodes = sir_model["recovered_nodes"]
    plt.clf()
    pos = sir_model["node_positions"]  # Use positions from the model
    nx.draw_networkx_nodes(graph, pos, node_color=['red' if node in infected_nodes else 'green' if node in recovered_nodes else 'blue' for node in graph.nodes], node_size=800)
    nx.draw_networkx_edges(graph, pos)
    for node, (x, y) in pos.items():
        plt.text(x, y, node, fontsize=8, ha='center', va='center', color='white', weight='bold')
    plt.title(title)
    canvas.draw()
