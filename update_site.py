import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import os

DATA_FILE = os.path.expanduser('~/prediction-tracker/docs/data.json')

def search_arxiv(query, max_results=3):
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
            results.append({
                "date": published,
                "content": f"[{arxiv_id}] {title}",
                "link": f"https://arxiv.org/abs/{arxiv_id}"
            })
        return results
    except Exception as e:
        print(f"Error searching ArXiv for {query}: {e}")
        return []

def main():
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    changed = False
    for prediction in data['predictions']:
        # Clean up the search query: remove special characters and take first few words
        raw_query = prediction['title'].split('will')[0].strip()
        clean_query = "".join([c if c.isalnum() or c.isspace() else " " for c in raw_query]).strip()
        new_updates = search_arxiv(clean_query)
        
        existing_links = {u['link'] for u in prediction['updates']}
        
        for update in new_updates:
            if update['link'] not in existing_links:
                prediction['updates'].insert(0, update)
                # Keep only top 5 updates to keep the site clean
                prediction['updates'] = prediction['updates'][:5]
                changed = True

    if changed:
        data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("Data updated with new research.")
    else:
        print("No new updates found.")

if __name__ == "__main__":
    main()
