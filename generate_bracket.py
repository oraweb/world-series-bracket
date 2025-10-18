#!/usr/bin/env python3
"""
Generate World Series bracket by crawling plaintextsports.com and creating GitHub issues for games.
"""

import os
import sys
import requests
import re
from html import unescape
from datetime import datetime
from typing import Dict, List, Tuple, Optional

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'oraweb'
REPO_NAME = 'world-series-bracket'
BASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Series configuration
SERIES_CONFIG = {
    'WC': {'rounds': 3, 'label': 'series:wc', 'name': 'Wild Card'},
    'DS': {'rounds': 5, 'label': 'series:ds', 'name': 'Division Series'},
    'CS': {'rounds': 7, 'label': 'series:cs', 'name': 'Championship Series'},
    'WS': {'rounds': 7, 'label': 'series:ws', 'name': 'World Series'}
}

# Statistics tracking
stats = {
    'api_calls': 0,
    'games_found': 0,
    'games_created': 0,
    'games_skipped': 0,
    'errors': 0
}


def log(message: str, level: str = 'INFO'):
    """Log a message with timestamp."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")


def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch a URL and return the content."""
    stats['api_calls'] += 1
    log(f"API Call #{stats['api_calls']}: {url}")
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        log(f"Error fetching {url}: {e}", 'ERROR')
        stats['errors'] += 1
        return None


def get_existing_issues() -> Dict[str, dict]:
    """Fetch all existing issues from the repository."""
    log("Checking existing issues...")
    issues = {}
    page = 1
    
    while True:
        url = f"{BASE_URL}/issues?state=all&per_page=100&page={page}"
        stats['api_calls'] += 1
        log(f"API Call #{stats['api_calls']}: Fetching issues page {page}")
        
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            page_issues = response.json()
            
            if not page_issues:
                break
            
            for issue in page_issues:
                issues[issue['title']] = issue
            
            page += 1
        except Exception as e:
            log(f"Error fetching issues: {e}", 'ERROR')
            stats['errors'] += 1
            break
    
    log(f"Found {len(issues)} existing issue(s)")
    return issues


def parse_series_from_text(text: str) -> Optional[Tuple[str, int]]:
    """Parse series information from text (e.g., 'ALCS Game 5' -> ('ALCS', 5))."""
    match = re.search(r'(ALWC|NLWC|ALDS|NLDS|ALCS|NLCS|WS|World Series)\s*Game\s*(\d+)', text, re.IGNORECASE)
    if match:
        series = match.group(1).upper()
        if 'WORLD' in series:
            series = 'WS'
        game_num = int(match.group(2))
        return series, game_num
    return None


def get_series_label(series: str) -> str:
    """Get the GitHub label for a series."""
    if 'WC' in series:
        return 'series:wc'
    elif 'DS' in series:
        return 'series:ds'
    elif 'CS' in series:
        return 'series:cs'
    elif 'WS' in series:
        return 'series:ws'
    return 'series:wc'  # Default


def get_league_label(series: str) -> str:
    """Get the league label for a series."""
    if series.startswith('AL'):
        return 'american'
    elif series.startswith('NL'):
        return 'national'
    # World Series doesn't have a league label
    return None


