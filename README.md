# nba_style_analyzer

# NBA Style-of-Play Analyzer

Analyze NBA teams' style using advanced metrics: pace, shooting tendencies (rim/3PT/mid-range), offensive/defensive ratings, free throw rate, offensive rebounding, and more.

Pulls live/full-season data via nba_api and generates a team-colored radar chart for every NBA team.

## Features
- Automatically fetches 2024-25 team stats (change season in main.py if you want current or another year)
- Computes normalized style metrics (0-10 scale relative to league range)
- Generates professional radar charts with team primary color + league average line
- Title shows ORTG | DRTG | Net Rating | Record
- Optional player contribution / hypothetical trade feature is ready for you to extend (see comment at bottom of main.py)

Setup
1. pip install -r requirements.txt
2. python main.py
→ Creates folder "radar_charts" with 30 PNG files (one per team)
