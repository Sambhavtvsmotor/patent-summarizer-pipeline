import os
import csv
import networkx as nx
import matplotlib.pyplot as plt
import re

def extract_entities_and_relationships(row):
    entities = []
    relationships = []

    patent_number = row.get('Patent Number', '').strip()
    inventor = row.get('Inventor', '').strip()
    assignee = row.get('Assignee', '').strip()
    claims = row.get('Claims', '').strip()
    abstract = row.get('Abstract', '').strip()

    if patent_number:
        entities.append(('Patent', patent_number))
    if inventor:
        entities.append(('Inventor', inventor))
    if assignee:
        entities.append(('Assignee', assignee))
    if claims:
        entities.append(('Claims', claims))
    if abstract:
        entities.append(('Abstract', abstract))

    if patent_number and inventor:
        relationships.append((inventor, patent_number, 'invented'))
    if patent_number and assignee:
        relationships.append((assignee, patent_number, 'assigned'))
    if patent_number and claims:
        relationships.append((patent_number, claims, 'has_claims'))
    if patent_number and abstract:
        relationships.append((patent_number, abstract, 'described_by'))

    return entities, relationships

def build_knowledge_graph(csv_file):
    G = nx.DiGraph()
    with open(csv_file, newline='', encoding='windows-1252') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entities, relationships = extract_entities_and_relationships(row)
            for entity_type, entity_value in entities:
                G.add_node(entity_value, label=entity_type)
            for source, target, relation in relationships:
                G.add_edge(source, target, label=relation)
    return G

def visualize_graph(G, output_image):
    pos = nx.spring_layout(G, k=0.5)
    plt.figure(figsize=(12, 8))

    node_labels = {node: f"{data['label']}: {node}" for node, data in G.nodes(data=True)}
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}

    nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=2000, node_color='lightblue', font_size=8, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=100)

    plt.title("Patent Knowledge Graph")
    plt.tight_layout()
    plt.savefig(output_image)
    plt.close()

# Example usage
csv_file = 'filtered_patents3.csv'  # Replace with your actual CSV file path
output_image = 'knowledge_graph2.png'
graph = build_knowledge_graph(csv_file)
visualize_graph(graph, output_image)

print(f"Knowledge graph saved as {output_image}")
