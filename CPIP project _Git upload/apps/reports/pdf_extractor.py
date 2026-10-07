import pdfplumber
import re
import os
from django.conf import settings


def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"PDF file not found: {full_path}")

    extracted_text = ""
    with pdfplumber.open(full_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                extracted_text += f"\n--- Page {page_num} ---\n"
                extracted_text += page_text + "\n"
    return extracted_text


def extract_tables_from_pdf(pdf_path):
    """Extract tables from a PDF file."""
    full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"PDF file not found: {full_path}")

    tables = []
    with pdfplumber.open(full_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_tables = page.extract_tables()
            if page_tables:
                for table in page_tables:
                    tables.append({'page': page_num, 'data': table})
    return tables


def extract_metadata_from_pdf(pdf_path):
    """Extract metadata (page count, etc)."""
    full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"PDF file not found: {full_path}")

    with pdfplumber.open(full_path) as pdf:
        return {'pages': len(pdf.pages), 'metadata': pdf.metadata}


def extract_numbers_from_text(text):
    """Extract numbers from text."""
    pattern = r'\d+[\d,]*\.?\d*%?'
    matches = re.findall(pattern, text)
    cleaned = []
    for match in matches:
        cleaned_match = match.replace(',', '')
        if cleaned_match.endswith('%'):
            cleaned_match = cleaned_match[:-1]
        try:
            cleaned.append(float(cleaned_match))
        except ValueError:
            pass
    return cleaned


def extract_year_from_text(text):
    """Extract 4-digit years from text."""
    pattern = r'\b(19\d{2}|20\d{2})\b'
    matches = re.findall(pattern, text)
    return [int(year) for year in matches]