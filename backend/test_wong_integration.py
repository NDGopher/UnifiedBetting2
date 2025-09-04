"""
Test Wong Teaser Integration

Tests the integration between Wong teaser analysis and BetBCK scraping.
"""

import json
from wong_teaser_scraper import WongTeaserBetBCKScraper

def test_wong_teaser_integration():
    """Test the Wong teaser integration"""
    print("="*80)
    print("WONG TEASER INTEGRATION TEST")
    print("="*80)
    
    # Initialize scraper
    scraper = WongTeaserBetBCKScraper()
    
    print("\n1. Testing Wong teaser analysis...")
    
    # Run analysis
    results = scraper.analyze_wong_teasers()
    
    print(f"   Success: {results['success']}")
    print(f"   Message: {results['message']}")
    
    if results['success']:
        print(f"   Games found: {len(results['games'])}")
        print(f"   Recommendations: {len(results['recommendations'])}")
        
        # Show games
        print("\n2. Games found:")
        for i, game in enumerate(results['games'], 1):
            print(f"   {i}. {game['away_team']} @ {game['home_team']}")
            print(f"      Spread: {game['away_spread']:+.1f}")
            if game.get('total'):
                print(f"      Total: {game['total']}")
        
        # Show top recommendations
        print("\n3. Top recommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"   {i}. {rec['teaser_type']}")
            print(f"      ROI: {rec['roi_percentage']:.1f}%")
            print(f"      Confidence: {rec['confidence_level']}")
            print(f"      Legs: {', '.join(leg['team'] for leg in rec['legs'])}")
    else:
        print(f"   Error: {results['message']}")
    
    print("\n" + "="*80)
    print("INTEGRATION TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_wong_teaser_integration()
