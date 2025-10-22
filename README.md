# ⚾ World Series Bracket Tracker 🏆

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

**Last Updated**: 2025-10-22 02:30:15 UTC

| Rank | Player | Total Points | 🌟 WC | 🎯 DS | 🏅 CS | 🏆 WS | Games |
|------|--------|--------------|-------|-------|-------|-------|-------|
| - | *No games scored yet* | 0 | 0 | 0 | 0 | 0 | 0 |

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
