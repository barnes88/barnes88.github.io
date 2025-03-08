#!/usr/bin/env python3
import os
import json
import time
import random
import scholarly
import bibtexparser
from pathlib import Path

def load_bibtex(bib_file):
    with open(bib_file, 'r', encoding='utf-8') as f:
        return bibtexparser.load(f)

def save_bibtex(bib_database, bib_file):
    with open(bib_file, 'w', encoding='utf-8') as f:
        bibtexparser.dump(bib_database, f)

def update_citations():
    bib_file = Path('_bibliography/papers.bib')
    
    # Load existing bibliography
    try:
        bib_database = load_bibtex(bib_file)
    except FileNotFoundError:
        print(f"Bibliography file not found at {bib_file}")
        return
    except Exception as e:
        print(f"Error loading bibliography: {str(e)}")
        return
    
    # Get Google Scholar ID from _config.yml
    try:
        with open('_config.yml', 'r', encoding='utf-8') as f:
            config = f.read()
            scholar_id = None
            for line in config.split('\n'):
                if 'scholar_userid:' in line:
                    scholar_id = line.split(':')[1].strip().split('&')[0]
                    break
        
        if not scholar_id:
            print("No Google Scholar ID found in _config.yml")
            return
    except Exception as e:
        print(f"Error reading _config.yml: {str(e)}")
        return

    try:
        # Get author's data
        print("Fetching data from Google Scholar...")
        author = scholarly.scholarly.search_author_id(scholar_id)
        if not author:
            print("Author not found on Google Scholar")
            return
            
        author = scholarly.scholarly.fill(author)
        if not author or 'publications' not in author:
            print("No publications found for author")
            return
            
        # Create a mapping of titles to citation counts
        citations = {}
        print("Processing publications...")
        for pub in author['publications']:
            try:
                pub_filled = scholarly.scholarly.fill(pub)
                if pub_filled and 'bib' in pub_filled and 'title' in pub_filled['bib']:
                    title = pub_filled['bib']['title']
                    cites = pub_filled.get('num_citations', 0)
                    citations[title.lower()] = cites
                    print(f"Found {cites} citations for: {title}")
                # Add random delay to avoid rate limiting
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"Error processing publication: {str(e)}")
                continue
        
        # Update citation counts in bibtex entries
        updated = False
        for entry in bib_database.entries:
            title = entry['title'].lower()
            if title in citations:
                entry['scholar'] = str(citations[title])
                updated = True
                print(f"Updated citation count for: {entry['title']}")
        
        if updated:
            save_bibtex(bib_database, bib_file)
            print("Updated citation counts in papers.bib")
        else:
            print("No citations needed updating")
            
    except Exception as e:
        print(f"Error updating citations: {str(e)}")

if __name__ == '__main__':
    update_citations() 