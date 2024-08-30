import random
from collections import deque
import networkx as nx
from strategies import (
    baseline_disinfection, random_disinfection, random_disinfection_repeat,
    disinfect_combined_repeat, disinfect_most_cubes_repeat,
    disinfect_combined_mul, disinfect_combined_sum, disinfect_combined_mul_repeat,
    disinfect_highest_degree_repeat, disinfect_combined_sum_repeat, disinfect_highest_degree,
    disinfect_most_cubes, disinfect_combined
)
import os
import csv
from utils import update_csv_table

def initialize_pandemic_model_one_disease_no_cure(graph, strategy, node_positions, k_action=4, epidemic_cards=6, nodes_to_infect_at_start=3):
    # 96 Cubes 24 in 4 Colors
    # 48 cities
    # 6 Epidemic card
    # Infection rate 7 tiles, (2,2,2,3,3,4,4)
    # Outbreak marker 8 tiles

    # Get and shuffle all Nodes
    num_nodes = graph.number_of_nodes()
    all_nodes = list(graph.nodes)
    random.shuffle(all_nodes)

    # Initialize stacks
    infection_discard_stack = deque()
    infection_stack = deque(all_nodes)
    player_stack = deque()

    # k Nodes to infect at the start (Pandemic normal value is 3x3, 3x2, 3x1 total 9 nodes)
    # Needs to be set to 3 so we do 3 times the different infection counts
    k_nodes_to_infect = nodes_to_infect_at_start

    # Set the amount of epidemic cards (4,5,6 Pandemic)
    epidemics = epidemic_cards

    infection_rate = [2, 2, 2, 3, 3, 4, 4]
    infection_rate_counter = 0
    outbreak_counter = 0

    k_actions = k_action

    # Set the disinfection strategy
    disinfection_strategy = strategy

    # -------------------------------
    # Start of Epidemic Cards Setup
    # -------------------------------
    if not epidemics == 0:
        # Calculate the chunk size for the epidemics (Floor division)
        chunk_size = num_nodes // epidemics

        # Add chunks with one epidemic node to the player deck
        for i in range(epidemics):
            if i == epidemics - 1:
                chunk = random.sample(all_nodes, len(all_nodes))
            else:
                chunk = random.sample(all_nodes, chunk_size)

            chunk.extend(["Epidemic"])
            random.shuffle(chunk)
            player_stack.extend(chunk)

            # Remove nodes used in this chunk
            all_nodes = list(set(all_nodes) - set(chunk))
    else:
        chunk = random.sample(all_nodes, len(all_nodes))
        random.shuffle(chunk)
        player_stack.extend(chunk)

    # Infect k nodes with 3 disease counters (blue)
    for _ in range(k_nodes_to_infect):
        node = infection_stack.pop()
        graph.nodes[node]["disease_counters"]["blue"] = 3
        infection_discard_stack.append(node)

    # Infect k nodes with 2 disease counters (blue)
    for _ in range(k_nodes_to_infect):
        node = infection_stack.pop()
        graph.nodes[node]["disease_counters"]["blue"] = 2
        infection_discard_stack.append(node)

    # Infect k nodes with 1 disease counter (blue)
    for _ in range(k_nodes_to_infect):
        node = infection_stack.pop()
        graph.nodes[node]["disease_counters"]["blue"] = 1
        infection_discard_stack.append(node)

    # Set the remaining nodes to have 0 disease counters
    for node in infection_stack:
        graph.nodes[node]["disease_counters"]["blue"] = 0

    # Initialize the pandemic model
    pandemic_model = {"graph": graph,
                      "node_positions": node_positions,
                      "infection_stack": infection_stack,
                      "infection_discard_stack": infection_discard_stack,
                      "player_stack": player_stack,
                      "infection_rate": infection_rate,
                      "infection_rate_counter": infection_rate_counter,
                      "outbreak_counter": outbreak_counter,
                      "disinfection_strategy": disinfection_strategy,
                      "k_actions": k_actions,
                      "epidemic_cards": epidemics,
                      "nodes_to_infect_at_start": nodes_to_infect_at_start}

    return pandemic_model

#@title Simulation and CSV creation

