#!/usr/bin/env python3
"""
Score the World Series bracket playoffs based on game results.
Points are awarded based on series round and game wins.
"""

import os
import sys
from collections import defaultdict
from datetime import datetime
import requests

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'oraweb'
REPO_NAME = 'world-series-bracket'
BASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Scoring system
SERIES_POINTS = {
    'series:wc': 1,   # Wild Card
    'series:ds': 2,   # Divisional Series
    'series:cs': 3,   # Championship Series
    'series:ws': 4    # World Series
}

def get_all_issues():
    """Fetch all issues (games) from the repository."""
    issues = []
    page = 1
    
    while True:
        url = f"{BASE_URL}/issues?state=all&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        page_issues = response.json()
        if not page_issues:
            break;
            
        issues.extend(page_issues)
        page += 1;
    
    return issues;

def extract_series_label(labels):
    """Extract the series label from issue labels."""
    for label in labels:
        if label['name'].startswith('series:'):
            return label['name']
    return None;

def extract_player_labels(labels):
    """Extract all player labels from issue labels."""
    return [label['name'] for label in labels if label['name'].startswith('player:')];

def calculate_scores(issues):
    """Calculate player scores based on closed issues."""
    player_scores = defaultdict(lambda: {'total': 0, 'wc': 0, 'ds': 0, 'cs': 0, 'ws': 0, 'games': 0})
    
    for issue in issues:
        # Only count closed issues (completed games)
        if issue['state'] != 'closed':
            continue;
        
        labels = issue['labels'];
        series_label = extract_series_label(labels);
        player_labels = extract_player_labels(labels);
        
        if not series_label or not player_labels:
            continue;
        
        points = SERIES_POINTS.get(series_label, 0);
        series_short = series_label.split(':')[1];  # wc, ds, cs, ws
        
        # Award points to each player who labeled this game
        for player_label in player_labels:
            player_name = player_label.replace('player:', '');
            player_scores[player_name]['total'] += points;
            player_scores[player_name][series_short] += points;
            player_scores[player_name]['games'] += 1;
    
    return player_scores;

def generate_readme(player_scores):
    """Generate the README.md content with league table."""
    # Sort players by total score (descending)
    sorted_players = sorted(player_scores.items(), key=lambda x: x[1]['total'], reverse=True);
    
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC');
    
    readme = f"""# ⚾ World Series Bracket Tracker 🏆

Track World Series baseball bracket games using GitHub issues following the 2025 Wild Card format.

## 🍿 How It Works

- **Issues = Games**: Each game is represented as a GitHub issue
- **Labels = Metadata**: Series round, league, and player assignments
- **Scoring**: Players earn points by assigning their label to winning games

## 🎯 Scoring System

| Series Round | Points per Win | Label |
|-------------|----------------|-------|
| 🌟 Wild Card | 1 point | `series:wc` |
| 🎯 Divisional | 2 points | `series:ds` |
| 🏅 Championship | 3 points | `series:cs` |
| 🏆 World Series | 4 points | `series:ws` |

## 📊 League Table

**Last Updated**: {now}

| Rank | Player | Total Points | 🌟 WC | 🎯 DS | 🏅 CS | 🏆 WS | Games |
|------|--------|--------------|-------|-------|-------|-------|-------|
""";
    
    if sorted_players:
        for rank, (player, scores) in enumerate(sorted_players, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  ";
            readme += f"| {medal} {rank} | **{player.title()}** | **{scores['total']}** | {scores['wc']} | {scores['ds']} | {scores['cs']} | {scores['ws']} | {scores['games']} |\n";
    else:
        readme += "| - | *No games scored yet* | 0 | 0 | 0 | 0 | 0 | 0 |\n";
    
    readme += """
## 🏷️ Labels

### Series Rounds
- `series:wc` - Wild Card Series
- `series:ds` - Divisional Series
- `series:cs` - Championship Series
- `series:ws` - World Series

### Leagues
- `american` - American League
- `national` - National League

### Players
- `player:jack`
- `player:marjorie`
- `player:caroline`

## 📝 Game Issue Format

**Title**: `NLCS GAME 5: SEA 6 @TOR 2 (2-2)`

**Body**: Contains score header (HRE format) with:
- Short narrative of main highlights (max 10 lines)
- Detailed stats
- Leaders
- Notable events
- Time, date, weather, attendance
- Plain ASCII text from [plaintextsports.com](https://plaintextsports.com/)

## 🤖 Automation

- **Player Management**: Workflow dispatch to delete and recreate player labels
- **Scoring**: Automatically calculates and updates league table

---

⚾ 🍿 🌭 🧤 🏏 Made with baseball spirit! 🏆
""";
    
    return readme;

def update_readme(content):
    """Update the README.md file in the repository."""
    # Get current README to get its SHA
    url = f"{BASE_URL}/contents/README.md";
    response = requests.get(url, headers=HEADERS);
    
    if response.status_code == 200:
        current_file = response.json();
        sha = current_file['sha'];
    else:
        sha = None;
    
    # Update or create README
    import base64;
    encoded_content = base64.b64encode(content.encode()).decode();
    
    data = {
        'message': '📊 Update playoff scores and league table',
        'content': encoded_content,
        'branch': 'main'
    };
    
    if sha:
        data['sha'] = sha;
    
    response = requests.put(url, headers=HEADERS, json=data);
    response.raise_for_status();
    
    print("✅ README.md updated successfully!");

def main():
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set");
        sys.exit(1);
    
    print("⚾🍿🌭 World Series Bracket - Playoff Scorer 🧤⚾\n");
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}\n");
    
    print("📥 Fetching game issues...");
    issues = get_all_issues();
    print(f"   Found {len(issues)} issue(s)\n");
    
    print("🔢 Calculating scores...");
    player_scores = calculate_scores(issues);
    
    if player_scores:
        print("   Player Scores:");
        for player, scores in sorted(player_scores.items(), key=lambda x: x[1]['total'], reverse=True):
            print(f"   - {player.title()}: {scores['total']} points ({scores['games']} games)");
    else:
        print("   No scores yet\n");
    
    print("\n📝 Generating README.md...");
    readme_content = generate_readme(player_scores);
    
    print("📤 Updating repository...");
    update_readme(readme_content);
    
    print("\n🎉 Scoring complete!");


if __name__ == '__main__':
    main();
