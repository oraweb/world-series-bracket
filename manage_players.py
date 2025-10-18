#!/usr/bin/env python3
"""
Manage player labels for the World Series bracket tracker.
This script deletes existing player labels and creates new ones.
"""

import os
import sys
from typing import List
import requests

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'oraweb'
REPO_NAME = 'world-series-bracket'
BASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/labels'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

PLAYER_LABEL_COLORS = ['#bfdadc', '#c5def5', '#f9d0c4', '#d4c5f9', '#c2e0c6', '#fad8b8', '#bfd4f2', '#f9c5d5', '#d5f4e6', '#fbe4d5']

def get_all_labels() -> List[dict]:
    """Fetch all existing labels from the repository."""
    response = requests.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def delete_player_labels():
    """Delete all labels that start with 'player:'."""
    print("🗑️  Deleting existing player labels...")
    labels = get_all_labels()
    deleted_count = 0
    
    for label in labels:
        if label['name'].startswith('player:'):
            delete_url = f"{BASE_URL}/{label['name']}"
            response = requests.delete(delete_url, headers=HEADERS)
            if response.status_code == 204:
                print(f"   ✓ Deleted: {label['name']}")
                deleted_count += 1
            else:
                print(f"   ✗ Failed to delete: {label['name']}")
    
    print(f"Deleted {deleted_count} player label(s)\n")

def create_player_labels(players: List[str]):
    """Create new player labels."""
    print("⚾ Creating new player labels...")
    created_count = 0
    
    for idx, player in enumerate(players):
        label_name = f"player:{player.lower()}"
        color = PLAYER_LABEL_COLORS[idx % len(PLAYER_LABEL_COLORS)]
        
        label_data = {
            'name': label_name,
            'color': color.lstrip('#'),
            'description': f'Player: {player}'
        }
        
        response = requests.post(BASE_URL, headers=HEADERS, json=label_data)
        if response.status_code == 201:
            print(f"   ✓ Created: {label_name} ({color})")
            created_count += 1
        else:
            print(f"   ✗ Failed to create: {label_name} - {response.text}")
    
    print(f"Created {created_count} player label(s)\n")

def main():
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    # Get players from command line arguments or use defaults
    if len(sys.argv) > 1:
        players = sys.argv[1:]
    else:
        players = ['jack', 'marjorie', 'caroline']
    
    print("⚾🍿🌭 World Series Bracket - Player Label Manager 🧤⚾\n")
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Players: {', '.join(players)}\n")
    
    delete_player_labels()
    create_player_labels(players)
    
    print("✅ Player label management complete!")

if __name__ == '__main__':
    main()