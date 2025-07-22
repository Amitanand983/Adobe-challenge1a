from pathlib import Path
from extract_text import extract_text_blocks, extract_title_and_indices
from feature_engineering import extract_features
from rule_engine import classify_headings
import json

## Docker paths 
# INPUT_DIR = Path("/app/input")    
# OUTPUT_DIR = Path("/app/output")  

# Input/output directories on your Mac (no Docker now)
INPUT_DIR = Path("/Users/amitanand/Desktop/challenge/Challenge_1a/input")
OUTPUT_DIR = Path("/Users/amitanand/Desktop/challenge/Challenge_1a/output")

def process_pdf(pdf_file):
    blocks = extract_text_blocks(pdf_file)
    blocks = extract_features(blocks)
    title, title_indices = extract_title_and_indices(blocks)
    outline = classify_headings(blocks, pdf_file.name, title_indices)
    result = {"title": title, "outline": outline}
    output_file = OUTPUT_DIR / f"{pdf_file.stem}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def main():
    pdf_files = INPUT_DIR.glob("*.pdf")
    for pdf_file in pdf_files:
        process_pdf(pdf_file)

if __name__ == "__main__":
    main()

