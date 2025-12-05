from datetime import datetime
import re

def _to_float(v):
    try:
        return float(v)
    except Exception:
        return None


def validate_packet_data(extracted_data_list):
    flags = []

    def find_data(t):
        for item in extracted_data_list:
            if item.get('type') == t:
                return item.get('data')
        return None

    invoice = find_data('Invoice')
    claim = find_data('ClaimForm')
    report = find_data('InspectionReport')

    if not claim:
        flags.append('CRITICAL: Missing Claim Form.')
    if not invoice:
        flags.append('CRITICAL: Missing Invoice.')

    if invoice and report:
        inv_total = _to_float(invoice.get('invoice_total'))
        assessed = _to_float(report.get('assessed_damage_value'))
        if inv_total and assessed and inv_total > assessed * 1.15:
            diff = inv_total - assessed
            flags.append(f'Amount Discrepancy: Invoice total ${inv_total:.2f} exceeds assessed value ${assessed:.2f} by ${diff:.2f}.')

    if claim:
        pol = claim.get('policy_number', '')
        if pol and not re.search(r'POL[-\\s]?\\d{4,8}', pol, flags=re.IGNORECASE):
            flags.append('Suspicious policy number format.')

    status = 'Approved' if len(flags) == 0 else 'Needs Manual Review'
    return status, flags