def extract_game_content(html: str) -> str:
    """Extract the game content from the HTML body."""
    # Extract body content
    body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    if not body_match:
        return ""
    
    body = body_match.group(1)
    
    # Remove script and style tags
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    
    # Replace HTML entities
    body = unescape(body)
    
    # Keep links by replacing them with markdown format
    # Extract links before removing tags
    links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', body)
    for href, text in links:
        if text.strip() and not any(skip in text.lower() for skip in ['dark mode', 'light mode', 'all sports', 'twitter', 'instagram', 'twitch']):
            # Convert to full URL if relative
            if href.startswith('/'):
                href = f'https://plaintextsports.com{href}'
            body = body.replace(f'<a href="{href}">{text}</a>', f'[{text}]({href})')
            body = body.replace(f"<a href='{href}'>{text}</a>", f'[{text}]({href})')
    
    # Convert line breaks
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</div>', '\n', body)
    body = re.sub(r'</p>', '\n\n', body)
    body = re.sub(r'<[^>]+>', '', body)
    
    # Clean up whitespace while preserving structure
    lines = []
    skip_patterns = ['all sports', 'dark mode', 'light mode', 'plaintextsports.com', 
                     'twitter', 'instagram', 'twitch', 'mobile app', 'page loaded', 
                     'data loaded', 'built by']
    
    for line in body.split('\n'):
        stripped = line.strip()
        if stripped:
            # Skip navigation and metadata elements
            if any(skip in stripped.lower() for skip in skip_patterns):
                continue
            lines.append(stripped)
    
    # Find the game information section
    content = []
    found_series = False
    capture_lines = 0
    
    for i, line in enumerate(lines):
        # Look for series information (e.g., "ALCS Game 5")
        if re.search(r'(ALWC|NLWC|ALDS|NLDS|ALCS|NLCS|WS|World Series)\s*Game\s*\d+', line, re.IGNORECASE):
            found_series = True
            # Go back to capture team info
            start_idx = max(0, i - 2)
            for idx in range(start_idx, i):
                if lines[idx] not in content:
                    content.append(lines[idx])
        
        if found_series:
            content.append(line)
            capture_lines += 1
            
            # Stop after we get the game time (around 10-15 lines)
            if 'Game Time' in line or capture_lines > 15:
                break
    
    return '\n'.join(content)


def parse_schedule_for_games(year: int) -> List[Tuple[str, str]]:
    """Parse the schedule page to find playoff games."""
    log(f"Fetching schedule for year {year}")
    schedule_url = f'https://plaintextsports.com/mlb/{year}/schedule'
    html = fetch_url(schedule_url)
    
    if not html:
        return []
    
    # Find all game links in the schedule
    game_links = re.findall(r'href="(/mlb/\d{4}-\d{2}-\d{2}/[^"]+)"', html)
    
    # Get unique links and filter for October games (playoffs)
    unique_links = []
    seen = set()
    for link in game_links:
        # Extract date from link
        date_match = re.search(r'/mlb/(\d{4}-\d{2})-\d{2}/', link)
        if date_match:
            year_month = date_match.group(1)
            # Only include October games (month 10)
            if year_month.endswith('-10') and link not in seen:
                unique_links.append(link)
                seen.add(link)
    
    log(f"Found {len(unique_links)} potential playoff game link(s) from schedule")
    stats['games_found'] = len(unique_links)
    
    return unique_links


def fetch_game_data(game_path: str) -> Optional[Dict]:
    """Fetch and parse game data from a game URL."""
    game_url = f'https://plaintextsports.com{game_path}'
    html = fetch_url(game_url)
    
    if not html:
        return None
    
    # Parse series information
    series_info = parse_series_from_text(html)
    if not series_info:
        log(f"No series information found for {game_path}, skipping")
        return None
    
    series, game_num = series_info
    
    # Extract game content
    content = extract_game_content(html)
    
    if not content:
        log(f"No content extracted for {game_path}", 'WARN')
        return None
    
    return {
        'path': game_path,
        'series': series,
        'game_num': game_num,
        'content': content,
        'url': game_url
    }


def create_issue_title(game_data: Dict) -> str:
    """Create the issue title from game data."""
    # Extract date and teams from path (e.g., /mlb/2025-10-17/tor-sea)
    path_match = re.search(r'/mlb/(\d{4}-\d{2}-\d{2})/([^/]+)', game_data['path'])
    if path_match:
        date = path_match.group(1)
        teams = path_match.group(2)
        series = game_data['series']
        game_num = game_data['game_num']
        return f"{series} Game {game_num}: {date}/{teams}"
    return f"{game_data['series']} Game {game_data['game_num']}: {game_data['path']}"


def create_github_issue(game_data: Dict):
    """Create a GitHub issue for a game."""
    title = create_issue_title(game_data)
    
    body = f"Game URL: {game_data['url']}\n\n"
    body += "```\n"
    body += game_data['content']
    body += "\n```\n"
    
    # Determine labels
    labels = [get_series_label(game_data['series'])]
    league_label = get_league_label(game_data['series'])
    if league_label:
        labels.append(league_label)
    
    issue_data = {
        'title': title,
        'body': body,
        'labels': labels
    }
    
    url = f"{BASE_URL}/issues"
    stats['api_calls'] += 1
    log(f"API Call #{stats['api_calls']}: Creating issue '{title}'")
    
    try:
        response = requests.post(url, headers=HEADERS, json=issue_data)
        response.raise_for_status()
        stats['games_created'] += 1
        log(f"✓ Created issue: {title}", 'SUCCESS')
        return True
    except Exception as e:
        log(f"✗ Failed to create issue '{title}': {e}", 'ERROR')
        stats['errors'] += 1
        return False


