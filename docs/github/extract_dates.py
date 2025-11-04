#!/usr/bin/env python3
"""
Extract date information from OCR data to validate timeline chronology
"""

import json
import re
from collections import defaultdict

def load_ocr_data(json_path):
    """Load OCR extracted data"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def extract_dates_and_repos(text):
    """Extract dates and associated repositories from text"""
    results = []

    # Look for patterns like "Created X commits in Y repositories" with context
    lines = text.split('\n')

    current_context = {
        'year': None,
        'month': None,
        'repos': []
    }

    for i, line in enumerate(lines):
        # Look for years
        year_match = re.search(r'\b(20[0-9]{2})\b', line)
        if year_match:
            current_context['year'] = year_match.group(1)

        # Look for month names (English)
        month_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(20[0-9]{2})?\b', line, re.IGNORECASE)
        if month_match:
            current_context['month'] = month_match.group(1)
            if month_match.group(2):
                current_context['year'] = month_match.group(2)

        # Look for repository mentions
        repo_match = re.search(r'([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)', line)
        if repo_match and len(repo_match.group(2)) > 3:
            repo_full = f"{repo_match.group(1)}/{repo_match.group(2)}"
            if current_context['year'] or current_context['month']:
                results.append({
                    'year': current_context['year'],
                    'month': current_context['month'],
                    'repo': repo_full,
                    'line': line.strip()
                })

    return results

def month_to_russian(month_en):
    """Convert English month abbreviation to Russian"""
    month_map = {
        'jan': 'Январь',
        'feb': 'Февраль',
        'mar': 'Март',
        'apr': 'Апрель',
        'may': 'Май',
        'jun': 'Июнь',
        'jul': 'Июль',
        'aug': 'Август',
        'sep': 'Сентябрь',
        'oct': 'Октябрь',
        'nov': 'Ноябрь',
        'dec': 'Декабрь'
    }
    return month_map.get(month_en.lower()[:3], month_en)

# Load OCR data
print("Loading OCR data...")
ocr_data = load_ocr_data("/home/x5/projects/gorlov.me/docs/github/ocr_output.json")

print("\n" + "="*80)
print("EXTRACTING DATE INFORMATION FROM ALL PAGES")
print("="*80)

all_dated_repos = []

for page_data in ocr_data['pages_text']:
    page_num = page_data['page']
    text = page_data['text']

    dated_repos = extract_dates_and_repos(text)

    if dated_repos:
        print(f"\n--- Page {page_num} ---")
        for entry in dated_repos:
            all_dated_repos.append(entry)
            date_str = f"{entry['year'] or '????'}-{entry['month'] or '??'}"
            print(f"  {date_str}: {entry['repo']}")

# Organize by year and month
by_period = defaultdict(list)
for entry in all_dated_repos:
    if entry['year'] and entry['month']:
        key = f"{entry['year']} {month_to_russian(entry['month'])}"
        by_period[key].append(entry['repo'])

print("\n" + "="*80)
print("DATED REPOSITORIES BY PERIOD")
print("="*80)

if by_period:
    for period in sorted(by_period.keys()):
        repos = list(set(by_period[period]))  # Remove duplicates
        print(f"\n{period}:")
        for repo in sorted(repos):
            print(f"  - {repo}")
else:
    print("\nNo dated repositories could be extracted from OCR.")
    print("This is expected as GitHub contribution graphs show dates visually,")
    print("not as easily OCR-able text adjacent to repository names.")

# Look for any year mentions
print("\n" + "="*80)
print("ALL YEAR MENTIONS IN PDF")
print("="*80)

all_years = set()
for page_data in ocr_data['pages_text']:
    years = re.findall(r'\b(20[0-9]{2})\b', page_data['text'])
    all_years.update(years)

print(f"\nYears found: {sorted(all_years)}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total dated repository mentions found: {len(all_dated_repos)}")
print(f"Unique time periods identified: {len(by_period)}")
print(f"Years detected in PDF: {len(all_years)}")
print("\nConclusion: Date extraction from GitHub screenshot PDFs is very limited.")
print("The contribution graphs display dates visually, making OCR ineffective")
print("for chronological validation of the timeline document.")
