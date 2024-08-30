import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import random
import pandas as pd
import os
import csv
from pandastable import Table, TableModel
from si import initialize_si_model, update_si_model, plot_graph, update_statistics as update_statistics_si
from sis import initialize_sis_model, update_sis_model, update_statistics as update_statistics_sis
from sir import initialize_sir_model, plot_sir_graph, update_sir_model, update_statistics as update_statistics_sir
from utils import update_csv_table
from pandemic import initialize_pandemic_model_one_disease_no_cure, simulate_pandemic_one_disease_no_cure, update_statistics_pandemic

matplotlib.use('TkAgg')

# Create a sample graph
G = nx.cycle_graph(10)

# Define possible column names
NODE_COLUMN_NAMES = ['node', 'Node', 'city', 'City']
EDGE_SOURCE_COLUMN_NAMES = ['source', 'Source', 'city1', 'City1']
EDGE_TARGET_COLUMN_NAMES = ['target', 'Target', 'city2', 'City2']

# Function to find the correct column name
def find_column_name(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

def load_nodes_csv():
    global nodes_csv_path
    nodes_csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    nodes_csv_label.config(text=nodes_csv_path)

def load_edges_csv():
    global edges_csv_path
    edges_csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    edges_csv_label.config(text=edges_csv_path)

def initialize_ui():
    disease_type_label.pack_forget()
    disease_type_choice.pack_forget()
    cure_status_label.pack_forget()
    cure_status_choice.pack_forget()
    disinfection_strategy_label.pack_forget()
    disinfection_strategy_choice.pack_forget()

def on_model_choice_change(event):
    selected_model = model_choice.get()
    if selected_model == "SI":
        beta_label.pack_forget()
        beta_entry.pack_forget()
        gamma_label.pack_forget()
        gamma_entry.pack_forget()
        disease_type_label.pack_forget()
        disease_type_choice.pack_forget()
        cure_status_label.pack_forget()
        cure_status_choice.pack_forget()
        disinfection_strategy_label.pack_forget()
        disinfection_strategy_choice.pack_forget()
    elif selected_model == "SIS" or selected_model == "SIR":
        beta_label.pack(side=tk.LEFT, before=update_graph_button)
        beta_entry.pack(side=tk.LEFT, before=update_graph_button)
        gamma_label.pack(side=tk.LEFT, before=update_graph_button)
        gamma_entry.pack(side=tk.LEFT, before=update_graph_button)
        disease_type_label.pack_forget()
        disease_type_choice.pack_forget()
        cure_status_label.pack_forget()
        cure_status_choice.pack_forget()
        disinfection_strategy_label.pack_forget()
        disinfection_strategy_choice.pack_forget()
    elif selected_model == "Pandemic":
        beta_label.pack_forget()
        beta_entry.pack_forget()
        gamma_label.pack_forget()
        gamma_entry.pack_forget()
        disease_type_label.pack(side=tk.LEFT, before=update_graph_button)
        disease_type_choice.pack(side=tk.LEFT, before=update_graph_button)
        cure_status_label.pack(side=tk.LEFT, before=update_graph_button)
        cure_status_choice.pack(side=tk.LEFT, before=update_graph_button)
        disinfection_strategy_label.pack(side=tk.LEFT, before=update_graph_button)
        disinfection_strategy_choice.pack(side=tk.LEFT, before=update_graph_button)

def update_statistics_model(statistics=None):
    selected_model = model_choice.get()
    if selected_model == "SI":
        update_statistics_si(model, csv_table, model_choice, node_count, infected_count, susceptible_count)
    elif selected_model == "SIS":
        update_statistics_sis(model, csv_table, model_choice, node_count, infected_count, susceptible_count)
    elif selected_model == "SIR":
        update_statistics_sir(model, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count)
    elif selected_model == "Pandemic" and statistics is not None:
        update_statistics_pandemic(statistics, csv_table, model_choice, node_count, infected_count, susceptible_count)

def update_graph():
    global model
    selected_graph = graph_choice.get()
    selected_model = model_choice.get()
    initial_infected_fraction = int(initial_fraction_entry.get()) / 100.0
    num_nodes = int(node_amount_entry.get()) if node_amount_entry.get() else 10
    beta = float(beta_entry.get())
    gamma = float(gamma_entry.get())

    if selected_model == "Pandemic":
        disinfection_strategy_selected = disinfection_strategy_choice.get()
        cure_status_selected = cure_status_choice.get()
        disease_choice_selected = disease_type_choice.get()

    if selected_graph == "Cycle Graph":
        G = nx.cycle_graph(num_nodes)
        node_positions = None
    elif selected_graph == "Complete Graph":
        G = nx.complete_graph(num_nodes)
        node_positions = None
    elif selected_graph == "Star Graph":
        G = nx.star_graph(num_nodes - 1)  # Star graph has n-1 peripheral nodes and 1 center node
        node_positions = None
    elif selected_graph == "Krackhardt Kite Graph":
        G = nx.krackhardt_kite_graph()  # Fixed size graph
        node_positions = None
    elif selected_graph == "CSV Graph":
        if nodes_csv_path and edges_csv_path:
            nodes_df = pd.read_csv(nodes_csv_path)
            edges_df = pd.read_csv(edges_csv_path)

            node_col = find_column_name(nodes_df, NODE_COLUMN_NAMES)
            source_col = find_column_name(edges_df, EDGE_SOURCE_COLUMN_NAMES)
            target_col = find_column_name(edges_df, EDGE_TARGET_COLUMN_NAMES)

            if node_col and source_col and target_col:
                G = nx.from_pandas_edgelist(edges_df, source=source_col, target=target_col)
                G.add_nodes_from(nodes_df[node_col])
                node_positions = None
            else:
                print("CSV files must have the required columns for nodes and edges.")
                return
        else:
            print("Please select both nodes and edges CSV files.")
            return
    elif selected_graph == "Pandemic Graph":
        cities_df = pd.read_csv("csv_to_load/cities.csv", index_col='City')
        disease_counters_df = pd.read_csv("csv_to_load/disease_counters.csv", index_col='City')
        edges_df = pd.read_csv("csv_to_load/edges.csv")
        positions_df = pd.read_csv("csv_to_load/node_positions.csv", index_col='City')

        G = nx.Graph()
        for city, color in cities_df['Color'].items():
            G.add_node(city, color=color)
        G.add_edges_from(edges_df.values)

        node_positions = positions_df.apply(tuple, axis=1).to_dict()
        model = {"graph": G, "node_positions": node_positions}

        if selected_model == "Pandemic":
            for city, counters in disease_counters_df.iterrows():
                model["graph"].nodes[city]['disease_counters'] = counters.to_dict()

            model = initialize_pandemic_model_one_disease_no_cure(model["graph"], disinfection_strategy_selected, model["node_positions"])
            plot_pandemic_graph(model, "Pandemic Graph", canvas, pandemic_mode=True)
        else:
            plot_pandemic_graph(model, "Pandemic Graph", canvas, pandemic_mode=False)
            if selected_model == "SI":
                model = initialize_si_model(G, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, node_positions)
                plot_graph(model, f"SI-Model on {selected_graph}", canvas)
            elif selected_model == "SIS":
                model = initialize_sis_model(G, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, node_positions)
                plot_graph(model, f"SIS-Model on {selected_graph}", canvas)
            elif selected_model == "SIR":
                model = initialize_sir_model(G, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count, node_positions)
                plot_sir_graph(model, f"SIR-Model on {selected_graph}", canvas)
        run_button.config(state=tk.NORMAL)
        run_steps_button.config(state=tk.NORMAL)
        return

    else:
        G = nx.cycle_graph(num_nodes)  # Default graph
        node_positions = None

    if selected_model == "SI":
        model = initialize_si_model(G, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, node_positions)
        plot_graph(model, f"SI-Model on {selected_graph}", canvas)
        run_button.config(state=tk.NORMAL)
        run_steps_button.config(state=tk.NORMAL)
    elif selected_model == "SIS":
        model = initialize_sis_model(G, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, node_positions)
        plot_graph(model, f"SIS-Model on {selected_graph}", canvas)
        run_button.config(state=tk.NORMAL)
        run_steps_button.config(state=tk.NORMAL)
    elif selected_model == "SIR":
        model = initialize_sir_model(G, initial_infected_fraction, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count, node_positions)
        plot_sir_graph(model, f"SIR-Model on {selected_graph}", canvas)
        run_button.config(state=tk.NORMAL)
        run_steps_button.config(state=tk.NORMAL)

def on_graph_choice_change(event):
    selected_graph = graph_choice.get()
    if selected_graph == "Krackhardt Kite Graph":
        node_amount_label.pack_forget()  # Hide label
        node_amount_entry.pack_forget()  # Hide entry
        csv_frame.pack_forget()
        model_choice.config(values=["SI", "SIS", "SIR"])
        initialize_ui()  # Hide pandemic-specific options
    elif selected_graph == "CSV Graph":
        node_amount_label.pack_forget()
        node_amount_entry.pack_forget()
        csv_frame.pack(side=tk.TOP, fill=tk.X)
        model_choice.config(values=["SI", "SIS", "SIR"])
        initialize_ui()  # Hide pandemic-specific options
    elif selected_graph == "Pandemic Graph":
        node_amount_label.pack_forget()
        node_amount_entry.pack_forget()
        csv_frame.pack_forget()
        model_choice.config(values=["Pandemic", "SI", "SIS", "SIR"])
        model_choice.set("Pandemic")  # Default to Pandemic model
        on_model_choice_change(None)  # Show pandemic-specific options
    else:
        if not node_amount_label.winfo_ismapped():  # Check if not already packed
            node_amount_label.pack(side=tk.LEFT, before=initial_fraction_label)  # Pack label if not visible
        if not node_amount_entry.winfo_ismapped():  # Check if not already packed
            node_amount_entry.pack(side=tk.LEFT, after=node_amount_label)  # Pack entry if not visible
        csv_frame.pack_forget()
        model_choice.config(values=["SI", "SIS", "SIR"])
        initialize_ui()  # Hide pandemic-specific options
    model_choice.current(0)

'''
# Function to update CSV table
def update_csv_table():
    csv_file = 'Model_Simulation.csv'
    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        csv_table.delete(*csv_table.get_children())
        csv_table["column"] = list(df.columns)
        csv_table["show"] = "headings"
        for column in csv_table["columns"]:
            csv_table.heading(column, text=column)
        for row in df.itertuples(index=False):
            csv_table.insert("", "end", values=row)
'''

def run_pandemic_model_steps():
    steps = int(steps_entry.get())
    model.run_steps(steps)
    plot_pandemic_graph(model, f"Pandemic Model - Steps {steps}", canvas, pandemic_mode=True)

def plot_pandemic_graph(model, title, canvas, pandemic_mode=True):
    G = model["graph"]
    node_positions = model["node_positions"]
    plt.clf()

    if pandemic_mode:
        node_colors = [G.nodes[city]['color'] for city in G.nodes()]
        yellow_nodes = [city for city, color in G.nodes(data='color') if color == 'yellow']
        font_colors = {city: 'black' if city in yellow_nodes else 'white' for city in G.nodes()}

        nx.draw_networkx_nodes(G, pos=node_positions, node_color=node_colors, node_size=800)
        nx.draw_networkx_edges(G, pos=node_positions)

        for node, (x, y) in node_positions.items():
            plt.text(x, y, node, fontsize=8, ha='center', va='center', color=font_colors[node], weight='bold')

        for node, (x, y) in node_positions.items():
            counters = G.nodes[node]['disease_counters']
            plt.text(x - 4, y + 3, f"{counters['blue']}", fontsize=8, ha='center', va='center', color='blue', weight='bold')
            plt.text(x - 1.5, y + 3, f"{counters['black']}", fontsize=8, ha='center', va='center', color='black', weight='bold')
            plt.text(x + 1.5, y + 3, f"{counters['red']}", fontsize=8, ha='center', va='center', color='red', weight='bold')
            plt.text(x + 4, y + 3, f"{counters['yellow']}", fontsize=8, ha='center', va='center', color='yellow', weight='bold')
    else:
        nx.draw_networkx_nodes(G, pos=node_positions, node_color='blue', node_size=800)
        nx.draw_networkx_edges(G, pos=node_positions)
        for node, (x, y) in node_positions.items():
            plt.text(x, y, node, fontsize=8, ha='center', va='center', color='white', weight='bold')

    plt.title(title)
    canvas.draw()


# Function to run the SI model for a specified number of steps
def run_si_model_steps():
    steps = int(steps_entry.get())
    for _ in range(steps):
        if update_si_model(model, canvas, csv_table, model_choice, node_count, infected_count, susceptible_count):
            break  # Stop if the simulation is complete

def run_sis_model_steps():
    steps = int(steps_entry.get())
    for _ in range(steps):
        update_sis_model(model, float(beta_entry.get()), float(gamma_entry.get()), canvas, csv_table, model_choice, node_count, infected_count, susceptible_count)

def run_sir_model_steps():
    steps = int(steps_entry.get())
    for _ in range(steps):
        update_sir_model(model, float(beta_entry.get()), float(gamma_entry.get()), canvas, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count)

def run_pandemic_model_steps():
    steps = int(steps_entry.get())
    statistics = simulate_pandemic_one_disease_no_cure(model, steps, run=0)
    update_statistics_model(statistics)
    plot_pandemic_graph(model, f"Pandemic Model - Steps {steps}", canvas, pandemic_mode=True)

# Create the main GUI window
# Create the main GUI window
root = tk.Tk()
root.title("Graph Visualization")

# Create a main frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

# Create a frame for the graph
graph_frame = tk.Frame(main_frame)
graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Create a frame for the tabs
tabs_frame = tk.Frame(main_frame)
tabs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

# Create tabs
tab_control = ttk.Notebook(tabs_frame)
tab1 = tk.Frame(tab_control)
tab2 = tk.Frame(tab_control)

tab_control.add(tab1, text='Statistics')
tab_control.add(tab2, text='CSV Data')
tab_control.pack(expand=1, fill='both')

# Graph Visualization
canvas = FigureCanvas(plt.figure())
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Update Graph controls
update_graph_frame = tk.Frame(graph_frame)
update_graph_frame.pack(side=tk.TOP, fill=tk.X)

graph_choice_label = tk.Label(update_graph_frame, text="Select Graph:")
graph_choice_label.pack(side=tk.LEFT)
graph_choice = ttk.Combobox(update_graph_frame, values=["Cycle Graph", "Complete Graph", "Star Graph", "Krackhardt Kite Graph", "CSV Graph", "Pandemic Graph"])
graph_choice.pack(side=tk.LEFT)
graph_choice.current(0)
graph_choice.bind("<<ComboboxSelected>>", on_graph_choice_change)

model_choice_label = tk.Label(update_graph_frame, text="Select Model:")
model_choice_label.pack(side=tk.LEFT)
model_choice = ttk.Combobox(update_graph_frame, values=["SI", "SIS", "SIR", "Pandemic"])
model_choice.bind("<<ComboboxSelected>>", on_model_choice_change)
model_choice.pack(side=tk.LEFT)
model_choice.current(0)

node_amount_label = tk.Label(update_graph_frame, text="Number of Nodes:")
node_amount_label.pack(side=tk.LEFT)
node_amount_entry = tk.Entry(update_graph_frame, width=5)
node_amount_entry.pack(side=tk.LEFT)
node_amount_entry.insert(0, "10")  # Default value

initial_fraction_label = tk.Label(update_graph_frame, text="Initial Infected (%):")
initial_fraction_label.pack(side=tk.LEFT)
initial_fraction_entry = tk.Entry(update_graph_frame, width=5)
initial_fraction_entry.pack(side=tk.LEFT)
initial_fraction_entry.insert(0, "10")  # Default value

beta_label = tk.Label(update_graph_frame, text="Beta:")
beta_label.pack(side=tk.LEFT)
beta_entry = tk.Entry(update_graph_frame, width=5)
beta_entry.pack(side=tk.LEFT)
beta_entry.insert(0, "0.3")  # Default value

beta_label.pack_forget()
beta_entry.pack_forget()

gamma_label = tk.Label(update_graph_frame, text="Gamma:")
gamma_label.pack(side=tk.LEFT)
gamma_entry = tk.Entry(update_graph_frame, width=5)
gamma_entry.pack(side=tk.LEFT)
gamma_entry.insert(0, "0.1")  # Default value

gamma_label.pack_forget()
gamma_entry.pack_forget()

update_graph_button = tk.Button(update_graph_frame, text="Initialize Graph", command=update_graph)
update_graph_button.pack(side=tk.LEFT)

run_button = tk.Button(update_graph_frame, text="Run One Step", command=lambda: (
    (update_si_model(model, canvas, csv_table, model_choice, node_count, infected_count, susceptible_count) and update_statistics_model()) if model_choice.get() == "SI" else
    (update_sis_model(model, float(beta_entry.get()), float(gamma_entry.get()), canvas, csv_table, model_choice, node_count, infected_count, susceptible_count) and update_statistics_model()) if model_choice.get() == "SIS" else
    (update_sir_model(model, float(beta_entry.get()), float(gamma_entry.get()), canvas, csv_table, model_choice, node_count, infected_count, susceptible_count, recovered_count) and update_statistics_model()) if model_choice.get() == "SIR" else
    (lambda: [statistics := simulate_pandemic_one_disease_no_cure(model, 1, run=0), update_statistics_model(statistics), plot_pandemic_graph(model, f"Pandemic Model - Step {model['step']}", canvas, pandemic_mode=True)])()
))
run_button.pack(side=tk.LEFT)


steps_label = tk.Label(update_graph_frame, text="Number of Steps:")
steps_label.pack(side=tk.LEFT)
steps_entry = tk.Entry(update_graph_frame, width=5)
steps_entry.pack(side=tk.LEFT)
steps_entry.insert(0, "10")  # Default value

run_steps_button = tk.Button(update_graph_frame, text="Run Steps", command=lambda: (
    run_si_model_steps() if model_choice.get() == "SI" else
    run_sis_model_steps() if model_choice.get() == "SIS" else
    run_sir_model_steps() if model_choice.get() == "SIR" else
    run_pandemic_model_steps
))
run_steps_button.pack(side=tk.LEFT)

#Pandemic code
# Additional controls for Pandemic Graph
disease_type_label  = tk.Label(update_graph_frame, text="Select Disease Type:")
disease_type_label .pack(side=tk.LEFT)
disease_type_choice  = ttk.Combobox(update_graph_frame, values=["One Disease", "All Diseases"])
disease_type_choice .pack(side=tk.LEFT)
disease_type_choice .current(0)

cure_status_label  = tk.Label(update_graph_frame, text="Cure Status:")
cure_status_label .pack(side=tk.LEFT)
cure_status_choice  = ttk.Combobox(update_graph_frame, values=["No Cure", "With Cure"])
cure_status_choice .pack(side=tk.LEFT)
cure_status_choice .current(0)

disinfection_strategy_label  = tk.Label(update_graph_frame, text="Disinfection Strategy:")
disinfection_strategy_label.pack(side=tk.LEFT)
disinfection_strategy_choice  = ttk.Combobox(update_graph_frame, values=["baseline", "random", "random_repeat", "most_cubes", "most_cubes_repeat", "highest_degree", "highest_degree_repeat", "combined", "combined_repeat", "combined_SUM", "combined_SUM_repeat", "combined_MUL", "combined_MUL_repeat"])
disinfection_strategy_choice .pack(side=tk.LEFT)
disinfection_strategy_choice .current(0)

# CSV file upload frame
csv_frame = tk.Frame(update_graph_frame)
csv_nodes_button = tk.Button(csv_frame, text="Load Nodes CSV", command=load_nodes_csv)
csv_nodes_button.pack(side=tk.LEFT)
nodes_csv_label = tk.Label(csv_frame, text="No file selected")
nodes_csv_label.pack(side=tk.LEFT)

csv_edges_button = tk.Button(csv_frame, text="Load Edges CSV", command=load_edges_csv)
csv_edges_button.pack(side=tk.LEFT)
edges_csv_label = tk.Label(csv_frame, text="No file selected")
edges_csv_label.pack(side=tk.LEFT)
csv_frame.pack_forget()  # Hide initially

# Statistics Tab
node_count = tk.StringVar()
node_count.set("Node Count: 0")
node_count_label = tk.Label(tab1, textvariable=node_count)
node_count_label.pack()

infected_count = tk.StringVar()
infected_count.set("Infected Nodes: 0")
infected_count_label = tk.Label(tab1, textvariable=infected_count)
infected_count_label.pack()

susceptible_count = tk.StringVar()
susceptible_count.set("Susceptible Nodes: 0")
susceptible_count_label = tk.Label(tab1, textvariable=susceptible_count)
susceptible_count_label.pack()

recovered_count = tk.StringVar()  # For SIR model
recovered_count.set("Recovered Nodes: 0")  # For SIR model
recovered_count_label = tk.Label(tab1, textvariable=recovered_count)
recovered_count_label.pack()

update_statistics_button = tk.Button(tab1, text="Update Statistics", command=update_statistics_model)
update_statistics_button.pack()

# CSV Data Tab
csv_table = ttk.Treeview(tab2)
csv_table.pack(fill=tk.BOTH, expand=1)

update_csv_table_button = tk.Button(tab2, text="Update CSV Data", command=update_csv_table)
update_csv_table_button.pack()
# Initial update
update_graph()
initialize_ui()
root.mainloop()

