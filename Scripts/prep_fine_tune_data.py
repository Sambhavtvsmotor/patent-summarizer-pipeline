# prep_finetune_data.py

import pandas as pd
from datasets import Dataset

# === CONFIG ===
INPUT_FILE = "output/patents_details_with_keyphrases.xlsx"
OUTPUT_DIR = "./finetune_data/"

df = pd.read_excel(INPUT_FILE, engine="openpyxl")

# Fill NaNs and clean
df["Cleaned Claims"] = df["Cleaned Claims"].fillna("")
df["Abstract"] = df["Abstract"].fillna("")

# Filter out rows with very short text
df = df[df["Cleaned Claims"].str.len() > 50]
df = df[df["Abstract"].str.len() > 20]

# Build dict
data = {
    "text": df["Cleaned Claims"].tolist(),
    "summary": df["Abstract"].tolist()
}

dataset = Dataset.from_dict(data).train_test_split(test_size=0.1)

dataset["train"].to_json(f"{OUTPUT_DIR}/train.json", orient="records", lines=True)
dataset["test"].to_json(f"{OUTPUT_DIR}/test.json", orient="records", lines=True)

print(f"✅ Saved training & test data in: {OUTPUT_DIR}")