def simulate_pandemic_one_disease_no_cure(model, num_steps, run):
    graph = model["graph"]  # Get the graph and stacks from the model
    infection_stack = model["infection_stack"]
    infection_discard_stack = model["infection_discard_stack"]
    player_stack = model["player_stack"]
    infection_rate = model["infection_rate"] # [2, 2, 2, 3, 3, 4, 4]
    infection_rate_counter = model["infection_rate_counter"]
    outbreak_counter = model["outbreak_counter"]
    disinfection_strategy = model["disinfection_strategy"]
    k_actions = model["k_actions"]
    epidemics = model["epidemic_cards"]
    nodes_to_infect_at_start = model["nodes_to_infect_at_start"]

    # Initialize lists to store statistics for each step
    statistics = []
    epidemic_counter = 0
    player_deck_empty  = False

    # Add the init step to the CSV-file
    statistics.append({
        'setup': disinfection_strategy,
        'run': run,  # Index of simulation run
        'k_actions': k_actions,
        'no_epidemic': epidemics,
        'timestep': -1,
        'susceptible_nodes': sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 0),
        'infection_1_nodes': sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 1),
        'infection_2_nodes': sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 2),
        'infection_3_nodes': sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 3),
        'epidemic_cards_drawn': epidemic_counter,
        'outbreaks': outbreak_counter,
        'deck_empty': player_deck_empty,
        'player_stack': len(player_stack),
        'infection_stack': len(infection_stack),
        'infection_discard_stack': len(infection_discard_stack),
        'infection_rate_counter': infection_rate_counter
    })

    for step in range(num_steps):
        # Perform actions (disinfection)
        if disinfection_strategy == "baseline":
            baseline_disinfection(graph, k_actions)
        elif disinfection_strategy == "random":
            random_disinfection(graph, k_actions)
        elif disinfection_strategy == "random_repeat":
            random_disinfection_repeat(graph, k_actions)
        elif disinfection_strategy == "most_cubes":
            disinfect_most_cubes(graph, k_actions)
        elif disinfection_strategy == "most_cubes_repeat":
            disinfect_most_cubes_repeat(graph, k_actions)
        elif disinfection_strategy == "highest_degree":
            disinfect_highest_degree(graph, k_actions)
        elif disinfection_strategy == "highest_degree_repeat":
            disinfect_highest_degree_repeat(graph, k_actions)
        elif disinfection_strategy == "combined":
            disinfect_combined(graph, k_actions)
        elif disinfection_strategy == "combined_repeat":
            disinfect_combined_repeat(graph, k_actions)
        elif disinfection_strategy == "combined_SUM":
            disinfect_combined_sum(graph, k_actions)
        elif disinfection_strategy == "combined_SUM_repeat":
            disinfect_combined_sum_repeat(graph, k_actions)
        elif disinfection_strategy == "combined_MUL":
            disinfect_combined_mul(graph, k_actions)
        elif disinfection_strategy == "combined_MUL_repeat":
            disinfect_combined_mul_repeat(graph, k_actions)


        # Draw 2 player stack cards
        for i in range(2):
            # Check if the stack is empty
            if player_stack:

                # Pop the card from the stack that is drawn
                card_player_drawn = player_stack.pop()

                # Since we don't have a cure we only have the Epidemic logic here
                if card_player_drawn == "Epidemic":
                    # Increment counter for stats
                    epidemic_counter += 1

                    # Infection rate will increase how many nodes get infected each round
                    infection_rate_counter += 1

                    if (infection_stack):
                        # Pop card from the left to simulate a draw from the bottem of the deck
                        node_to_outbreak = infection_stack.popleft()

                        # Add card to the discard stack
                        infection_discard_stack.append(node_to_outbreak)

                        # Add 3 cubes to the epidemic node
                        while graph.nodes[node_to_outbreak]["disease_counters"]["blue"] != 3:
                            graph.nodes[node_to_outbreak]["disease_counters"]["blue"] += 1

                        # Call outbereak (increases the node count) and return the outbreak counter for the CSV-File
                        outbreak_counter = outbreak(graph, node_to_outbreak, "blue", set(node_to_outbreak), outbreak_counter + 1)

                    # Shuffe the discard stack add it on top of the infection stack and delete all nodes from the discard stack
                    random.shuffle(infection_discard_stack)
                    infection_stack.extend(infection_discard_stack)
                    infection_discard_stack.clear()
            else:
                player_deck_empty  = True

        # Draw as many cards as infection rate and infect the cities by 1 cube
        # Game is over if no cards left for the player to draw so we end the infection
        if not player_deck_empty :
            for i in range(infection_rate[infection_rate_counter]):
                if infection_stack:
                    node_to_infect = infection_stack.pop()
                    infection_discard_stack.append(node_to_infect)

                    disease_counter = graph.nodes[node_to_infect]["disease_counters"]["blue"]

                    if disease_counter == 3:
                        outbreak_counter = outbreak(graph, node_to_infect, "blue", set(node_to_infect), outbreak_counter + 1)
                    else:
                        graph.nodes[node_to_infect]["disease_counters"]["blue"] += 1

        # Count node statuses
        susceptible_nodes = sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 0)
        infection_1_nodes = sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 1)
        infection_2_nodes = sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 2)
        infection_3_nodes = sum(1 for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] == 3)
        outbreaks = outbreak_counter

        # Append statistics for this time step
        statistics.append({
            'setup': disinfection_strategy,
            'run': run,  # Index of simulation run
            'k_actions': k_actions,
            'no_epidemic': epidemics,
            'timestep': step,
            'susceptible_nodes': susceptible_nodes,
            'infection_1_nodes': infection_1_nodes,
            'infection_2_nodes': infection_2_nodes,
            'infection_3_nodes': infection_3_nodes,
            'epidemic_cards_drawn': epidemic_counter,
            'outbreaks': outbreaks,
            'deck_empty': player_deck_empty,
            'player_stack': len(player_stack),
            'infection_stack': len(infection_stack),
            'infection_discard_stack': len(infection_discard_stack),
            'infection_rate_counter': infection_rate_counter
        })

    return statistics

