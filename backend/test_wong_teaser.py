"""
Test script for Wong Teaser Analysis System

Demonstrates the system with sample NFL Week 1 2025 data.
"""

import json
from wong_teaser_analyzer import WongTeaserAnalyzer, TeaserType, TeaserOdds, GameData
from wong_data_integration import WongDataIntegration

def test_basic_functionality():
    """Test basic Wong teaser functionality"""
    print("="*80)
    print("WONG TEASER ANALYSIS SYSTEM - TEST")
    print("="*80)
    
    # Initialize analyzer
    analyzer = WongTeaserAnalyzer()
    integration = WongDataIntegration()
    
    # Create sample Week 1 games
    print("\n1. Creating sample Week 1 2025 games...")
    games = integration.create_sample_nfl_week(1)
    
    print(f"   Created {len(games)} sample games:")
    for game in games:
        print(f"   • {game.away_team} @ {game.home_team} ({game.away_spread:+.1f})")
    
    # Test individual game analysis
    print("\n2. Analyzing individual games for Wong criteria...")
    for game in games:
        strict_result = analyzer.check_wong_criteria(game)
        if strict_result["qualifies"]:
            print(f"   ✓ {game.away_team} @ {game.home_team}: QUALIFIES")
            if strict_result["underdog_leg"]:
                leg = strict_result["underdog_leg"]
                print(f"     Underdog leg: {leg.team} {leg.original_spread:+.1f} → {leg.teased_spread:+.1f}")
            if strict_result["favorite_leg"]:
                leg = strict_result["favorite_leg"]
                print(f"     Favorite leg: {leg.team} {leg.original_spread:+.1f} → {leg.teased_spread:+.1f}")
        else:
            print(f"   ✗ {game.away_team} @ {game.home_team}: Does not qualify")
    
    # Generate recommendations
    print("\n3. Generating teaser recommendations...")
    recommendations = analyzer.generate_teaser_recommendations(games)
    
    print(f"   Generated {len(recommendations)} recommendations")
    
    # Show top 5 recommendations
    print("\n4. Top 5 Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"\n   {i}. {rec.teaser_type.value.upper()} TEASER")
        print(f"      ROI: {rec.roi_percentage:.1f}% | Criteria Score: {rec.criteria_score}")
        print(f"      Confidence: {rec.confidence_level} | EV: ${rec.expected_value:.2f}")
        print(f"      Odds: {rec.odds.risk}/{rec.odds.win} ({rec.odds.american_odds:+d})")
        
        print(f"      Legs:")
        for leg in rec.legs:
            print(f"        • {leg.team}: {leg.original_spread:+.1f} → {leg.teased_spread:+.1f}")
            print(f"          ({leg.leg_type}, {leg.win_rate_estimate:.1%} win rate)")
        
        print(f"      Reasoning:")
        for reason in rec.reasoning:
            print(f"        - {reason}")
    
    # Test custom odds
    print("\n5. Testing with custom odds (your book's odds)...")
    custom_odds = {
        TeaserType.TWO_TEAM_6PT: TeaserOdds(110, 100, 100/110),  # -110
        TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 160, 160/100),  # +160
        TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 300, 300/100),  # +300
        TeaserType.THREE_TEAM_10PT: TeaserOdds(120, 100, 100/120),  # -120
    }
    
    custom_recommendations = analyzer.generate_teaser_recommendations(games, custom_odds)
    
    print(f"   Generated {len(custom_recommendations)} recommendations with custom odds")
    
    # Show best custom odds recommendation
    if custom_recommendations:
        best_rec = custom_recommendations[0]
        print(f"\n   Best Custom Odds Recommendation:")
        print(f"   {best_rec.teaser_type.value.upper()}: {best_rec.roi_percentage:.1f}% ROI")
        print(f"   Legs: {', '.join(leg.team for leg in best_rec.legs)}")
        print(f"   EV: ${best_rec.expected_value:.2f}")
    
    # Weekly analysis
    print("\n6. Weekly Analysis Summary...")
    weekly_analysis = integration.get_weekly_analysis(1)
    
    summary = weekly_analysis["summary"]
    print(f"   Total Games: {summary['total_games']}")
    print(f"   Qualifying Games: {summary['qualifying_games']}")
    print(f"   Total Recommendations: {summary['total_recommendations']}")
    
    print(f"\n   Recommendations by Type:")
    for teaser_type, count in summary['recommendations_by_type'].items():
        avg_ev = summary['average_ev_by_type'].get(teaser_type, 0)
        print(f"     {teaser_type}: {count} recommendations (avg {avg_ev:.1f}% ROI)")
    
    # Export results
    print("\n7. Exporting results...")
    filename = integration.export_weekly_report(1)
    print(f"   Exported to: {filename}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*80)

def test_odds_comparison():
    """Test odds comparison functionality"""
    print("\n" + "="*80)
    print("ODDS COMPARISON TEST")
    print("="*80)
    
    analyzer = WongTeaserAnalyzer()
    integration = WongDataIntegration()
    
    # Your book's odds
    your_odds = {
        TeaserType.TWO_TEAM_6PT: TeaserOdds(110, 100, 100/110),  # -110
        TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 160, 160/100),  # +160
        TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 300, 300/100),  # +300
        TeaserType.THREE_TEAM_10PT: TeaserOdds(120, 100, 100/120),  # -120
    }
    
    # Major book odds (worse)
    major_book_odds = {
        TeaserType.TWO_TEAM_6PT: TeaserOdds(135, 100, 100/135),  # -135
        TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 150, 150/100),  # +150
        TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 250, 250/100),  # +250
        TeaserType.THREE_TEAM_10PT: TeaserOdds(130, 100, 100/130),  # -130
    }
    
    games = integration.create_sample_nfl_week(1)
    
    print("\nYour Book's Odds Analysis:")
    your_recs = analyzer.generate_teaser_recommendations(games, your_odds)
    for rec in your_recs[:3]:
        print(f"  {rec.teaser_type.value}: {rec.roi_percentage:.1f}% ROI")
    
    print("\nMajor Book Odds Analysis:")
    major_recs = analyzer.generate_teaser_recommendations(games, major_book_odds)
    for rec in major_recs[:3]:
        print(f"  {rec.teaser_type.value}: {rec.roi_percentage:.1f}% ROI")
    
    print("\nAdvantage of Your Book:")
    for teaser_type in TeaserType:
        your_rec = next((r for r in your_recs if r.teaser_type == teaser_type), None)
        major_rec = next((r for r in major_recs if r.teaser_type == teaser_type), None)
        
        if your_rec and major_rec:
            advantage = your_rec.roi_percentage - major_rec.roi_percentage
            print(f"  {teaser_type.value}: {advantage:+.1f}% ROI advantage")

if __name__ == "__main__":
    test_basic_functionality()
    test_odds_comparison()
