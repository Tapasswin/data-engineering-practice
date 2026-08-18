import json
from pathlib import Path
import pandas as pd

def main():
    folder_path = Path("data")
    if not folder_path.exists():
        raise FileNotFoundError("Missing 'data' directory. Make sure the JSON files are present in the project before running the container.")

    json_file = list(folder_path.rglob("*.json"))
    for f in json_file:
        with open(f, 'r') as file:
            # load JSON
            data = json.load(file)
        # Flatten JSON 
        df = pd.json_normalize(data)
        csv_name = f.stem + ".csv"
        # Save to CSV
        output_path = f.with_suffix(".csv")
        df.to_csv(f"{output_path}", index=False)
        print(f"Saved in {output_path} ({len(df)} rows)")
        df_csv = pd.read_csv(f"{output_path}")
        print(df_csv.head())

if __name__ == "__main__":
    main()
