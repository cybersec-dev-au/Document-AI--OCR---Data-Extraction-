import re
import json

class DataExtractor:
    def __init__(self):
        # Common regexes for document fields
        self.date_patterns = [
            r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}',  # 12/12/2023 or 12-12-23
            r'\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}',  # 2023-12-12
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}', # Dec 12, 2023
        ]
        
        # Keywords for amounts
        self.total_keywords = ['total', 'amount', 'balance', 'due', 'grand total', 'net amount', 'total check']
        self.amount_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'

    def extract_all(self, text_lines):
        """
        Takes a list of strings (each a line from OCR) and returns 
        structured data.
        """
        full_text = " ".join(text_lines).lower()
        
        return {
            "date": self._extract_date(full_text),
            "total_amount": self._extract_total(text_lines),
            "vendor": self._extract_vendor(text_lines[:5]), # Usually in first few lines
            "items": self._extract_line_items(text_lines),
            "raw_text": "\n".join(text_lines)
        }

    def _extract_date(self, text):
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "Not found"

    def _extract_total(self, lines):
        # Look for keywords and numbers near them
        found_amounts = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in self.total_keywords):
                # Look for a number in this line or the next few
                # Search up to 2 lines below if current line has no number
                for j in range(i, min(i+3, len(lines))):
                    matches = re.findall(self.amount_pattern, lines[j])
                    if matches:
                        # Pick the last amount (might be total)
                        found_amounts.append(float(matches[-1].replace(',', '')))
                        break
        
        if found_amounts:
            # Usually the largest amount when multiple 'total' lines exist
            return max(found_amounts)
        
        # Fallback: largest number in the text
        all_amounts = []
        for line in lines:
            matches = re.findall(self.amount_pattern, line)
            for m in matches:
                try:
                    all_amounts.append(float(m.replace(',', '')))
                except:
                    continue
        if all_amounts:
            return max(all_amounts)
            
        return "Not found"

    def _extract_vendor(self, top_lines):
        # Simplification: Assume vendor is in the first few lines 
        if top_lines:
            # Avoid picking dates/numbers/very short strings as vendor
            for line in top_lines:
                if len(line.strip()) > 3 and not re.search(r'\d{3,}', line):
                    return line.strip()
        return "Not found"

    def _extract_line_items(self, lines):
        # Placeholder for more complex line item extraction
        # For now, just a list of lines that look like items
        items = []
        # Basic heuristic: text with a number nearby
        for line in lines:
            if re.search(r'\d{1,}\.\d{2}', line) and len(line) > 10:
                items.append(line.strip())
        return items[:5] # Limit for UI
