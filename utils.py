import os
import pandas as pd


def update_csv_table(csv_table, model_choice):
    selected_model = model_choice.get()
    if selected_model == "SI":
        csv_file = 'SI_Model_Simulation.csv'
    elif selected_model == "SIS":
        csv_file = 'SIS_Model_Simulation.csv'
    elif selected_model == "SIR":
        csv_file = 'SIR_Model_Simulation.csv'

    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        csv_table.delete(*csv_table.get_children())
        csv_table["column"] = list(df.columns)
        csv_table["show"] = "headings"
        for column in csv_table["columns"]:
            csv_table.heading(column, text=column)
        for row in df.itertuples(index=False):
            csv_table.insert("", "end", values=row)
