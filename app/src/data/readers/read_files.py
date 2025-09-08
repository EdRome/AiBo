import os
import pandas as pd

def read_file(file_path):
    match file_path.type:
        case "text/csv":
            return pd.read_csv(file_path)
        case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return pd.read_excel(file_path, engine="openpyxl")
        case "application/vnd.ms-excel":
            return pd.read_excel(file_path, engine="openpyxl")
        case _:
            raise ValueError("Unsupported file type")

def _read_files(dataset_path):
    time = None
    fact = None
    trans = None
    item = None
    store = None
    customer = None

    # List files in the downloaded directory
    print("Files in the downloaded directory:")
    print(dataset_path)
    for root, _, files in os.walk(dataset_path):
        for name in files:
            print(os.path.join(root, name))
            if name == "time_dim.csv":
                time = pd.read_csv(os.path.join(root, name))
            elif name == "fact_table.csv":
                fact = pd.read_csv(os.path.join(root, name))
            elif name == "Trans_dim.csv":
                trans = pd.read_csv(os.path.join(root, name))
            elif name == "item_dim.csv":
                item = pd.read_csv(os.path.join(root, name), encoding="latin")
            elif name == "store_dim.csv":
                store = pd.read_csv(os.path.join(root, name))
            elif name == "customer_dim.csv":
                customer = pd.read_csv(os.path.join(root, name), encoding="latin")

    return time, fact, trans, item, store, customer