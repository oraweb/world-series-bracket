# World Series Bracket System - Implementation Guide

## Overview

This repository implements a World Series bracket tracking system using GitHub Issues to represent games and GitHub Actions workflows to automate scoring and label management.

## Components

### Python Scripts

1. **setup_labels.py** - Creates initial series and league labels
   - Creates 4 series round labels: `series:wc`, `series:ds`, `series:cs`, `series:ws`
   - Creates 2 league labels: `american`, `national`
   - Can be run via workflow or manually with proper GitHub token

2. **manage_players.py** - Manages player labels
   - Deletes all existing `player:*` labels
   - Creates new player labels with specified names
   - Default players: jack, marjorie, caroline
   - Accepts custom player names as command-line arguments

3. **score_playoffs.py** - Calculates and updates playoff scores
   - Fetches all issues (games) from the repository
   - Calculates points based on series round and player assignments
   - Updates README.md with league table
   - Scoring rules:
     - Wild Card: 1 point per win
     - Divisional Series: 2 points per win
     - Championship Series: 3 points per win
     - World Series: 4 points per win

### GitHub Actions Workflows

1. **.github/workflows/setup-labels.yml**
   - Trigger: Manual workflow_dispatch
   - Purpose: One-time setup of series and league labels
   - Runs: `setup_labels.py`

2. **.github/workflows/manage-players.yml**
   - Trigger: Manual workflow_dispatch
   - Purpose: Delete and recreate player labels
   - Input: Space-separated list of player names (optional)
   - Runs: `manage_players.py`

3. **.github/workflows/score-playoffs.yml**
   - Trigger: Automatic on issue close or label, or manual
   - Purpose: Calculate and update playoff scores
   - Runs: `score_playoffs.py`
   - Updates: README.md with league table

## Setup Instructions

### Initial Setup

1. Run the "Setup Labels" workflow to create series and league labels:
   - Go to Actions tab
   - Select "Setup Labels"
   - Click "Run workflow"

2. Run the "Manage Player Labels" workflow to create player labels:
   - Go to Actions tab
   - Select "Manage Player Labels"
   - Click "Run workflow"
   - (Optional) Enter custom player names or use defaults

### Creating a Game

Create a new issue with the following format:

**Title**: `NLCS GAME 5: SEA 6 @TOR 2 (2-2)`

**Body**: Include HRE score header and game details:
```
=== SCORE HEADER (HRE) ===
[Plain ASCII text from plaintextsports.com]

Short narrative about main highlights (max 10 lines)

Detailed stats
Leaders
Notable events
Time, date, weather, attendance
```

**Labels**:
- Series round: `series:wc`, `series:ds`, `series:cs`, or `series:ws`
- League: `american` or `national`

### Assigning Points

Players earn points by:
1. Waiting for their team to win a game
2. Adding their player label (`player:jack`, `player:marjorie`, `player:caroline`) to the issue
3. Closing the issue to mark the game as complete

The scoring system will automatically calculate points when:
- An issue is closed (game completed)
- An issue is labeled (player assignment)

## How Scoring Works

1. The workflow triggers when an issue is closed or labeled
2. The `score_playoffs.py` script:
   - Fetches all closed issues
   - Identifies series labels and player labels
   - Calculates points based on series round
   - Aggregates scores by player
   - Generates a new README.md with updated league table
   - Updates the repository README.md

## Label Reference

### Series Labels
- `series:wc` - Wild Card Series (1 point/win)
- `series:ds` - Divisional Series (2 points/win)
- `series:cs` - Championship Series (3 points/win)
- `series:ws` - World Series (4 points/win)

### League Labels
- `american` - American League
- `national` - National League

### Player Labels
- `player:jack`
- `player:marjorie`
- `player:caroline`

## Technical Requirements

- Python 3.x
- requests library (see requirements.txt)
- GitHub token with repo permissions (automatically provided in workflows)

## Customization

### Adding New Players

Run the "Manage Player Labels" workflow with custom player names:
```
Actions → Manage Player Labels → Run workflow → Enter: "sarah mike daniel"
```

### Manual Script Execution

If you need to run scripts manually:

```bash
# Set GitHub token
export GITHUB_TOKEN="your_github_token"

# Setup labels
python3 setup_labels.py

# Manage players (default)
python3 manage_players.py

# Manage players (custom)
python3 manage_players.py sarah mike daniel

# Score playoffs
python3 score_playoffs.py
```

## Troubleshooting

- **Workflow fails**: Check that GitHub token has proper permissions
- **Labels not created**: Verify repository settings allow label creation
- **Scores not updating**: Ensure issues are properly labeled and closed
- **README not updating**: Check workflow logs for API errors

## Data Model

```
Issue (Game)
├── Title: "NLCS GAME 5: SEA 6 @TOR 2 (2-2)"
├── Body: Plain ASCII game details from plaintextsports.com
├── State: open (in progress) or closed (completed)
└── Labels:
    ├── Series: series:wc | series:ds | series:cs | series:ws
    ├── League: american | national
    └── Players: player:* (one or more)
```

## Architecture

```
┌─────────────────┐
│  GitHub Issues  │ (Games)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub Labels  │ (Series, League, Players)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Close Issue    │ (Game Won)
│  Add Label      │ (Player Claims)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │ (Trigger)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│score_playoffs.py│ (Calculate)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   README.md     │ (League Table)
└─────────────────┘
```
