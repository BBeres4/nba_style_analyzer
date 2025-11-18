
import os
import pandas as pd
import matplotlib.pyplot as plt
from math import pi
from nba_api.stats.endpoints import LeagueDashTeamStats, LeagueDashTeamShotLocations

# ------------------ CONFIG ------------------
season = '2024-25'  # Change to '2025-26' for current season if you want
# ------------------------------------------

# Team primary colors (hex)
team_colors = {
    "Atlanta Hawks": "#E03A3E",
    "Boston Celtics": "#007A33",
    "Brooklyn Nets": "#000000",
    "Charlotte Hornets": "#1D1160",
    "Chicago Bulls": "#CE1141",
    "Cleveland Cavaliers": "#860038",
    "Dallas Mavericks": "#00538C",
    "Denver Nuggets": "#0E2240",
    "Detroit Pistons": "#C8102E",
    "Golden State Warriors": "#1D1160",
    "Houston Rockets": "#CE1141",
    "Indiana Pacers": "#002D62",
    "LA Clippers": "#C8102E",
    "Los Angeles Lakers": "#552583",
    "Memphis Grizzlies": "#12173F",
    "Miami Heat": "#98002E",
    "Milwaukee Bucks": "#00471B",
    "Minnesota Timberwolves": "#0C2340",
    "New Orleans Pelicans": "#0C2340",
    "New York Knicks": "#006BB6",
    "Oklahoma City Thunder": "#007AC1",
    "Orlando Magic": "#0077C0",
    "Philadelphia 76ers": "#006BB6",
    "Phoenix Suns": "#1D1160",
    "Portland Trail Blazers": "#E03A3E",
    "Sacramento Kings": "#5A2D81",
    "San Antonio Spurs": "#C4CED4",
    "Toronto Raptors": "#CE1141",
    "Utah Jazz": "#002B5C",
    "Washington Wizards": "#002B5C",
}

# Fetch data
print("Fetching data from nba_api...")
base_stats = LeagueDashTeamStats(
    measure_type_detailed_defense='Base',
    per_mode_detailed='Totals',
    season=season,
    season_type_all_star='Regular Season'
).get_data_frames()[0]

advanced_stats = LeagueDashTeamStats(
    measure_type_detailed_defense='Advanced',
    per_mode_detailed='Totals',
    season=season,
    season_type_all_star='Regular Season'
).get_data_frames()[0]

shot_locations = LeagueDashTeamShotLocations(
    per_mode_simple='Totals',
    season=season,
    season_type_all_star='Regular Season'
).get_data_frames()[0]

# Clean shot location column names (multi-level → single level)
shot_locations.columns = shot_locations.columns.map(' '.join).str.strip()

# Robust column selection
rim_fga_col = [col for col in shot_locations.columns if 'Restricted Area' in col and 'FGA' in col][0]
mid_fga_col = [col for col in shot_locations.columns if 'Mid-Range' in col and 'FGA' in col][0]
three_fga_cols = [col for col in shot_locations.columns if '3 FGA' in col]

total_fga = shot_locations.filter(like='FGA').sum(axis=1)

shot_locations['RIM_RATE'] = shot_locations[rim_fga_col] / total_fga
shot_locations['MID_RATE'] = shot_locations[mid_fga_col] / total_fga
shot_locations['3PT_RATE'] = shot_locations[three_fga_cols].sum(axis=1) / total_fga

# Merge everything
df = base_stats[['TEAM_ID', 'TEAM_NAME', 'GP', 'W', 'L', 'FGA', 'FG3A', 'FTA']]
df['3PAR'] = base_stats['FG3A'] / base_stats['FGA']
df['FTR'] = base_stats['FTA'] / base_stats['FGA']

df = df.merge(advanced_stats[['TEAM_ID', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE', 'ORB_PCT']], on='TEAM_ID')
df = df.merge(shot_locations[['TEAM_ID', 'RIM_RATE', 'MID_RATE', '3PT_RATE']], on='TEAM_ID')

# Metrics we will put on the radar
metrics = ['PACE', '3PAR', 'RIM_RATE', 'MID_RATE', 'FTR', 'ORB_PCT']

# Normalize each metric 0–10 (league range)
for metric in metrics:
    min_val = df[metric].min()
    max_val = df[metric].max()
    range_val = max_val - min_val
    if range_val == 0:
        df[f'{metric}_NORM'] = 5.0
    else:
        df[f'{metric}_NORM'] = (df[metric] - min_val) / range_val * 10

categories = [
    'Pace',
    '3-Pt Attempt\nRate',
    'Rim Attempt\nRate',
    'Mid-Range\nRate',
    'Free Throw\nRate',
    'Off. Rebound %'
]

norm_cols = [m + '_NORM' for m in metrics]

# Create output folder
os.makedirs('radar_charts', exist_ok=True)

print("Generating radar charts...")

for _, row in df.iterrows():
    team_name = row['TEAM_NAME']
    color = team_colors.get(team_name, '#333333')

    values = row[norm_cols].tolist()
    values += values[:1]  # close the circle

    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]

    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111, polar=True)

    ax.plot(angles, values, linewidth=3, linestyle='solid', color=color)
    ax.fill(angles, values, color=color, alpha=0.25)

    # League average line
    avg = [5] * len(categories)
    avg += avg[:1]
    ax.plot(angles, avg, linewidth=2, linestyle='--', color='gray', alpha=0.8)

    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([a * 180 / pi for a in angles[:-1]], categories, fontsize=12)

    ax.set_rlim(0, 10)
    ax.set_rticks([2, 4, 6, 8, 10])
    ax.grid(True, color='gray', linestyle='--')
    ax.spines['polar'].set_visible(False)
    ax.set_yticklabels([])  # hide radial labels for cleaner look

    title = f"{team_name} • 2024-25 Style of Play\n" \
            f"ORTG {row['OFF_RATING']:.1f} • DRTG {row['DEF_RATING']:.1f} " \
            f"• Net {row['NET_RATING']:+.1f} • {row['W']}-{row['L']}"

    plt.title(title, size=18, color=color, pad=20)

    plt.savefig(f"radar_charts/{team_name.replace(' ', '_').replace('/', '_')}.png",
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

print("Done! Check the 'radar_charts' folder — 30 team radar charts generated.")

# ==================================================================
# OPTIONAL / FUTURE: Add new player contribution (hypothetical trade / rookie impact)
# Example idea:
# 1. Fetch a player's shot chart or playtype data
# 2. Weight blend player stats with current team stats by projected minutes
# 3. Re-normalize and redraw radar
# You can copy the loop above and adjust the row values accordingly.
# Example stub:
# player_row = row.copy()
# player_row['RIM_RATE'] = 0.9 * row['RIM_RATE'] + 0.1 * player_rim_rate
# ... then re-normalize only the changed metrics and redraw
# ==================================================================