def update_readme_with_bracket():
    """Update README.md with playoff bracket information."""
    log("Updating README.md with bracket information...")
    
    # For now, we'll add a simple placeholder at the top
    # In a real implementation, we would parse the bracket structure from the site
    bracket_section = """## 🏆 2025 MLB Postseason Bracket

*Bracket will be displayed here after games are created*

---

"""
    
    # Get current README
    url = f"{BASE_URL}/contents/README.md"
    stats['api_calls'] += 1
    log(f"API Call #{stats['api_calls']}: Fetching current README.md")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        current_file = response.json()
        
        import base64
        current_content = base64.b64decode(current_file['content']).decode()
        
        # Check if bracket section already exists
        if '## 🏆 2025 MLB Postseason Bracket' in current_content:
            log("Bracket section already exists in README.md")
            return
        
        # Add bracket section at the top after the title
        lines = current_content.split('\n')
        new_content = []
        for i, line in enumerate(lines):
            new_content.append(line)
            if i == 0 and line.startswith('#'):  # After the main title
                new_content.append('')
                new_content.append(bracket_section.strip())
        
        new_content_str = '\n'.join(new_content)
        
        # Update README
        encoded_content = base64.b64encode(new_content_str.encode()).decode()
        
        data = {
            'message': '🏆 Add 2025 postseason bracket section',
            'content': encoded_content,
            'sha': current_file['sha'],
            'branch': 'main'
        }
        
        stats['api_calls'] += 1
        log(f"API Call #{stats['api_calls']}: Updating README.md")
        response = requests.put(url, headers=HEADERS, json=data)
        response.raise_for_status()
        
        log("✓ README.md updated successfully", 'SUCCESS')
    except Exception as e:
        log(f"✗ Failed to update README.md: {e}", 'ERROR')
        stats['errors'] += 1


def print_statistics():
    """Print final statistics."""
    log("\n" + "="*60)
    log("STATISTICS SUMMARY")
    log("="*60)
    log(f"Total API calls:        {stats['api_calls']}")
    log(f"Games found:            {stats['games_found']}")
    log(f"Games created:          {stats['games_created']}")
    log(f"Games skipped:          {stats['games_skipped']}")
    log(f"Errors:                 {stats['errors']}")
    log("="*60)


def main():
    if not GITHUB_TOKEN:
        log("❌ Error: GITHUB_TOKEN environment variable not set", 'ERROR')
        sys.exit(1)
    
    log("⚾🍿🌭 World Series Bracket Generator 🧤⚾")
    log(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    log("")
    
    # Get current year
    current_year = datetime.now().year
    log(f"Processing year: {current_year}")
    log("")
    
    # Get existing issues
    existing_issues = get_existing_issues()
    log("")
    
    # Parse schedule for games
    game_links = parse_schedule_for_games(current_year)
    log("")
    
    # Process each game
    log("Processing games...")
    for game_path in game_links:
        # Check if we already have an issue for this game
        # We need to check partial matches since we don't know the series/game number yet
        game_id = game_path.split('/')[-1]  # e.g., 'tor-sea'
        
        # Check if any existing issue title contains this game
        skip = False
        for title in existing_issues.keys():
            if game_id in title.lower():
                log(f"Game {game_path} already exists, skipping")
                stats['games_skipped'] += 1
                skip = True
                break
        
        if skip:
            continue
        
        # Fetch game data
        game_data = fetch_game_data(game_path)
        
        if not game_data:
            stats['games_skipped'] += 1
            continue
        
        # Check again with full title
        title = create_issue_title(game_data)
        if title in existing_issues:
            log(f"Issue '{title}' already exists, skipping")
            stats['games_skipped'] += 1
            continue
        
        # Create issue
        create_github_issue(game_data)
    
    log("")
    
    # Update README with bracket
    update_readme_with_bracket()
    
    log("")
    print_statistics()
    
    log("")
    log("✅ Bracket generation complete!")


if __name__ == '__main__':
    main()
