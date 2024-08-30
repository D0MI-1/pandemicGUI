import random

#@title Strategy 0: Baseline disinfect
def baseline_disinfection(graph, k):
    pass

#@title Strategy 1: Randomly Disinfect Nodes (one Cube per Node per Turn)
def random_disinfection(graph, k):
    # Randomly disinfect k nodes with a blue disease counter greater than 0
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]
    nodes_to_disinfect = random.sample(nodes_to_disinfect, min(k, len(nodes_to_disinfect)))

    for node in nodes_to_disinfect:
        graph.nodes[node]["disease_counters"]["blue"] -= 1

#@title Strategy 1: Randomly Disinfect Nodes (Nodes can repeat)
def random_disinfection_repeat(graph, k):
    # Get nodes with a blue disease counter greater than 0
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    # Initialize disinfection count
    disinfection_count = 0

    while nodes_to_disinfect and disinfection_count < k:
        # Randomly select a node to disinfect
        node_to_disinfect = random.choice(nodes_to_disinfect)

        # Decrease the disease counter for the selected node
        graph.nodes[node_to_disinfect]["disease_counters"]["blue"] -= 1

        # Increment disinfection count
        disinfection_count += 1

        # If the counter becomes 0, remove the node from the list
        if graph.nodes[node_to_disinfect]["disease_counters"]["blue"] == 0:
            nodes_to_disinfect.remove(node_to_disinfect)

#@title Strategy 2: Disinfect Nodes with Most Cubes

