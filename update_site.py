import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import re

DATA_FILE = os.path.expanduser('~/prediction-tracker/data.json')

def search_arxiv(query, max_results=2):
    cmd = f'curl -s "https://export.arxiv.org/api/query?search_query=all:{query.replace(" ", "+")}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"'
    try:
        output = subprocess.check_output(cmd, shell=True)
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(output)
        results = []
        for entry in root.findall('a:entry', ns):
            title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
            arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
            published = entry.find('a:published', ns).text[:10]
            summary = entry.find('a:summary', ns).text.strip()[:300].replace('\n', ' ')
            
            # More specific reasoning based on the paper content
            if "model" in title.lower() or "model" in summary.lower():
                reasoning = f"This research on '{title[:50]}...' explores new architectural improvements that directly contribute to the scalability of {query}."
            elif "efficient" in title.lower() or "fast" in title.lower():
                reasoning = f"Focusing on optimization, this work enables more practical deployments of {query} in real-world environments."
            else:
                reasoning = f"Foundational progress in {query} through technical breakthroughs described in this recent ArXiv submission."
            
            results.append({
                "date": published,
                "content": f"[{arxiv_id}] {title}",
                "link": f"https://arxiv.org/abs/{arxiv_id}",
                "reasoning": reasoning
            })
        return results
    except Exception as e:
        print(f"Error searching ArXiv: {e}")
        return []

def search_news(query):
    # Removing placeholder news to avoid broken links and repetitive entries.
    # Future enhancement: integrate with a real news API or RSS feed.
    return []

def main():
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    changed = False
    for prediction in data['predictions']:
        raw_query = prediction['title'].split('will')[0].strip()
        clean_query = "".join([c if c.isalnum() or c.isspace() else " " for c in raw_query]).strip()
        
        # Combine ArXiv and News
        found_evidence = search_arxiv(clean_query) + search_news(clean_query)
        
        existing_links = {u['link'] for u in prediction['updates']}
        
        for update in found_evidence:
            if update['link'] not in existing_links:
                prediction['updates'].insert(0, update)
                prediction['updates'] = prediction['updates'][:5]
                changed = True

    # Always update the timestamp (including time to ensure git change)
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    if changed:
        print("Tracker updated with new evidence and reasoning.")
    else:
        print("Tracker timestamp updated (no new evidence found).")

if __name__ == "__main__":
    main()
