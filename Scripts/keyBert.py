import pandas as pd
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
import os

# === CONFIG ===
INPUT_FILE = "output/patents_details_with_bart_summary.xlsx"
OUTPUT_FILE = "output/patents_details_with_keyphrases.xlsx"

# === Load data ===
df = pd.read_excel(INPUT_FILE, engine="openpyxl")
print(f"✅ Loaded {len(df)} rows from {INPUT_FILE}")

# === Load KeyBERT model ===
kw_model = KeyBERT(model="all-MiniLM-L6-v2")
print("✅ KeyBERT model loaded!")

# === Load KeyphraseVectorizer ===
vectorizer = KeyphraseCountVectorizer(spacy_pipeline="en_core_web_sm")
print("✅ Using KeyphraseCountVectorizer for better phrase extraction.")

# === Extract key phrases ===
keyphrases_list = []

for idx, row in df.iterrows():
    cleaned_claims = row.get("Cleaned Claims", "")
    if not cleaned_claims or len(cleaned_claims.split()) < 5:
        keyphrases_list.append("N/A")
        continue

    # Extract top 5 phrases with MMR for diversity
    phrases = kw_model.extract_keywords(
        cleaned_claims,
        vectorizer=vectorizer,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        top_n=5,
        use_mmr=True,      # ✅ Adds diversity
        diversity=0.5      # Adjust to balance relevance vs uniqueness
    )

    # Join phrases nicely
    top_phrases = [kw for kw, score in phrases]
    keyphrases_str = "; ".join(top_phrases)

    keyphrases_list.append(keyphrases_str)
    print(f"Row {idx+1}: {keyphrases_str}")

# Add new column
df["Key Phrases"] = keyphrases_list

# Save to Excel
os.makedirs("output", exist_ok=True)
df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
print(f"\n✅ Saved file with key phrases: {OUTPUT_FILE}")
