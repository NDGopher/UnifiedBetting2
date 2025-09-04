#!/usr/bin/env python3

import json

def check_tampa_odds():
    with open('data/ev_table.json', 'r') as f:
        data = json.load(f)
    
    events = data.get('ev_table', [])
    print(f"Total EV events: {len(events)}")
    
    # Find Tampa Bay games
    tampa_games = []
    for event in events:
        event_name = event.get('event', '').lower()
        if 'tampa' in event_name and 'atlanta' in event_name:
            tampa_games.append(event)
    
    print(f"\nFound {len(tampa_games)} Tampa Bay vs Atlanta games:")
    for i, game in enumerate(tampa_games):
        print(f"\n{i+1}. {game.get('bet', '')}")
        print(f"   NVP: {game.get('pin_nvp', '')}")
        print(f"   Book Odds: {game.get('betbck_odds', '')}")
        print(f"   EV: {game.get('ev', '')}")
        print(f"   Event ID: {game.get('event_id', '')}")
    
    # Also check the matched games to see the raw data
    print(f"\n=== Checking Matched Games ===")
    with open('data/matched_games.json', 'r') as f:
        matched_data = json.load(f)
    
    matched_games = matched_data.get('matched_games', [])
    tampa_matched = []
    for game in matched_games:
        home = game.get('pinnacle_home_team', '').lower()
        away = game.get('pinnacle_away_team', '').lower()
        if 'tampa' in home or 'tampa' in away:
            if 'atlanta' in home or 'atlanta' in away:
                tampa_matched.append(game)
    
    print(f"Found {len(tampa_matched)} Tampa Bay matched games:")
    for i, game in enumerate(tampa_matched):
        print(f"\n{i+1}. {game.get('pinnacle_home_team', '')} vs {game.get('pinnacle_away_team', '')}")
        print(f"   Event ID: {game.get('pinnacle_event_id', '')}")
        print(f"   Sport: {game.get('sport_name', '')}")

if __name__ == "__main__":
    check_tampa_odds()

