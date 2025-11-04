#!/usr/bin/env python3
"""
OCR-based validation of GitHub projects timeline against PDF screenshots
"""

import pdf2image
import pytesseract
from PIL import Image
import re
from collections import defaultdict
import json

# Paths
PDF_PATH = "/home/x5/projects/gorlov.me/docs/github/screencapture-github-pavel-gorlov-2025-06-24-13_45_46.pdf"
TIMELINE_PATH = "/home/x5/projects/gorlov.me/docs/github/projects_timeline.md"

def extract_text_from_pdf(pdf_path, page_num=None):
    """Extract text from PDF using OCR"""
    print(f"Converting PDF to images...")

    if page_num:
        images = pdf2image.convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
    else:
        images = pdf2image.convert_from_path(pdf_path)

    print(f"Extracted {len(images)} pages")

    all_text = []
    for i, image in enumerate(images, 1):
        print(f"Processing page {i}/{len(images)}...")
        text = pytesseract.image_to_string(image, lang='eng+rus')
        all_text.append({
            'page': i,
            'text': text
        })

    return all_text

def extract_github_repos(text):
    """Extract GitHub repository names from text"""
    repos = set()

    # Pattern for GitHub URLs
    github_url_pattern = r'github\.com/([^/\s]+)/([^/\s\)]+)'
    matches = re.findall(github_url_pattern, text, re.IGNORECASE)

    for owner, repo in matches:
        # Clean up repo name
        repo = repo.strip()
        # Remove common suffixes
        repo = re.sub(r'\.(git|html?)$', '', repo)
        repos.add(f"{owner}/{repo}")

    # Also look for standalone repo names (after owner/)
    # Pattern: owner/repo-name format
    owner_repo_pattern = r'([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)'
    matches = re.findall(owner_repo_pattern, text)

    for owner, repo in matches:
        if len(repo) > 2:  # Filter out very short matches
            repos.add(f"{owner}/{repo}")

    return repos

def extract_dates_from_text(text):
    """Extract dates from text"""
    dates = []

    # Look for year patterns
    year_pattern = r'\b(20[0-9]{2})\b'
    years = re.findall(year_pattern, text)

    # Look for month names in English
    month_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b'
    months = re.findall(month_pattern, text, re.IGNORECASE)

    return {
        'years': set(years),
        'months': [m.lower() for m in months]
    }

# Test with first page
print("="*80)
print("Testing OCR on first page...")
print("="*80)

page_data = extract_text_from_pdf(PDF_PATH, page_num=1)

print("\n" + "="*80)
print("OCR Result from Page 1:")
print("="*80)
print(page_data[0]['text'][:2000])

print("\n" + "="*80)
print("Extracted GitHub repositories:")
print("="*80)
repos = extract_github_repos(page_data[0]['text'])
for repo in sorted(repos):
    print(f"  - {repo}")

print("\n" + "="*80)
print("Extracted dates:")
print("="*80)
dates = extract_dates_from_text(page_data[0]['text'])
print(f"Years: {sorted(dates['years'])}")
print(f"Months: {dates['months'][:10]}")  # First 10 months
