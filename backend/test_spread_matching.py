#!/usr/bin/env python3

def test_spread_matching():
    # Simulate the current logic
    bck_line = -2.0  # Tampa Bay -2.0 from BetBCK
    pin_spreads = {
        "2.0": {"nvp_home": 2.019, "nvp_away": 1.981},
        "-2.0": {"nvp_home": 2.419, "nvp_away": 1.705}
    }
    
    print(f"BetBCK line: {bck_line}")
    print(f"Available Pinnacle spreads: {list(pin_spreads.keys())}")
    
    # Current logic
    pin_spread_key = str(bck_line)  # "-2.0"
    pin_spread_market = pin_spreads.get(pin_spread_key)
    print(f"Direct match for '{pin_spread_key}': {pin_spread_market}")
    
    # Try negative conversion
    if not pin_spread_market:
        try:
            neg_key = str(-float(bck_line))  # str(-(-2.0)) = "2.0"
            pin_spread_market = pin_spreads.get(neg_key)
            print(f"Negative conversion '{neg_key}': {pin_spread_market}")
        except Exception as e:
            print(f"Error in negative conversion: {e}")
    
    print(f"Final selected market: {pin_spread_market}")
    
    if pin_spread_market:
        print(f"  NVP Home: {pin_spread_market.get('nvp_home')}")
        print(f"  NVP Away: {pin_spread_market.get('nvp_away')}")

if __name__ == "__main__":
    test_spread_matching()

