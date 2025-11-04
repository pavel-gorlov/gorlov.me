#!/usr/bin/env python3
"""
Compare timeline with OCR-extracted data and generate discrepancy report
"""

import re
from collections import defaultdict
from difflib import SequenceMatcher
import json

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

def load_ocr_data(json_path):
    """Load OCR extracted data"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def extract_repo_name(full_path):
    """Extract just the repo name from owner/repo format"""
    if '/' in full_path:
        return full_path.split('/')[-1]
    return full_path

def clean_repo_name(name):
    """Clean up OCR errors in repo names"""
    # Remove common OCR artifacts
    cleaned = name.lower().strip()
    # Remove trailing special characters
    cleaned = re.sub(r'[^a-z0-9_.-]+$', '', cleaned)
    return cleaned

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_match(ocr_repo, timeline_repos, threshold=0.7):
    """Find best matching timeline repo for an OCR result"""
    ocr_name = clean_repo_name(extract_repo_name(ocr_repo))
    best_match = None
    best_score = 0

    for timeline_repo in timeline_repos:
        timeline_name = clean_repo_name(timeline_repo)
        score = similarity(ocr_name, timeline_name)

        if score > best_score and score >= threshold:
            best_score = score
            best_match = timeline_repo

    return best_match, best_score

def manual_corrections():
    """Manual mapping for known OCR errors"""
    return {
        # OCR error -> correct name
        'avasales': 'aviasales',
        'avestaton': 'aviastation',
        'statcsites': 'static-sites',
        'reirectme': 'redirectme',
        'postess-svg': 'postcss-svg',
        'postess-s': 'postcss-svg',
        'tavelpayo': 'travelpayouts',
        'tavelpya': 'travelpayouts',
        'ravelpayoute.com': 'travelpayouts.com',
        'travelpayoutscom': 'travelpayouts.com',
        'travelpayoutspartnersback': 'travelpayouts.partners.back',
        'mewno': 'mewtwo',
        'mewwo': 'mewtwo',
        'mewiwo': 'mewtwo',
        'nanowhte': 'nano.white_label',
        'unie': 'uxie',
        'klt': 'klit',
    }

def analyze_ocr_repos(ocr_repos, timeline_repos):
    """Analyze OCR repos and match with timeline"""
    corrections = manual_corrections()
    matches = []
    potential_matches = []
    no_matches = []

    for ocr_repo in ocr_repos:
        repo_name = extract_repo_name(ocr_repo)
        cleaned = clean_repo_name(repo_name)

        # Check manual corrections first
        if cleaned in corrections:
            corrected = corrections[cleaned]
            if corrected in timeline_repos:
                matches.append({
                    'ocr': ocr_repo,
                    'timeline': corrected,
                    'confidence': 'manual',
                    'note': 'Manual correction applied'
                })
                continue

        # Check exact match
        if repo_name in timeline_repos or cleaned in [clean_repo_name(r) for r in timeline_repos]:
            matches.append({
                'ocr': ocr_repo,
                'timeline': repo_name,
                'confidence': 'exact',
                'note': 'Exact match found'
            })
            continue

        # Check fuzzy match
        best_match, score = find_best_match(ocr_repo, timeline_repos, threshold=0.7)
        if best_match:
            potential_matches.append({
                'ocr': ocr_repo,
                'timeline': best_match,
                'confidence': f'{score:.2f}',
                'note': f'Fuzzy match (similarity: {score:.2%})'
            })
        else:
            no_matches.append({
                'ocr': ocr_repo,
                'note': 'No match found in timeline'
            })

    return {
        'matches': matches,
        'potential_matches': potential_matches,
        'no_matches': no_matches
    }

def generate_report(timeline_data, ocr_data, analysis):
    """Generate comprehensive validation report"""
    timeline_repos = set(timeline_data['all_repos'])
    ocr_repos_raw = set(ocr_data['pdf_repos'])

    # Get all matched repos from OCR
    matched_in_ocr = set()
    for match in analysis['matches']:
        matched_in_ocr.add(match['timeline'])
    for match in analysis['potential_matches']:
        matched_in_ocr.add(match['timeline'])

    # Find repos in timeline but not detected in OCR
    missing_in_ocr = timeline_repos - matched_in_ocr

    report = []
    report.append("="*80)
    report.append("GITHUB PROJECTS TIMELINE VALIDATION REPORT")
    report.append("="*80)
    report.append("")

    # Summary
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total projects in timeline: {timeline_data['total']}")
    report.append(f"Total repositories found in PDF (raw OCR): {len(ocr_repos_raw)}")
    report.append(f"Exact matches: {len(analysis['matches'])}")
    report.append(f"Potential matches (fuzzy): {len(analysis['potential_matches'])}")
    report.append(f"No matches from OCR: {len(analysis['no_matches'])}")
    report.append(f"Projects in timeline NOT detected in PDF: {len(missing_in_ocr)}")
    report.append("")

    # Accuracy assessment
    detected_count = len(matched_in_ocr)
    accuracy = (detected_count / timeline_data['total'] * 100) if timeline_data['total'] > 0 else 0
    report.append(f"Detection rate: {detected_count}/{timeline_data['total']} ({accuracy:.1f}%)")
    report.append("")

    # Exact matches
    if analysis['matches']:
        report.append("="*80)
        report.append(f"EXACT MATCHES ({len(analysis['matches'])} found)")
        report.append("="*80)
        for match in sorted(analysis['matches'], key=lambda x: x['timeline']):
            report.append(f"  OCR: {match['ocr']:<40} -> Timeline: {match['timeline']}")
            if match['note']:
                report.append(f"       Note: {match['note']}")
        report.append("")

    # Potential matches
    if analysis['potential_matches']:
        report.append("="*80)
        report.append(f"POTENTIAL MATCHES - FUZZY ({len(analysis['potential_matches'])} found)")
        report.append("="*80)
        for match in sorted(analysis['potential_matches'], key=lambda x: float(x['confidence']), reverse=True):
            report.append(f"  OCR: {match['ocr']:<40} -> Timeline: {match['timeline']}")
            report.append(f"       {match['note']}")
        report.append("")

    # No matches
    if analysis['no_matches']:
        report.append("="*80)
        report.append(f"NO MATCHES FROM OCR ({len(analysis['no_matches'])} found)")
        report.append("="*80)
        report.append("These OCR results could not be matched to any timeline project:")
        for item in sorted(analysis['no_matches'], key=lambda x: x['ocr']):
            report.append(f"  - {item['ocr']}")
        report.append("")

    # Missing in OCR
    if missing_in_ocr:
        report.append("="*80)
        report.append(f"PROJECTS IN TIMELINE NOT DETECTED IN PDF ({len(missing_in_ocr)} projects)")
        report.append("="*80)
        report.append("These projects are in the timeline but were not found in the OCR scan:")
        report.append("")

        # Group by first letter for easier reading
        by_letter = defaultdict(list)
        for repo in sorted(missing_in_ocr):
            first_letter = repo[0].upper() if repo else 'OTHER'
            by_letter[first_letter].append(repo)

        for letter in sorted(by_letter.keys()):
            report.append(f"[{letter}]")
            for repo in by_letter[letter]:
                report.append(f"  - {repo}")
            report.append("")

    # Recommendations
    report.append("="*80)
    report.append("RECOMMENDATIONS")
    report.append("="*80)
    report.append("")
    report.append("1. OCR QUALITY ISSUES:")
    report.append("   - The OCR detected only a small portion of projects due to:")
    report.append("     * GitHub contribution graphs are visual/graphical")
    report.append("     * Not all project names are displayed as text in screenshots")
    report.append("     * OCR errors in text recognition")
    report.append("")
    report.append("2. VALIDATION METHOD:")
    report.append("   - The PDF appears to be GitHub contribution screenshots")
    report.append("   - These mainly show contribution activity graphs, not full project lists")
    report.append("   - Only projects with 'Contributed to X/Y' text are reliably detected")
    report.append("")
    report.append("3. TIMELINE ACCURACY:")
    report.append("   - Based on limited OCR detection, cannot fully validate all timeline entries")
    report.append("   - Detected projects DO appear in timeline (good sign)")
    report.append("   - Most timeline entries cannot be verified from PDF alone")
    report.append("")
    report.append("4. SUGGESTIONS:")
    report.append("   - Consider using GitHub API for more accurate validation")
    report.append("   - Or use git commit history directly from repositories")
    report.append("   - OCR is limited for validating contribution graphs")
    report.append("")

    return "\n".join(report)

# Main execution
print("Loading timeline data...")
timeline_data = parse_timeline_md("/home/x5/projects/gorlov.me/docs/github/projects_timeline.md")

print("Loading OCR data...")
ocr_data = load_ocr_data("/home/x5/projects/gorlov.me/docs/github/ocr_output.json")

print("Analyzing matches...")
analysis = analyze_ocr_repos(ocr_data['pdf_repos'], timeline_data['all_repos'])

print("Generating report...")
report = generate_report(timeline_data, ocr_data, analysis)

# Print report
print("\n" + report)

# Save report
report_path = "/home/x5/projects/gorlov.me/docs/github/validation_report.txt"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print("\n" + "="*80)
print(f"Report saved to: {report_path}")
print("="*80)
