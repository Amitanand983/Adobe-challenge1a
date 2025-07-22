import numpy as np
import re

def extract_features(blocks):
    # Compute median font size per page
    page_fonts = {}
    for b in blocks:
        page_fonts.setdefault(b['page'], []).append(b['font_size'])
    page_medians = {p: np.median(sizes) if sizes else 1 for p, sizes in page_fonts.items()}
    for block in blocks:
        median_font = page_medians.get(block['page'], 1)
        text = block['text']
        x = block['x']
        width = block['width']
        y = block['y'] if 'y' in block else 0
        # Centered: block center within 20% of page width (assume 600px page width)
        is_centered = abs((x + width/2) - 300) < 120
        # Indentation: 0 = left, 1 = moderate, 2 = deep
        if x < 60:
            indent = 0
        elif x < 120:
            indent = 1
        else:
            indent = 2
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        word_count = len(text.split())
        numbering = bool(re.match(r'^(\d+\.)+(\d+)?', text.strip()))
        page_position = y / 800  # assume 800px page height
        block['features'] = {
            'font_size_ratio': block['font_size'] / median_font if median_font else 1,
            'is_bold': block['is_bold'],
            'is_italic': block['is_italic'],
            'is_centered': is_centered,
            'indent': indent,
            'caps_ratio': caps_ratio,
            'word_count': word_count,
            'numbering': numbering,
            'page_position': page_position,
            'font_size': block['font_size'],
            'y': y
        }
    return blocks
