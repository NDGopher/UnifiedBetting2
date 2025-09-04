#!/usr/bin/env python3

import json

def check_betbck_spreads():
    with open('data/matched_games.json', 'r') as f:
        data = json.load(f)
    
    matched_games = data.get('matched_games', [])
    
    # Find Tampa Bay game
    tampa_game = None
    for game in matched_games:
        home = game.get('pinnacle_home_team', '').lower()
        away = game.get('pinnacle_away_team', '').lower()
        if 'tampa' in home or 'tampa' in away:
            if 'atlanta' in home or 'atlanta' in away:
                tampa_game = game
                break
    
    if tampa_game:
        print(f"Found Tampa Bay game:")
        print(f"  Pinnacle: {tampa_game.get('pinnacle_home_team')} vs {tampa_game.get('pinnacle_away_team')}")
        print(f"  BetBCK: {tampa_game.get('betbck_home_team')} vs {tampa_game.get('betbck_away_team')}")
        
        betbck_game = tampa_game.get('betbck_game', {})
        betbck_odds = betbck_game.get('betbck_site_odds', {})
        
        print(f"\nBetBCK spreads:")
        spreads = betbck_odds.get('site_top_team_spreads', [])
        for spread in spreads:
            print(f"  {spread.get('team', '')} {spread.get('line', '')} @ {spread.get('odds', '')}")
        
        print(f"\nBetBCK bottom team spreads:")
        spreads = betbck_odds.get('site_bottom_team_spreads', [])
        for spread in spreads:
            print(f"  {spread.get('team', '')} {spread.get('line', '')} @ {spread.get('odds', '')}")
    else:
        print("Tampa Bay game not found in matched games")

if __name__ == "__main__":
    check_betbck_spreads()

