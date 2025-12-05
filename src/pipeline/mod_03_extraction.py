import re
from datetime import datetime

# ✅ Clean and safe regex patterns (compatible with Python 3.13+)
INVOICE_PATTERNS = {
    'invoice_id': [
        r'INV[-\s]?\d{3,6}',
        r'Invoice\s*#?:?\s*(\w+-?\d+)'
    ],
    'invoice_total': [
        r'Total\s*[:\s]?\$?\s*([0-9,]+(?:\.\d{1,2})?)',
        r'Amount\s*Due\s*[:\s]?\$?\s*([0-9,]+(?:\.\d{1,2})?)'
    ]
}

CLAIM_PATTERNS = {
    'policy_number': [
        r'POL[-\s]?\d{4,8}',
        r'Policy\s*No\.?\s*[:\s]?(?:\w+-?\d+)'
    ],
    # ✅ Fixed safe date pattern
    'date_of_loss': [
        r'(?:Date\s+of\s+(?:Loss|Accident))[:\s]*(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})'
    ]
}

INSPECTION_PATTERNS = {
    'vehicle_vin': [
        r'VIN[:\s]*([A-HJ-NPR-Za-hj-npr-z0-9\-]{11,17})'
    ],
    # ✅ Fixed and expanded damage patterns
    'assessed_damage_value': [
        r'Assessed\s+Damage\s*[:\s]?\$?\s*([0-9,]+(?:\.\d{1,2})?)',
        r'Damage\s+Estimate\s*[:\s]?\$?\s*([0-9,]+(?:\.\d{1,2})?)'
    ]
}


def _search_patterns(text, patterns):
    for patt in patterns:
        try:
            m = re.search(patt, text, flags=re.IGNORECASE)
            if m:
                return m.group(1) if m.groups() else m.group(0)
        except re.error as e:
            # If regex pattern fails, log and continue gracefully
            print(f"[WARN] Regex failed: {patt} — {e}")
    return None


def _parse_money(val):
    if not val:
        return None
    cleaned = re.sub(r'[^0-9.]', '', val)
    try:
        return float(cleaned) if cleaned else None
    except Exception:
        return None


def extract_key_values(doc_chunk_images, doc_type, doc_chunk_texts=None):
    """
    Deterministic key–value extractor for each document type.
    """
    text = ''
    if doc_chunk_texts:
        text = '\n'.join([t for t in doc_chunk_texts if t])

    if not text:
        return {'error': 'No text provided for extraction'}

    if doc_type == 'Invoice':
        invoice_id = _search_patterns(text, INVOICE_PATTERNS['invoice_id'])
        invoice_total_raw = _search_patterns(text, INVOICE_PATTERNS['invoice_total'])
        return {
            'invoice_id': invoice_id,
            'invoice_total': _parse_money(invoice_total_raw),
            'raw_total_str': invoice_total_raw
        }

    if doc_type == 'ClaimForm':
        policy = _search_patterns(text, CLAIM_PATTERNS['policy_number'])
        date_raw = _search_patterns(text, CLAIM_PATTERNS['date_of_loss'])
        date_parsed = None
        if date_raw:
            for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d'):
                try:
                    date_parsed = datetime.strptime(date_raw, fmt).date().isoformat()
                    break
                except Exception:
                    continue
        return {'policy_number': policy, 'date_of_loss': date_parsed or date_raw}

    if doc_type == 'InspectionReport':
        vin = _search_patterns(text, INSPECTION_PATTERNS['vehicle_vin'])
        assessed_raw = _search_patterns(text, INSPECTION_PATTERNS['assessed_damage_value'])
        return {
            'vehicle_vin': vin,
            'assessed_damage_value': _parse_money(assessed_raw),
            'raw_assessed_str': assessed_raw
        }

    return {'error': f'Unsupported doc_type: {doc_type}'}
