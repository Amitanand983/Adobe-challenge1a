import fitz  # PyMuPDF
import re


def is_form_field(text):
    if re.match(r"^\d+\. ", text):
        return True
    if re.match(r"^[0-9A-Za-z .]+: *$", text):
        return True
    if len(text.split()) <= 2 and any(c.isdigit() for c in text):
        return True
    if text.count('.') > 3 or text.count(' ') > 10:
        return True
    return False


def is_separator(text):
    return bool(re.match(r"^[-_]{3,}$", text.strip()))


def is_title_candidate(text):
    # Not a form field, not a separator, not starting with number/parenthesis
    if is_form_field(text) or is_separator(text):
        return False
    if re.match(r"^[\d\(]+", text.strip()):
        return False
    return True


def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")['blocks']
        for block in blocks:
            if block['type'] != 0:
                continue  # Only text blocks
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text']
                    if not text or text.isspace():
                        continue
                    bbox = span['bbox']
                    x0, y0, x1, y1 = bbox
                    height = y1 - y0
                    font_size = span.get('size', 0)
                    font = span.get('font', '')
                    is_bold = 'Bold' in font or 'bold' in font
                    is_italic = 'Italic' in font or 'Oblique' in font or 'italic' in font
                    text_blocks.append({
                        'text': text,
                        'page': page_num,
                        'bbox': bbox,
                        'font_size': font_size,
                        'font': font,
                        'is_bold': is_bold,
                        'is_italic': is_italic,
                        'x': x0,
                        'y': y0,
                        'width': x1 - x0,
                        'height': height
                    })
    return text_blocks


def is_potential_heading(text):
    text = text.strip()
    if not text:
        return False
    if text.startswith(("•", "-", "*")):
        return False
    if any(char.isdigit() for char in text[:3]) and '.' in text:
        return False
    if len(text) <= 3:
        return False
    if len(text.split()) < 3 and not text.isupper():
        return False
    return True


def extract_title_and_indices(blocks):
    first_page_blocks = [ (i, b) for i, b in enumerate(blocks) if b['page'] == 0 ]
    if not first_page_blocks:
        return '', set()
    font_sizes = [b['font_size'] for _, b in first_page_blocks]
    median_font = sorted(font_sizes)[len(font_sizes)//2] if font_sizes else 1
    candidates = [
        (i, b) for i, b in first_page_blocks
        if b['font_size'] >= 1.0 * median_font and abs((b['x'] + b['width']/2) - 300) < 220 and b['y'] < 0.45 * 800 and len(b['text']) <= 90 and is_title_candidate(b['text'])
    ]
    if not candidates:
        return '', set()
    candidates.sort(key=lambda x: x[1]['y'])
    # Try to merge short, adjacent blocks at the very top if together they form a content-rich title
    top_blocks = []
    base_font_size = candidates[0][1]['font_size']
    total_len = 0
    for i, (idx, b) in enumerate(candidates):
        if b['y'] > 0.15 * 800:
            break
        if i == 0 or (abs(b['font_size'] - base_font_size) / base_font_size < 0.15 and (b['y'] - candidates[i-1][1]['y'] < 80)):
            top_blocks.append((idx, b))
            total_len += len(b['text'])
        else:
            break
    if top_blocks and total_len > 30:
        title = '  '.join(b['text'] for idx, b in top_blocks)
        indices = set(idx for idx, b in top_blocks)
        return title, indices
    # Otherwise, use the single best block (topmost, largest, centered, content-rich)
    best = max(candidates, key=lambda x: (x[1]['font_size'], -x[1]['y'], len(x[1]['text'])))
    return best[1]['text'], {best[0]}


def apply_weighted_rules(block):
    if not is_potential_heading(block['text']):
        return 0.0, 'body'

    # Simplified rules for Phase 1
    if block['font_size'] > 20:
        return 0.9, 'H1'
    elif block['font_size'] > 15:
        return 0.8, 'H2'
    elif block['font_size'] > 10:
        return 0.7, 'H3'
    else:
        return 0.0, 'body'
