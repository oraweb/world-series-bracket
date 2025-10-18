#!/usr/bin/env python3
"""
Setup initial labels for the World Series bracket tracker.
Creates series round labels and league labels.
"""

import os
import sys
import requests

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'oraweb'
REPO_NAME = 'world-series-bracket'
BASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/labels'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Define labels to create
LABELS = [
    # Series round labels
    {
        'name': 'series:wc',
        'color': 'fbca04',
        'description': 'Wild Card Series - 1 point per win'
    },
    {
        'name': 'series:ds',
        'color': 'f9d0c4',
        'description': 'Divisional Series - 2 points per win'
    },
    {
        'name': 'series:cs',
        'color': 'd4c5f9',
        'description': 'Championship Series - 3 points per win'
    },
    {
        'name': 'series:ws',
        'color': 'e99695',
        'description': 'World Series - 4 points per win'
    },
    # League labels
    {
        'name': 'american',
        'color': '0052cc',
        'description': 'American League'
    },
    {
        'name': 'national',
        'color': 'c5def5',
        'description': 'National League'
    }
]

def get_all_labels():
    """Fetch all existing labels from the repository."""
    response = requests.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def label_exists(label_name, existing_labels):
    """Check if a label already exists."""
    return any(label['name'] == label_name for label in existing_labels)

def create_label(label_data):
    """Create a single label."""
    response = requests.post(BASE_URL, headers=HEADERS, json=label_data)
    return response.status_code == 201

def update_label(label_name, label_data):
    """Update an existing label."""
    url = f"{BASE_URL}/{label_name}"
    response = requests.patch(url, headers=HEADERS, json=label_data)
    return response.status_code == 200

def main():
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    print("⚾🍿🌭 World Series Bracket - Label Setup 🧤⚾\n")
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}\n")
    
    print("📥 Fetching existing labels...")
    existing_labels = get_all_labels()
    existing_names = {label['name'] for label in existing_labels}
    print(f"   Found {len(existing_labels)} existing label(s)\n")
    
    print("🏷️  Creating/updating labels...")
    created_count = 0
    updated_count = 0
    
    for label_info in LABELS:
        label_name = label_info['name']
        label_data = {
            'name': label_name,
            'color': label_info['color'],
            'description': label_info['description']
        }
        
        if label_name in existing_names:
            if update_label(label_name, label_data):
                print(f"   ✓ Updated: {label_name}")
                updated_count += 1
            else:
                print(f"   ✗ Failed to update: {label_name}")
        else:
            if create_label(label_data):
                print(f"   ✓ Created: {label_name}")
                created_count += 1
            else:
                print(f"   ✗ Failed to create: {label_name}")
    
    print(f"\n✅ Setup complete!")
    print(f"   Created: {created_count} label(s)")
    print(f"   Updated: {updated_count} label(s)")

if __name__ == '__main__':
    main()
