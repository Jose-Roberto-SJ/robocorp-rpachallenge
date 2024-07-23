import re

def contains_monetary_value(description: str) -> bool:

    monetary_patterns = [
        r'\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?',  # $11.1 or $111,111.11
        r'\b\d+ dollars\b',                     # 11 dollars
        r'\b\d+ USD\b'                          # 11 USD
    ]

    combined_pattern = '|'.join(monetary_patterns)

    match = re.search(combined_pattern, description, re.IGNORECASE)

    # True if monetary values found or False if not
    return match is not None