def update_statistics_pandemic(statistics, csv_table, model_choice, node_count, infected_count, susceptible_count):
    last_stat = statistics[-1]

    # Update statistics display
    node_count.set(f"Node Count: {last_stat['susceptible_nodes'] + last_stat['infection_1_nodes'] + last_stat['infection_2_nodes'] + last_stat['infection_3_nodes']}")
    infected_count.set(f"Infected Nodes: {last_stat['infection_1_nodes'] + last_stat['infection_2_nodes'] + last_stat['infection_3_nodes']}")
    susceptible_count.set(f"Susceptible Nodes: {last_stat['susceptible_nodes']}")

    # Update CSV data
    csv_file = 'Pandemic_Model_Simulation.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'setup', 'run', 'k_actions', 'no_epidemic', 'timestep',
            'susceptible_nodes', 'infection_1_nodes', 'infection_2_nodes',
            'infection_3_nodes', 'epidemic_cards_drawn', 'outbreaks',
            'deck_empty', 'player_stack', 'infection_stack', 'infection_discard_stack',
            'infection_rate_counter'
        ])
        if not file_exists:
            writer.writeheader()
        for record in statistics:
            writer.writerow(record)

    # Update CSV table view
    update_csv_table(csv_table, model_choice)


def outbreak(graph, node, color, outbreak_nodes=None, outbreak_counter=0):

    # Set of Nodes that had an Outbreak (1 Outbreak per iteration)
    if outbreak_nodes is None:
        outbreak_nodes = set()  # Initialize the set of nodes that have had an outbreak
    outbreak_nodes.add(node)  # Add the current node to the set

    connected_nodes = graph.neighbors(node)
    #print(connected_nodes)

    # Infect every neighbour
    for cn in connected_nodes:
        if cn not in outbreak_nodes:  # Only process the node if it hasn't had an outbreak yet
            if(graph.nodes[cn]['disease_counters'][color] == 3):
                outbreak(graph, cn, color, outbreak_nodes, outbreak_counter + 1)
            else:
                graph.nodes[cn]['disease_counters'][color] += 1

    return outbreak_counter