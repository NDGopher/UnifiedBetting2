from typing import Dict


def canonicalize_site(site_id: str) -> str:
    s = (site_id or '').lower().strip()
    # Known mappings to our icon columns
    mapping = {
        'fanduel': 'fanduel',
        'fan_duel': 'fanduel',
        'mgm': 'betmgm',
        'betmgm': 'betmgm',
        'draftkings': 'draftkings',
        'dk': 'draftkings',
        'caesars': 'caesars',
        'espnbet': 'espnbet',
        'espn_bet': 'espnbet',
        'pinnacle': 'pinnacle',
        'betonline': 'betonline',
        'bet_online': 'betonline',
        'betrivers': 'betrivers',
        'bet_rivers': 'betrivers',
        'bet365': 'bet365',
        'bet_365': 'bet365',
        'bovada': 'bovada',
        'circa': 'circa',
        'hard_rock': 'hardrock',
        'hardrock': 'hardrock',
    }
    for k, v in mapping.items():
        if k in s:
            return v
    return s.replace(' ', '_')

