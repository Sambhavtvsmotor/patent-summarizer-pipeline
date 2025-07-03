import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from serpapi import GoogleSearch
import networkx as nx
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import re
import math

# 🔐 Set your SerpAPI Key here
SERPAPI_API_KEY = "YOUR_SERPAPI_KEY"  # Replace with your actual key!

print("📦 Loading BERT-based REBEL model...")
tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large").to(
    "cuda" if torch.cuda.is_available() else "cpu"
)


def fetch_patent_text_serpapi(patent_number):
    print(f"🔎 Fetching {patent_number} using SerpAPI...")
    params = {
        "engine": "google_patents",
        "q": patent_number,
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    patent_data = results.get("inline_patent")
    if patent_data:
        return f"{patent_data.get('abstract', '')}\n{patent_data.get('description', '')}\n{patent_data.get('claims', '')}".strip()

    # Fallback to scrape Google Patents
    print("⚠️ Falling back to scraping Google Patents page...")
    url = f"https://patents.google.com/patent/{patent_number}/en"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(html.text, "html.parser")

    abstract = soup.find("meta", {"name": "DC.description"})
    desc = soup.find("div", {"itemprop": "description"})
    claims = soup.find("section", {"itemprop": "claims"})

    abstract_text = abstract["content"] if abstract else ""
    desc_text = desc.get_text(separator=" ", strip=True) if desc else ""
    claims_text = claims.get_text(separator=" ", strip=True) if claims else ""

    return f"{abstract_text}\n{desc_text}\n{claims_text}".strip() or None


def extract_rebel_triples(text, chunk_size=512):
    """
    Split text into chunks, run REBEL on each,
    and extract triples using regex + smart fallback.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    triples = []

    tokens = tokenizer(text)["input_ids"]
    total_tokens = len(tokens)
    num_chunks = math.ceil(total_tokens / chunk_size)

    print(f"🔢 Total tokens: {total_tokens} | Chunk size: {chunk_size} | Chunks: {num_chunks}")

    for i in range(0, total_tokens, chunk_size):
        chunk_tokens = tokens[i:i+chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)

        inputs = tokenizer(
            chunk_text,
            return_tensors="pt",
            truncation=True,
            max_length=chunk_size
        ).to(device)

        with torch.no_grad():
            generated_tokens = model.generate(
                **inputs,
                max_length=chunk_size,
                num_beams=8,
                early_stopping=True
            )

        output_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        print(f"=== REBEL Output for chunk ===\n{output_text}\n")

        # Try regex pattern first
        pattern = r"<subject>(.*?)<relation>(.*?)<object>(.*?)\."
        matches = re.findall(pattern, output_text, re.DOTALL)

        if matches:
            for s, r, o in matches:
                triples.append((s.strip(), r.strip(), o.strip()))
        else:
            # Smart fallback: find groups of 3 words
            words = output_text.strip().split()
            if len(words) >= 3:
                num_triples = len(words) // 3
                for i in range(num_triples):
                    triple = words[i*3:(i+1)*3]
                    if len(triple) == 3:
                        triples.append(tuple(w.strip() for w in triple))
                        print(f"⚙️ Added fallback triple: {triples[-1]}")

    return triples


def build_graph(triples, patent_number):
    G = nx.DiGraph()
    for subj, rel, obj in triples:
        G.add_edge(subj, obj, label=rel)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2500, font_size=10)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='darkred')
    plt.title(f"📘 Knowledge Graph: {patent_number}")
    plt.axis('off')

    filename = f"knowledge_graph_{patent_number}.png"
    plt.savefig(filename, format="png", bbox_inches='tight')
    print(f"✅ Graph saved as: {filename}")
    plt.show()


if __name__ == "__main__":
    patent_number = input("📄 Enter Patent/Application Number (e.g., CN116113573A): ").strip()
    text = fetch_patent_text_serpapi(patent_number)

    if not text:
        print("❌ No text found for this patent.")
    else:
        print("=== Input Text Preview ===")
        print(text[:1000], "\n... [truncated] ...")

        print("🧠 Extracting BERT-based relations...")
        triples = extract_rebel_triples(text)

        print(f"📈 Extracted {len(triples)} triples.")
        if triples:
            for t in triples:
                print(" -", t)
            build_graph(triples, patent_number)
        else:
            print("⚠️ No triples extracted. Try a different patent or check your input text.")
