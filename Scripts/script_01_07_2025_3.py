from serpapi import GoogleSearch
import pandas as pd
import os
import re

# ✅ Define your custom patent stop words list
patent_stop_words = [
    "wherein", "thereof", "therein", "said", "claim", "claims",
    "the", "a", "an", "and", "or", "of", "to", "in"
]

# ✅ Text cleaning function
def clean_text(text, stop_words):
    if not text or not isinstance(text, str):
        return "N/A"
    
    # Lowercase
    text = text.lower()
    # Remove line breaks, tabs, extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove stop words
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    # Rejoin
    cleaned = ' '.join(tokens).strip()
    return cleaned

def fetch_patent_details(patent_id, serpapi_api_key):
    params = {
        "engine": "google_patents_details",
        "patent_id": f"patent/{patent_id}",
        "api_key": serpapi_api_key
    }
    search = GoogleSearch(params)
    result = search.get_dict()
    if "error" in result:
        print(f"Error fetching {patent_id}: {result['error']}")
        return None

    # ✅ Collect both numbers if available
    patent_data = {
        "Patent Number": result.get("publication_number", "N/A"),
        "Application Number": result.get("application_number", "N/A"),
        "Title": result.get("title", "N/A"),
        "Abstract": result.get("abstract", "N/A"),
        "Publication Date": result.get("publication_date", "N/A"),
        "Inventors": ", ".join([inv.get("name", "") for inv in result.get("inventors", [])]) or "N/A",
        "PDF Link": result.get("pdf", "N/A")
    }

    # ✅ Add Summary
    summary_text = result.get("SUMMARY")
    if not summary_text:
        summary_text = result.get("description", "N/A")
    patent_data["Summary"] = summary_text

    # ✅ Process claims
    claims = result.get("claims", [])
    claims_text = []
    if isinstance(claims, list):
        for idx, claim in enumerate(claims, start=1):
            if isinstance(claim, dict):
                claims_text.append(f"Claim {idx}: {claim.get('text', 'N/A')}")
            else:
                claims_text.append(f"Claim {idx}: {claim}")
    elif isinstance(claims, str):
        claims_text.append(f"Claim 1: {claims}")
    else:
        claims_text.append("N/A")
    patent_data["Claims"] = "\n".join(claims_text)

    # ✅ Process CPC Classifications
    classifications = result.get("classification", {}).get("cpc", [])
    cpc_text = []
    if classifications:
        for cpc in classifications:
            cpc_text.append(f"{cpc.get('code', 'N/A')}: {cpc.get('description', 'N/A')}")
    else:
        cpc_text.append("N/A")
    patent_data["CPC Classifications"] = "\n".join(cpc_text)

    # ✅ Clean key text fields and add as new columns
    patent_data["Cleaned Abstract"] = clean_text(patent_data["Abstract"], patent_stop_words)
    patent_data["Cleaned Summary"] = clean_text(patent_data["Summary"], patent_stop_words)
    patent_data["Cleaned Claims"] = clean_text(patent_data["Claims"], patent_stop_words)

    return patent_data

if __name__ == "__main__":
    serpapi_api_key = "70ab3069b92c8d3e48c553465a777e6b447eee57e50ac7bdc4a436af06f04f41"  # Replace with your valid API key

    # ✅ Accept multiple patent or application numbers
    patent_ids_input = input("Enter patent numbers OR application numbers separated by commas (e.g., US8460931B2, US20210012345A1): ").strip()
    patent_ids = [num.strip() for num in patent_ids_input.split(",") if num.strip()]

    all_patent_data = []
    for patent_id in patent_ids:
        print(f"Fetching {patent_id} ...")
        patent_info = fetch_patent_details(patent_id, serpapi_api_key)
        if patent_info:
            all_patent_data.append(patent_info)

    if all_patent_data:
        new_df = pd.DataFrame(all_patent_data)

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "patents_details.xlsx")

        if os.path.exists(output_file):
            print(f"\nAppending to existing file: {output_file}")
            existing_df = pd.read_excel(output_file, engine="openpyxl")
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            print(f"\nCreating new file: {output_file}")
            combined_df = new_df

        # ✅ Optional: Remove duplicates by Patent Number & Application Number
        combined_df.drop_duplicates(
            subset=["Patent Number", "Application Number"],
            keep="last",
            inplace=True
        )

        combined_df.to_excel(output_file, index=False, engine="openpyxl")

        print(f"\n✅ Patent details saved to: {output_file}")
    else:
        print("\n⚠️ No valid data fetched. Nothing saved.")
