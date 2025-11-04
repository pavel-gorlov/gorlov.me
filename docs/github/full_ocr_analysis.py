#!/usr/bin/env python3
"""
Full OCR-based validation of GitHub projects timeline against PDF screenshots
"""

import pdf2image
import pytesseract
from PIL import Image
import re
from collections import defaultdict
import json

# Paths
PDF_PATH = "/home/x5/projects/gorlov.me/docs/github/screencapture-github-pavel-gorlov-2025-06-24-13_45_46.pdf"

def extract_text_from_all_pages(pdf_path):
    """Extract text from all PDF pages using OCR"""
    print(f"Converting PDF to images...")
    images = pdf2image.convert_from_path(pdf_path, dpi=200)  # Higher DPI for better OCR
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

def extract_github_info(pages_data):
    """Extract GitHub repository names and dates from all pages"""
    repos_by_date = defaultdict(list)
    all_repos = set()

    # Patterns
    # Pattern 1: "Contributed to owner/repo"
    contributed_pattern = r'Contributed to\s+([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)'

    # Pattern 2: GitHub URLs
    github_url_pattern = r'github\.com/([^/\s]+)/([^/\s\)]+)'

    # Pattern 3: Simple owner/repo pattern
    owner_repo_pattern = r'\b([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)\b'

    # Month mapping (English to Russian)
    month_map = {
        'jan': 'январь', 'january': 'январь',
        'feb': 'февраль', 'february': 'февраль',
        'mar': 'март', 'march': 'март',
        'apr': 'апрель', 'april': 'апрель',
        'may': 'май',
        'jun': 'июнь', 'june': 'июнь',
        'jul': 'июль', 'july': 'июль',
        'aug': 'август', 'august': 'август',
        'sep': 'сентябрь', 'september': 'сентябрь',
        'oct': 'октябрь', 'october': 'октябрь',
        'nov': 'ноябрь', 'november': 'ноябрь',
        'dec': 'декабрь', 'december': 'декабрь'
    }

    for page_data in pages_data:
        text = page_data['text']
        page = page_data['page']

        # Extract years
        years = re.findall(r'\b(20[0-9]{2})\b', text)

        # Extract "Contributed to" repos
        contributed_matches = re.findall(contributed_pattern, text, re.IGNORECASE)
        for owner, repo in contributed_matches:
            repo_name = repo.strip()
            # Clean up
            repo_name = re.sub(r'\.(git|html?)$', '', repo_name)
            repo_full = f"{owner}/{repo_name}"
            all_repos.add(repo_full)
            print(f"  Page {page}: Found 'Contributed to' - {repo_full}")

        # Extract from GitHub URLs
        url_matches = re.findall(github_url_pattern, text, re.IGNORECASE)
        for owner, repo in url_matches:
            repo_name = repo.strip()
            repo_name = re.sub(r'\.(git|html?)$', '', repo_name)
            repo_full = f"{owner}/{repo_name}"
            all_repos.add(repo_full)
            print(f"  Page {page}: Found URL - {repo_full}")

        # Extract owner/repo patterns (more generic)
        generic_matches = re.findall(owner_repo_pattern, text)
        for owner, repo in generic_matches:
            if len(repo) > 2 and not repo.endswith('.ru'):  # Filter noise
                repo_full = f"{owner}/{repo}"
                # Only add if it looks reasonable
                if owner not in ['Created', 'commits', 'repository', 'repositories']:
                    all_repos.add(repo_full)

    return {
        'all_repos': sorted(all_repos),
        'total_found': len(all_repos)
    }

def parse_timeline_md(timeline_path):
    """Parse the timeline markdown file"""
    with open(timeline_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    timeline_repos = set()
    timeline_by_period = defaultdict(list)
    current_year = None
    current_month = None

    for line in lines:
        line = line.strip()

        # Year header
        if re.match(r'^##\s+\d{4}$', line):
            current_year = line.replace('#', '').strip()

        # Month header
        elif line.startswith('###'):
            current_month = line.replace('#', '').strip()

        # Project name
        elif line.startswith('-'):
            project = line[1:].strip()
            timeline_repos.add(project)
            if current_year and current_month:
                timeline_by_period[f"{current_year} {current_month}"].append(project)

    return {
        'all_repos': sorted(timeline_repos),
        'total': len(timeline_repos),
        'by_period': timeline_by_period
    }

print("="*80)
print("FULL OCR ANALYSIS - Processing all pages")
print("="*80)

# Process all pages
pages_data = extract_text_from_all_pages(PDF_PATH)

print("\n" + "="*80)
print("Extracting GitHub information from all pages...")
print("="*80)

github_data = extract_github_info(pages_data)

print("\n" + "="*80)
print(f"TOTAL REPOSITORIES FOUND IN PDF: {github_data['total_found']}")
print("="*80)
for repo in github_data['all_repos']:
    print(f"  - {repo}")

# Parse timeline
print("\n" + "="*80)
print("Parsing timeline markdown...")
print("="*80)

timeline_data = parse_timeline_md("/home/x5/projects/gorlov.me/docs/github/projects_timeline.md")

print(f"\nTOTAL REPOSITORIES IN TIMELINE: {timeline_data['total']}")
print("\nFirst 20 repos from timeline:")
for repo in timeline_data['all_repos'][:20]:
    print(f"  - {repo}")

# Save detailed output
output = {
    'pdf_repos': github_data['all_repos'],
    'timeline_repos': timeline_data['all_repos'],
    'pages_text': pages_data
}

with open('/home/x5/projects/gorlov.me/docs/github/ocr_output.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("Detailed output saved to: /home/x5/projects/gorlov.me/docs/github/ocr_output.json")
print("="*80)
