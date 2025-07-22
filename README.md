# PDF Structure Extraction Challenge (Adobe 1A)

## Overview
This project extracts structured information (title and hierarchical outline) from PDF files, following Adobe's challenge requirements. The output is a JSON file per PDF, matching a strict schema, and is robust to a variety of document layouts.

## Approach
- **Text Extraction:** Uses PyMuPDF to extract text blocks, font size, position, and other metadata from each PDF page.
- **Feature Engineering:** For each block, computes features such as font size ratio, boldness, centeredness, indentation, caps ratio, word count, and more.
- **Title Extraction:** Selects the topmost, largest, centered, content-rich block(s) as the document title, avoiding form fields and separators. For short, adjacent blocks at the very top, merges them if together they form a content-rich title.
- **Outline Extraction:**
  - Assigns heading levels (H1, H2, H3, H4) using font size, indentation, numbering, and content patterns.
  - Avoids including form fields, separators, or content blocks as headings.
  - Ensures all section headings are included, with correct page numbers (0-based).
- **Output:** Writes a JSON file per PDF in the `output/` directory, matching the provided schema.

## Output Schema
Each output JSON matches the following schema:
```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Section Title", "page": 0},
    {"level": "H2", "text": "Subsection", "page": 1},
    {"level": "H3", "text": "Sub-subsection", "page": 2}
  ]
}
```
- `title`: The main document title (string).
- `outline`: List of headings, each with a level (H1/H2/H3/H4), text, and 0-based page number.

## Heading Level Logic
- **H1:** Largest, centered, all-caps, or matches common heading patterns (e.g., "SUMMARY", "OVERVIEW").
- **H2:** Numbered headings (e.g., "2.1"), indented, bold, or slightly smaller font.
- **H3:** All-caps, ends with a colon, or deeply indented.
- **H4:** Long subheadings or content blocks with more than 12 words.
- **General:** If the outline is sparse, thresholds are relaxed to include more candidates.

## Folder Structure
```
Challenge_1a/
├── input/           # Place your input PDF files here
├── output/          # Extracted JSON outputs will be saved here
├── schema/          # Contains output_schema.json for validation
├── sample_output/   # Reference/sample outputs for comparison
├── src/             # Source code
│   ├── main.py
│   ├── extract_text.py
│   ├── feature_engineering.py
│   ├── rule_engine.py
│   ├── utils.py
├── requirements.txt # Python dependencies
├── Dockerfile       # For containerized execution
├── .gitignore
├── README.md        # This file
```

## How to Run Locally
1. **Install Python 3.10+ and pip.**
2. **Create a virtual environment (recommended):**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Place your PDF files in the `input/` directory.**
5. **Run the extraction:**
   ```sh
   python src/main.py
   ```
6. **Check the `output/` directory for the resulting JSON files.**

## How to Run with Docker
1. **Build the Docker image:**
   ```sh
   docker build -t pdf-structure-extractor .
   ```
2. **Run the container:**
   ```sh
   docker run --rm \
     -v $(pwd)/input:/app/input:ro \
     -v $(pwd)/output:/app/output \
     -v $(pwd)/schema:/app/schema:ro \
     pdf-structure-extractor
   ```
   - This will process all PDFs in `input/` and write JSONs to `output/`.

## Troubleshooting
- **No output or empty outline?**
  - Check that your PDFs are text-based (not scanned images).
  - Try lowering font size thresholds in `rule_engine.py` for more permissive heading extraction.
- **Docker build fails?**
  - Ensure you have Docker installed and enough disk space.
- **Output JSON does not match schema?**
  - Validate against `schema/output_schema.json` using a JSON schema validator.
- **Performance issues?**
  - For large PDFs, ensure you have enough memory and CPU. The code is optimized for speed and memory, but very large files may require more resources.

## Contribution Guidelines
- Fork the repository and create a new branch for your feature or bugfix.
- Write clear commit messages and document your changes.
- Ensure all tests pass and outputs match the schema.
- Open a pull request with a description of your changes.

## Notes
- **Page numbers in output are 0-based** (first page is 0).
- **No internet access is required or used** during runtime.
- **No OCR is performed**; only text-based PDFs are supported.
- **The code is robust and generalizes to new PDFs** (not hardcoded for any sample).
- **All dependencies are open source** and listed in `requirements.txt`.

## Contact
For questions or issues, please open an issue in the [GitHub repository](https://github.com/Amitanand983/Adobe-challenge1a). 