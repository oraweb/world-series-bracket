# Testing Guide for Generate Bracket

## Overview

This guide explains how to test the `generate_bracket.py` script and workflow.

## Prerequisites

1. Labels must be set up first (run "Setup Labels" workflow)
2. GitHub token must have `issues: write` and `contents: write` permissions

## Manual Testing

### 1. Test Script Locally (Dry Run)

```bash
# Without creating issues (requires mock token or will fail)
export GITHUB_TOKEN="mock_token"
python3 generate_bracket.py
```

### 2. Test Core Functions

```bash
# Test parsing and extraction functions
python3 << 'EOF'
from generate_bracket import (
    parse_series_from_text, 
    get_series_label, 
    get_league_label,
    extract_game_content
)
import requests

# Test series parsing
print(parse_series_from_text("ALCS Game 5 Final"))
# Expected: ('ALCS', 5)

# Test label generation
print(get_series_label("ALCS"))
# Expected: 'series:cs'

print(get_league_label("NLCS"))
# Expected: 'national'

# Test content extraction
response = requests.get('https://plaintextsports.com/mlb/2025-10-17/tor-sea')
content = extract_game_content(response.text)
print(f"Extracted {len(content)} characters")
# Expected: ~300-400 characters with game data
EOF
```

## GitHub Actions Testing

### 1. Run the Workflow

1. Go to the repository's Actions tab
2. Select "Generate Bracket" workflow
3. Click "Run workflow"
4. (Optional) Enter a year or leave blank for current year
5. Click "Run workflow" button

### 2. Monitor Execution

1. Click on the running workflow
2. Expand the "Generate bracket" step
3. Watch the logs for:
   - API calls count
   - Games found
   - Games created
   - Games skipped (duplicates)
   - Any errors

### 3. Verify Results

After the workflow completes:

1. **Check Issues**:
   - Go to repository Issues tab
   - Verify new issues were created with titles like "ALCS Game 5: 2025-10-17/tor-sea"
   - Check issue bodies contain game data
   - Verify labels are correct (series and league)

2. **Check README.md**:
   - Verify bracket section was added at the top
   - Bracket visualization should be present
   - Format information should be included

3. **Check for Duplicates**:
   - Run the workflow again
   - It should skip all existing games
   - No duplicate issues should be created

## Expected Output

### Console Logs
```
[2025-10-18 06:00:00] [INFO] ⚾🍿🌭 World Series Bracket Generator 🧤⚾
[2025-10-18 06:00:00] [INFO] Repository: oraweb/world-series-bracket
[2025-10-18 06:00:00] [INFO] Processing year: 2025
[2025-10-18 06:00:00] [INFO] Checking existing issues...
[2025-10-18 06:00:00] [INFO] API Call #1: Fetching issues page 1
[2025-10-18 06:00:00] [INFO] Found 0 existing issue(s)
[2025-10-18 06:00:00] [INFO] Fetching schedule for year 2025
[2025-10-18 06:00:00] [INFO] API Call #2: https://plaintextsports.com/mlb/2025/schedule
[2025-10-18 06:00:00] [INFO] Found 34 potential playoff game link(s) from schedule
[2025-10-18 06:00:00] [INFO] Processing games...
[2025-10-18 06:00:00] [INFO] API Call #3: https://plaintextsports.com/mlb/2025-10-17/tor-sea
[2025-10-18 06:00:00] [INFO] API Call #4: Creating issue 'ALCS Game 5: 2025-10-17/tor-sea'
[2025-10-18 06:00:00] [SUCCESS] ✓ Created issue: ALCS Game 5: 2025-10-17/tor-sea
...
[2025-10-18 06:00:30] [INFO] Updating README.md with bracket information...
[2025-10-18 06:00:30] [SUCCESS] ✓ README.md updated successfully
[2025-10-18 06:00:30] [INFO] 
============================================================
STATISTICS SUMMARY
============================================================
Total API calls:        72
Games found:            34
Games created:          34
Games skipped:          0
Errors:                 0
============================================================
[2025-10-18 06:00:30] [INFO] ✅ Bracket generation complete!
```

### Issue Format

**Title**: `ALCS Game 5: 2025-10-17/tor-sea`

**Body**:
```
Game URL: https://plaintextsports.com/mlb/2025-10-17/tor-sea

```
1 Toronto
Blue Jays2W
ALCS Game 5Final2 - 6
2 Seattle
Mariners3W
Play-by-Play   Box Score
1  2  3  4  5  6  7  8  9    T  H  E
------------------------------------------
TOR   0  0  0  0  1  1  0  0  0    2  7  0
SEA   0  1  0  0  0  0  0  5  x    6  5  0
W: Gabe Speier (1-1)
L: Brendon Little (0-1)
Game Time: 6:10 PM-9:10 PM (2h 59m)
```
```

**Labels**: `series:cs`, `american`

## Troubleshooting

### Issue: "GITHUB_TOKEN environment variable not set"
**Solution**: Ensure the workflow has proper permissions and the token is passed via environment variables.

### Issue: "Failed to fetch game data"
**Solution**: 
- Check if plaintextsports.com is accessible
- Verify the game URL format is correct
- Check if the game has series information in the HTML

### Issue: "Duplicate issues created"
**Solution**: The script checks existing issues by title. Ensure titles are consistent and unique.

### Issue: "No games found"
**Solution**: 
- Verify the year is correct
- Check if there are October games in the schedule
- Ensure the schedule URL is correct

### Issue: "README.md not updated"
**Solution**: 
- Check workflow has `contents: write` permission
- Verify the README.md exists in the repository
- Check for API errors in the logs

## Data Sources

- **Schedule**: https://plaintextsports.com/mlb/2025/schedule
- **Game Data**: https://plaintextsports.com/mlb/YYYY-MM-DD/team1-team2
- **Bracket Info**: https://plaintextsports.com/mlb/

## Next Steps After Testing

1. Close issues for completed games
2. Add player labels to issues to assign points
3. Run "Score Playoffs" workflow to update league table
