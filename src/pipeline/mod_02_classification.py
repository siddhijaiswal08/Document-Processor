import os
import numpy as np
import logging

try:
    import pytesseract
except Exception:
    pytesseract = None

LABEL_KEYWORDS = {
    'Invoice': ['invoice', 'total', 'amount due', 'vat', 'subtotal'],
    'ClaimForm': ['claim', 'policy', 'claimant', 'date of loss'],
    'InspectionReport': ['inspection', 'inspector', 'assessed', 'odometer', 'vehicle'],
    'Receipt': ['receipt', 'paid', 'change', 'method of payment']
}


def classify_document_chunk(doc_chunk_images, doc_chunk_texts=None):
    combined = ''
    if doc_chunk_texts:
        combined = ' '.join([t for t in doc_chunk_texts if t])
    if not combined and doc_chunk_images and pytesseract is not None:
        combined = '\n'.join([pytesseract.image_to_string(img) for img in doc_chunk_images])

    combined_low = combined.lower()
    scores = {k: 0 for k in LABEL_KEYWORDS.keys()}

    for label, keywords in LABEL_KEYWORDS.items():
        for kw in keywords:
            if kw in combined_low:
                scores[label] += 1

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]
    total_hits = sum(scores.values())

    if total_hits == 0:
        estimated_conf = 0.55
        best_label = 'InspectionReport' if len(doc_chunk_images) > 1 else 'ClaimForm'
    else:
        estimated_conf = min(0.98, 0.5 + (best_score / max(1, total_hits)))

    model_path = os.path.join('models', 'doc_classifier.pt')
    if os.path.exists(model_path):
        logging.info('Detected model at %s — plug inference here', model_path)
        # Plug in your trained model inference here

    return best_label, float(estimated_conf)
