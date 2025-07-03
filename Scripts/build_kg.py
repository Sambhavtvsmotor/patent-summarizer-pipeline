import pandas as pd
import networkx as nx
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# === CONFIG ===
INPUT_FILE = "output/patents_details_with_keyphrases.xlsx"
OUTPUT_GRAPH = "output/patent_kg.graphml"

# === Load data ===
df = pd.read_excel(INPUT_FILE, engine="openpyxl")
print(f"✅ Loaded {len(df)} rows from {INPUT_FILE}")

# === Build KG ===
G = nx.MultiDiGraph()  # Directed multi-edge graph

for idx, row in df.iterrows():
    patent_id = row.get("Publication Number", f"Patent_{idx+1}")
    title = str(row.get("Title", "")).strip()

    # Robust handling for NaN
    inventors = str(row.get("Inventors", "") or "").split(", ")
    cpc_raw = row.get("CPC Classifications", "")
    cpc_codes = str(cpc_raw if not pd.isna(cpc_raw) else "").split("\n")

    phrases_raw = row.get("Key Phrases", "")
    key_phrases = str(phrases_raw if not pd.isna(phrases_raw) else "").split("; ")

    # Add Patent node
    G.add_node(
        patent_id,
        label="Patent",
        title=title
    )

    # Add Inventors
    for inv in inventors:
        if inv.strip():
            G.add_node(inv.strip(), label="Inventor")
            G.add_edge(patent_id, inv.strip(), relation="INVENTED_BY")

    # Add CPC codes
    for cpc in cpc_codes:
        if cpc.strip() and ":" in cpc:
            code, desc = cpc.split(":", 1)
            G.add_node(code.strip(), label="CPC", description=desc.strip())
            G.add_edge(patent_id, code.strip(), relation="CLASSIFIED_AS")

    # Add Key Phrases
    for phrase in key_phrases:
        if phrase.strip() and phrase != "N/A":
            G.add_node(phrase.strip(), label="KeyPhrase")
            G.add_edge(patent_id, phrase.strip(), relation="MENTIONS")

print(f"✅ Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

# === Pick a layout ===
pos = nx.spring_layout(G, k=0.15, iterations=20)

# === Make colors by node type ===
colors = []
for node in G.nodes(data=True):
    label = node[1].get("label", "")
    if label == "Patent":
        colors.append("skyblue")
    elif label == "Inventor":
        colors.append("lightgreen")
    elif label == "CPC":
        colors.append("lightcoral")
    elif label == "KeyPhrase":
        colors.append("gold")
    else:
        colors.append("gray")

plt.figure(figsize=(18, 12))
nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=100, alpha=0.8)
nx.draw_networkx_edges(G, pos, alpha=0.2)
nx.draw_networkx_labels(G, pos, font_size=8)

plt.axis("off")

# === Add legend ===
legend_elements = [
    mpatches.Patch(color="skyblue", label="Patent"),
    mpatches.Patch(color="lightgreen", label="Inventor"),
    mpatches.Patch(color="lightcoral", label="CPC Classification"),
    mpatches.Patch(color="gold", label="Key Phrase")
]

plt.legend(
    handles=legend_elements,
    loc="lower left",
    title="Node Types",
    fontsize="large",
    title_fontsize="x-large",
    frameon=True
)

plt.tight_layout()
os.makedirs("output", exist_ok=True)
plt.savefig("output/patent_kg_snapshot.png", dpi=300)
plt.close()

print(f"✅ Static PNG snapshot with legend saved: output/patent_kg_snapshot.png")

# === Save the GraphML ===
nx.write_graphml(G, OUTPUT_GRAPH)
print(f"✅ Knowledge Graph exported to: {OUTPUT_GRAPH}")
