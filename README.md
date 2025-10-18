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

**Last Updated**: Not yet calculated

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

### Setup Labels (One-time)
Run the "Setup Labels" workflow to create series and league labels:
```
Actions → Setup Labels → Run workflow
```

### Manage Player Labels
Run the "Manage Player Labels" workflow to delete and recreate player labels:
```
Actions → Manage Player Labels → Run workflow
```
You can specify custom player names or use the defaults (jack, marjorie, caroline).

### Score Playoffs
The "Score Playoffs" workflow runs automatically when:
- An issue is closed (game completed)
- An issue is labeled (player assignment)

You can also trigger it manually to recalculate scores.

## 🎮 How to Play

1. **Setup**: Run the setup workflows to create labels
2. **Create Games**: Create issues for each game with proper title format
3. **Add Labels**: Label each game with series round and league
4. **Close Won Games**: Close the issue when a game is won
5. **Claim Points**: Add your player label to issues your team won
6. **Watch Scores**: The league table updates automatically!

---

⚾ 🍿 🌭 🧤 🏏 Made with baseball spirit! 🏆
