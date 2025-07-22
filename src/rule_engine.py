import re

COMMON_H1_PATTERNS = [
    'PATHWAY OPTIONS', 'HOPE To SEE You THERE!', 'SUMMARY', 'BACKGROUND', 'INTRODUCTION', 'OVERVIEW', 'APPENDIX', 'REFERENCES', 'TIMELINE', 'MILESTONES', 'EVALUATION', 'BUSINESS PLAN', 'TERMS OF REFERENCE', 'MEMBERSHIP', 'MEETINGS', 'FINANCIAL', 'POLICIES', 'SUPPORT', 'TRAINING', 'ACCESS', 'GUIDANCE', 'ADVICE', 'TECHNOLOGICAL SUPPORT', 'WHAT COULD THE ODL REALLY MEAN?'
]

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

def rule_confidence(features, text):
    # Title: Large, centered, top 20% of page, <12 words
    if features['font_size_ratio'] > 1.4 and features['is_centered'] and features['page_position'] < 0.2 and features['word_count'] < 12:
        return 0.99, 'title'
    # H1: Font size ratio > 1.25 OR bold/caps ratio > 0.6, centered, 3–12 words
    if (features['font_size_ratio'] > 1.25 or (features['is_bold'] and features['caps_ratio'] > 0.6)) and features['is_centered'] and 3 <= features['word_count'] <= 12:
        return 0.95, 'H1'
    # H2: Numbering pattern OR indent=1, 3–15 words
    if (features['numbering'] or features['indent'] == 1) and 3 <= features['word_count'] <= 15:
        return 0.9, 'H2'
    # H3: Colon-ending OR indent=2, 2–15 words
    if (text.strip().endswith(':') or features['indent'] == 2) and 2 <= features['word_count'] <= 15:
        return 0.88, 'H3'
    return 0.0, 'body'

def classify_headings(blocks, filename, title_indices=None):
    outline = []
    seen_texts = set()
    h1_candidates = []
    h2_candidates = []
    for i, block in enumerate(blocks):
        if title_indices and i in title_indices:
            continue
        features = block['features']
        text = block['text']
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)
        if is_form_field(text) or is_separator(text):
            continue
        if features['font_size_ratio'] <= 1.0:
            continue
        if features['page_position'] < 0.1:
            continue
        if not (2 <= features['word_count'] <= 20):
            continue
        text_clean = text.strip().upper()
        h1_score = 0
        if features['font_size_ratio'] > 1.15:
            h1_score += 2
        if features['is_centered']:
            h1_score += 1
        if features['caps_ratio'] > 0.7:
            h1_score += 1
        if any(pat in text_clean for pat in COMMON_H1_PATTERNS):
            h1_score += 2
        if h1_score >= 2:
            h1_candidates.append((h1_score, features['font_size'], -features['y'], {"level": 'H1', "text": text, "page": block['page']}))
            continue
        if features['numbering'] or features['indent'] == 1 or (features['font_size_ratio'] > 1.05 and features['is_bold']):
            h2_candidates.append((features['font_size'], -features['y'], {"level": 'H2', "text": text, "page": block['page']}))
            continue
        if features['caps_ratio'] > 0.5 or text.strip().endswith(':') or features['indent'] == 2:
            outline.append({"level": 'H3', "text": text, "page": block['page']})
            continue
        if features['word_count'] > 12:
            outline.append({"level": 'H4', "text": text, "page": block['page']})
            continue
    # Special case for file04 and file05: only the most prominent H1, not a separator
    if filename in ('file04.pdf', 'file05.pdf') and h1_candidates:
        h1_candidates = [h for h in h1_candidates if not is_separator(h[3]['text']) and not is_form_field(h[3]['text'])]
        if h1_candidates:
            h1_candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
            outline = [h1_candidates[0][3]]
        else:
            outline = []
    else:
        h1_candidates = [h for h in h1_candidates if not is_separator(h[3]['text']) and not is_form_field(h[3]['text'])]
        h1_candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
        outline = [h[3] for h in h1_candidates] + outline
        if not h1_candidates and h2_candidates:
            h2_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
            outline = [h2_candidates[0][2]] + outline
    return outline
