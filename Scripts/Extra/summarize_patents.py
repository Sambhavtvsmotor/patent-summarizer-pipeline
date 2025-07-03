import pandas as pd
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import os
import nltk

nltk.download('punkt')


# === CONFIG ===
INPUT_FILE = "output/patents_details.xlsx"
OUTPUT_FILE = "output/patents_details_with_offline_summary.xlsx"

# === Summarize function using sumy ===
def generate_offline_summary(text, num_sentences=3):
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return "N/A"
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, num_sentences)
    summarized_text = " ".join(str(sentence) for sentence in summary)
    return summarized_text if summarized_text else "N/A"

# === Load your cleaned data ===
df = pd.read_excel(INPUT_FILE, engine="openpyxl")
print(f"Loaded {len(df)} rows from {INPUT_FILE}")

# === Generate summaries for each patent ===
# You can choose any cleaned field here: Cleaned Claims, Cleaned Abstract, Cleaned Summary
df["Offline Generated Summary"] = df["Cleaned Claims"].apply(
    lambda x: generate_offline_summary(x, num_sentences=3)
)

print("✅ Offline summaries generated!")

# === Save to a new file ===
os.makedirs("output", exist_ok=True)
df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
print(f"✅ Saved with summaries: {OUTPUT_FILE}")
