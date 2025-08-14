import pandas as pd

def load_client_data(filepath):
    df = pd.read_excel(filepath)  # Loads the first (and only) sheet
    return df
