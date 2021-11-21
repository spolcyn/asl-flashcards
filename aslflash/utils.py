import pandas as pd

def validate_timing_csv(csv_path: str):
    df = pd.read_csv(csv_path)

    return all([
        "word" in df.columns, # type: ignore
        "start_time" in df.columns, # type: ignore
    ])
