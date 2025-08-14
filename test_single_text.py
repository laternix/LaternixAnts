#!/usr/bin/env python3
"""
Test why specific text is being filtered
"""

import re

text = "Erneuerung der Bürobeleuchtung auf LED"
text_lower = text.lower()

# Test with "beleuchtung"
keyword = "beleuchtung"
pattern = r'\b' + re.escape(keyword) + r'\b'

print(f"Text: {text}")
print(f"Text lower: {text_lower}")
print(f"Keyword: {keyword}")
print(f"Pattern: {pattern}")

match = re.search(pattern, text_lower, re.IGNORECASE)
print(f"Match found: {match}")

# Try without word boundaries
if keyword in text_lower:
    print(f"Substring match: YES")
else:
    print(f"Substring match: NO")

# Check what's around "beleuchtung"
import unicodedata
for i, char in enumerate(text_lower):
    if i >= 15 and i <= 30:
        print(f"Char {i}: '{char}' - {unicodedata.name(char, 'UNKNOWN')}")