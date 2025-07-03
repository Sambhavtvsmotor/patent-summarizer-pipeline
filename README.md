# 📄 Patent Extraction Pipeline — SSWA + Local BART Summarizer

## ✅ Project Overview

This pipeline processes patent data end-to-end:
1. Extracts relevant features from raw patent documents (Abstract, Claims, CPC Codes, etc.).
2. Cleans and pre-processes text with stopword removal.
3. Applies a **Semantic Similarity Weighted Algorithm (SSWA)** to rank the most relevant sentences.
4. Generates **dual input prompts** (Original Abstract + SSWA-ranked sentences).
5. Feeds the prompt to a **local BART Sequence-to-Sequence model** for fluent, abstractive summaries.
6. Saves the output in an Excel sheet for further use (e.g., building Knowledge Graphs).

---

## ✅ What We Added Today [2025-07-02]

**🎯 Key features implemented:**
- Integrated `sentence-transformers` for semantic similarity scoring.
- Built the `sswa_rank_sentences()` function using **MiniLM-L6-v2** embeddings.
- Designed a **Dual Input strategy** that combines:
  - The full **original Abstract** (for domain style & coherence).
  - The top N **key sentences** from Claims (for technical details).
- Integrated **offline local BART** (`facebook/bart-large-cnn`).
- Replaced fragile `pipeline()` usage with a robust `tokenizer` + `model.generate()` pattern.
- Solved `IndexError` issues by enforcing token truncation with `max_length=1024`.
- Final output: `output/patents_details_with_bart_summary.xlsx`  
  ➜ Includes a new `SSWA BART Summary` column.

---

## ✅ 📂 Folder Structure

Python Code/ 
├── myenv/ 
├── patent_documents/ 
├── Rough/
├── Scripts/
     	├── script.py
		├── built._kg.py
		├── finetune.py
		├── keybert.py
		├── sswa_pipeline.py
		├── requirements.txt
 		├── README.md
     	├── output/ 
				└── patents_details.xlsx 
				└── patents_details_with_offline_summary.xlsx


---

## ✅ 🔑 How It Works

**1️⃣** Loads `patents_details.xlsx` with your processed patent data.

**2️⃣** For each row:
   - Ranks Claims sentences by similarity to the Abstract.
   - Combines Abstract + top-ranked sentences into a dual-input chunk.

**3️⃣** Uses `BartTokenizer` + `BartForConditionalGeneration` to:
   - Truncate safely to the model’s limit (1024 tokens).
   - Generate a fluent summary using beam search.

**4️⃣** Appends the generated summary to a new column.

**5️⃣** Saves everything to a versioned Excel file for downstream tasks.

---




## ✅ How to run

1. Activate your virtual environment:
      	.\myenv\Scripts\activate   # Windows
   	source myenv/bin/activate  # Linux/Mac

2. Install dependencies:
	pip install -r requirements.txt

3. Run:
	python script.py

4. Your final file will be at:
		Scripts/output/patents_details_with_bart_summary.xlsx

Input one or more patent/application numbers separated by commas.

✅ Dependencies
serpapi for Google Patents search

pandas for data handling

openpyxl for Excel export

nltk or spacy for text cleaning


📌 Notes
Always close patents_details.xlsx before running the script.

Stop words are defined in patent_stop_words — update this as you refine your NLP pipeline.




# 📅 DAILY PROGRESS LOG — [2025-07-03]

---

## ✅ Overview

**Goal:** Refine the patent processing pipeline: extraction → cleaning → semantic ranking → summarization → knowledge graph.

---

## ✅ 1️⃣ Patent Data Pipeline

- ✔️ Extracted **Title**, **Publication/Application Number**, **Abstract**, **Claims**, **Summary**, **CPC Classifications**, **Inventors**, and **PDF link**.
- ✔️ Added **stopword removal** step for text cleaning.
- ✔️ Appended data to **Excel** (`patents_details.xlsx`) — does not overwrite existing data.

---

## ✅ 2️⃣ SSWA (Semantic Similarity With Attention)

- ✔️ Used **SentenceTransformer** (`all-MiniLM-L6-v2`) to rank claim sentences against the abstract.
- ✔️ Implemented **Top-N** selection for dual-phase summarization input.

---

## ✅ 3️⃣ BART Summarizer

- ✔️ Ran local **`facebook/bart-large-cnn`** summarizer:
  - Single input (claims only)
  - Dual input (abstract + top-ranked claims)
- ✔️ Handled truncation & input length.
- ✔️ Stored generated BART summaries back to Excel.

---

## ✅ 4️⃣ Knowledge Graph (KG)

- ✔️ Built KG in **NetworkX**:
  - Nodes: `Patent`, `Inventor`, `CPC`, `KeyPhrase`
  - Edges: `INVENTED_BY`, `CLASSIFIED_AS`, `MENTIONS`
- ✔️ Saved:
  - `patent_kg.graphml` for **Neo4j** or **Gephi**.
  - `patent_kg_snapshot.png` with clear node colors and labels.

---

## ✅ 5️⃣ Keyphrase Extraction

- ✔️ Tried **KeyBERT + KeyphraseVectorizers**
- ⚠️ Hit `blis` build error due to missing C++ build tools.
- ✔️ Verified **KeyBERT** works standalone with `SentenceTransformer`.

---

## ✅ 6️⃣ BART Fine-Tuning Attempt

- ✔️ Set up domain fine-tuning script.
- ⚠️ Encountered `TrainingArguments` version mismatch.
- Currently Working on this, trying to understand the issue

---

## 🟢 What’s Working Now

| Step | Status |
|------|--------|
| SerpAPI extraction | ✅ |
| Excel append | ✅ |
| Text cleaning | ✅ |
| SSWA sentence ranking | ✅ |
| Local BART summarization | ✅ |
| KG build & export | ✅ |
| KeyBERT (default embedder) | ✅ |

---

## 🔧 Next Steps

- Fix local build for `KeyphraseVectorizers` (install MSVC or test on Colab)
- Fine-tune **BART** on cleaned domain data (Colab recommended)
- Expand KG: load into **Neo4j** and test graph queries
- Try chunked input for longer abstracts/claims with BART
- Prepare final README updates for project push to GitHub

---

## 🗂️ Files Updated Today

- `Scripts/script.py`
- `Scripts/sswa_pipeline.py`
- `Scripts/build_kg.py`
- `output/patents_details.xlsx`
- `output/patent_kg.graphml`
- `output/patent_kg_snapshot.png`

---

## ⚡ Keep It Rolling!

> 🚀 We have a fully functional pipeline — only advanced NLP vectorizer and fine-tuning steps need environment tuning.  
> All base steps work end-to-end!

---

_✏️ Prepared by: [Team TIP] — [2025-07-03]_
