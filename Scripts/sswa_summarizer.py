import pandas as pd
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from transformers import BartTokenizer, BartForConditionalGeneration
import os

# === CONFIG ===
INPUT_FILE = "output/patents_details.xlsx"
OUTPUT_FILE = "output/patents_details_with_bart_summary.xlsx"

# === Load data ===
df = pd.read_excel(INPUT_FILE, engine="openpyxl")
print(f"Loaded {len(df)} rows from {INPUT_FILE}")

# === Load embedding model for SSWA ===
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# === Load local BART summarizer ===
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Load tokenizer for BART
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

# === SSWA ranking function ===
def sswa_rank_sentences(abstract, sentences, top_n=3):
    if not abstract or not sentences:
        return []

    emb_abstract = embedder.encode(abstract, convert_to_tensor=True)
    emb_sentences = embedder.encode(sentences, convert_to_tensor=True)

    similarities = util.cos_sim(emb_abstract, emb_sentences)[0]

    scored = list(zip(sentences, similarities.tolist()))
    scored.sort(key=lambda x: x[1], reverse=True)

    return [s[0] for s in scored[:top_n]]

# === Apply Dual Input ===
bart_summaries = []

for idx, row in df.iterrows():
    raw_abstract = row.get("Abstract", "")
    cleaned_claims = row.get("Cleaned Claims", "")

    claim_sentences = [s.strip() for s in cleaned_claims.split('.') if len(s.strip()) > 20]
    top_sentences = sswa_rank_sentences(raw_abstract, claim_sentences, top_n=3)

    dual_input = f"""
    ABSTRACT:
    {raw_abstract}

    KEY SENTENCES:
    {' '.join(top_sentences)}
    """

    tokens = tokenizer(dual_input, return_tensors='pt', truncation=True, max_length=1024)
    safe_input = tokenizer.decode(tokens['input_ids'][0], skip_special_tokens=True)

    if len(safe_input.split()) < 50:
        final_summary = "N/A"
    else:
        bart_output = summarizer(
            safe_input,
            max_length=100,
            min_length=30,
            do_sample=False
        )
        final_summary = bart_output[0]['summary_text']

    bart_summaries.append(final_summary)
    print(f"Row {idx+1}: {final_summary[:60]}...")


# Save new file
df["SSWA BART Summary"] = bart_summaries
os.makedirs("output", exist_ok=True)
df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
print(f"✅ Saved final file with SSWA + Dual Input BART summaries: {OUTPUT_FILE}")