def disinfect_most_cubes(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    nodes_to_disinfect = sorted(nodes_to_disinfect, key=lambda node: graph.nodes[node]["disease_counters"]["blue"], reverse=True)
    nodes_to_disinfect = nodes_to_disinfect[:k]

    for node in nodes_to_disinfect:
        graph.nodes[node]["disease_counters"]["blue"] -= 1

#@title Strategy 2: Disinfect Nodes with Most Cubes (Nodes can repeat)
def disinfect_most_cubes_repeat(graph, k):
    # Get nodes with a blue disease counter greater than 0
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    # Sort nodes by blue disease counter
    nodes_to_disinfect = sorted(nodes_to_disinfect, key=lambda node: graph.nodes[node]["disease_counters"]["blue"], reverse=True)

    # Initialize disinfection count
    disinfection_count = 0

    while nodes_to_disinfect and disinfection_count < k:
        # Select the node with the most cubes
        node_to_disinfect = nodes_to_disinfect[0]

        graph.nodes[node_to_disinfect]["disease_counters"]["blue"] -= 1

        disinfection_count += 1

        # If the counter becomes 0, remove the node from the list
        if graph.nodes[node_to_disinfect]["disease_counters"]["blue"] == 0:
            nodes_to_disinfect.remove(node_to_disinfect)

        nodes_to_disinfect.sort(key=lambda node: graph.nodes[node]["disease_counters"]["blue"], reverse=True)

#@title Strategy 3: Disinfect Nodes with Highest Degree

def disinfect_highest_degree(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    nodes_to_disinfect = sorted(nodes_to_disinfect, key=lambda node: graph.degree[node], reverse=True)
    nodes_to_disinfect = nodes_to_disinfect[:k]

    for node in nodes_to_disinfect:
        graph.nodes[node]["disease_counters"]["blue"] -= 1

#@title Strategy 3: Disinfect Nodes with Highest Degree (repeat)

def disinfect_highest_degree_repeat(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    nodes_to_disinfect = sorted(nodes_to_disinfect, key=lambda node: graph.degree[node], reverse=True)

    disinfection_count = 0

    while nodes_to_disinfect and disinfection_count < k:
        node_to_disinfect = nodes_to_disinfect[0]

        graph.nodes[node_to_disinfect]["disease_counters"]["blue"] -= 1

        disinfection_count += 1

        if graph.nodes[node_to_disinfect]["disease_counters"]["blue"] == 0:
            nodes_to_disinfect.remove(node_to_disinfect)

        nodes_to_disinfect.sort(key=lambda node: graph.degree[node], reverse=True)

#@title Strategy 4: Combination of Most Cubes and Highest Degree (only sort)

def disinfect_combined(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    nodes_to_disinfect = sorted(nodes_to_disinfect, key=lambda node: (graph.nodes[node]["disease_counters"]["blue"], graph.degree[node]), reverse=True)
    nodes_to_disinfect = nodes_to_disinfect[:k]

    for node in nodes_to_disinfect:
        graph.nodes[node]["disease_counters"]["blue"] -= 1

#@title Strategy 4: Combination of Most Cubes and Highest Degree (only sort)(repeat)

def disinfect_combined_repeat(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    nodes_to_disinfect = sorted(nodes_to_disinfect, key=lambda node: (graph.nodes[node]["disease_counters"]["blue"], graph.degree[node]), reverse=True)

    disinfection_count = 0

    while nodes_to_disinfect and disinfection_count < k:
        node_to_disinfect = nodes_to_disinfect[0]

        graph.nodes[node_to_disinfect]["disease_counters"]["blue"] -= 1

        disinfection_count += 1

        if graph.nodes[node_to_disinfect]["disease_counters"]["blue"] == 0:
            nodes_to_disinfect.remove(node_to_disinfect)

        nodes_to_disinfect.sort(key=lambda node: (graph.nodes[node]["disease_counters"]["blue"], graph.degree[node]), reverse=True)

#@title Strategy 5: Combination of Most Cubes and Highest Degree (SUM function)

def disinfect_combined_sum(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    # Define a function to calculate the score for a node
    def calculate_score(node):
        degree_score = min(5, graph.degree[node])
        disease_score = min(3, graph.nodes[node]["disease_counters"]["blue"])
        return degree_score + disease_score

    # Sort the nodes based on the score
    nodes_to_disinfect = sorted(nodes_to_disinfect, key=calculate_score, reverse=True)
    nodes_to_disinfect = nodes_to_disinfect[:k]

    for node in nodes_to_disinfect:
        graph.nodes[node]["disease_counters"]["blue"] -= 1


#@title Strategy 5: Combination of Most Cubes and Highest Degree (SUM function)(repeat)
def disinfect_combined_sum_repeat(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    # Define a function to calculate the score for a node
    def calculate_score(node):
        degree_score = min(5, graph.degree[node])
        disease_score = min(3, graph.nodes[node]["disease_counters"]["blue"])
        return degree_score + disease_score

    disinfection_count = 0

    nodes_to_disinfect = sorted(nodes_to_disinfect, key=calculate_score, reverse=True)

    while nodes_to_disinfect and disinfection_count < k:
        node_to_disinfect = nodes_to_disinfect[0]

        graph.nodes[node_to_disinfect]["disease_counters"]["blue"] -= 1

        disinfection_count += 1

        if graph.nodes[node_to_disinfect]["disease_counters"]["blue"] == 0:
            nodes_to_disinfect.remove(node_to_disinfect)

        # Sort the nodes based on the score
        nodes_to_disinfect.sort(key=calculate_score, reverse=True)

#@title Strategy 6: Combination of Most Cubes and Highest Degree (MUL function)
def disinfect_combined_mul(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    # Define a function to calculate the score for a node
    def calculate_score(node):
        degree_score = min(5, graph.degree[node])
        disease_score = min(3, graph.nodes[node]["disease_counters"]["blue"])
        return degree_score * disease_score

    # Sort the nodes based on the score
    nodes_to_disinfect = sorted(nodes_to_disinfect, key=calculate_score, reverse=True)
    nodes_to_disinfect = nodes_to_disinfect[:k]

    for node in nodes_to_disinfect:
        graph.nodes[node]["disease_counters"]["blue"] -= 1


#@title Strategy 6: Combination of Most Cubes and Highest Degree (MUL function)(repeat)
def disinfect_combined_mul_repeat(graph, k):
    nodes_to_disinfect = [node for node in graph.nodes if graph.nodes[node]["disease_counters"]["blue"] > 0]

    # Define a function to calculate the score for a node
    def calculate_score(node):
        degree_score = min(5, graph.degree[node])
        disease_score = min(3, graph.nodes[node]["disease_counters"]["blue"])
        return degree_score * disease_score

    disinfection_count = 0

    nodes_to_disinfect = sorted(nodes_to_disinfect, key=calculate_score, reverse=True)

    while nodes_to_disinfect and disinfection_count < k:
        node_to_disinfect = nodes_to_disinfect[0]

        graph.nodes[node_to_disinfect]["disease_counters"]["blue"] -= 1

        disinfection_count += 1

        if graph.nodes[node_to_disinfect]["disease_counters"]["blue"] == 0:
            nodes_to_disinfect.remove(node_to_disinfect)

        # Sort the nodes based on the score
        nodes_to_disinfect.sort(key=calculate_score, reverse=True)