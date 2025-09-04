"""
Wong Teaser Command Line Interface

Provides command-line access to Wong teaser analysis functionality.
"""

import argparse
import json
import sys
from typing import Dict, Any, List
from datetime import datetime
from wong_teaser_analyzer import WongTeaserAnalyzer, TeaserType, TeaserOdds, GameData
from wong_data_integration import WongDataIntegration

def print_recommendation_summary(recommendations: List[Any], limit: int = 10):
    """Print a summary of top recommendations"""
    print(f"\n{'='*80}")
    print(f"TOP {min(limit, len(recommendations))} WONG TEASER RECOMMENDATIONS")
    print(f"{'='*80}")
    
    for i, rec in enumerate(recommendations[:limit], 1):
        print(f"\n{i}. {rec.teaser_type.value.upper()} TEASER")
        print(f"   ROI: {rec.roi_percentage:.1f}% | Criteria Score: {rec.criteria_score}")
        print(f"   Confidence: {rec.confidence_level} | EV: ${rec.expected_value:.2f}")
        print(f"   Odds: {rec.odds.risk}/{rec.odds.win} ({rec.odds.american_odds:+d})")
        
        print(f"   Legs:")
        for leg in rec.legs:
            print(f"     • {leg.team}: {leg.original_spread:+.1f} → {leg.teased_spread:+.1f}")
            print(f"       ({leg.leg_type}, {leg.win_rate_estimate:.1%} win rate)")
        
        print(f"   Reasoning:")
        for reason in rec.reasoning:
            print(f"     - {reason}")

def print_weekly_summary(analysis: Dict[str, Any]):
    """Print weekly analysis summary"""
    print(f"\n{'='*80}")
    print(f"WEEK {analysis['week']} NFL WONG TEASER ANALYSIS")
    print(f"{'='*80}")
    
    summary = analysis['summary']
    print(f"Total Games: {summary['total_games']}")
    print(f"Qualifying Games: {summary['qualifying_games']}")
    print(f"Total Recommendations: {summary['total_recommendations']}")
    
    print(f"\nRecommendations by Type:")
    for teaser_type, count in summary['recommendations_by_type'].items():
        avg_ev = summary['average_ev_by_type'].get(teaser_type, 0)
        print(f"  {teaser_type}: {count} recommendations (avg {avg_ev:.1f}% ROI)")
    
    if summary['top_recommendation']:
        top_rec = summary['top_recommendation']
        print(f"\nTop Recommendation:")
        print(f"  {top_rec.teaser_type.value}: {top_rec.roi_percentage:.1f}% ROI")
        print(f"  Legs: {', '.join(leg.team for leg in top_rec.legs)}")

def analyze_week(args):
    """Analyze a specific NFL week"""
    integration = WongDataIntegration()
    
    print(f"Analyzing Week {args.week}...")
    analysis = integration.get_weekly_analysis(args.week, args.source)
    
    print_weekly_summary(analysis)
    
    if args.detailed:
        print_recommendation_summary(analysis['recommendations'], args.limit)
    
    if args.export:
        filename = integration.export_weekly_report(args.week)
        print(f"\nExported to: {filename}")

def analyze_custom_odds(args):
    """Analyze with custom odds"""
    analyzer = WongTeaserAnalyzer()
    integration = WongDataIntegration()
    
    # Parse custom odds
    custom_odds = {}
    for odds_str in args.odds:
        parts = odds_str.split(':')
        if len(parts) != 2:
            print(f"Invalid odds format: {odds_str}. Use format: type:risk/win")
            continue
        
        teaser_type_str, odds_part = parts
        try:
            teaser_type = TeaserType(teaser_type_str)
        except ValueError:
            print(f"Invalid teaser type: {teaser_type_str}")
            continue
        
        risk_win = odds_part.split('/')
        if len(risk_win) != 2:
            print(f"Invalid odds format: {odds_part}. Use format: risk/win")
            continue
        
        try:
            risk = int(risk_win[0])
            win = int(risk_win[1])
            custom_odds[teaser_type] = TeaserOdds(risk, win, win/risk)
        except ValueError:
            print(f"Invalid risk/win values: {odds_part}")
            continue
    
    print("Analyzing with custom odds...")
    analysis = integration.get_weekly_analysis(args.week, args.source)
    
    # Re-analyze with custom odds
    games = integration.create_sample_nfl_week(args.week)
    recommendations = analyzer.generate_teaser_recommendations(games, custom_odds)
    
    print(f"\nCustom Odds Analysis:")
    for teaser_type, odds in custom_odds.items():
        print(f"  {teaser_type.value}: {odds.risk}/{odds.win} ({odds.american_odds:+d})")
    
    print_recommendation_summary(recommendations, args.limit)

def compare_odds(args):
    """Compare different odds structures"""
    analyzer = WongTeaserAnalyzer()
    integration = WongDataIntegration()
    
    # Standard odds from conversation
    standard_odds = {
        TeaserType.TWO_TEAM_6PT: TeaserOdds(110, 100, 100/110),
        TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 160, 160/100),
        TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 300, 300/100),
        TeaserType.THREE_TEAM_10PT: TeaserOdds(120, 100, 100/120),
    }
    
    # Major book odds (worse)
    major_book_odds = {
        TeaserType.TWO_TEAM_6PT: TeaserOdds(135, 100, 100/135),
        TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 150, 150/100),
        TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 250, 250/100),
        TeaserType.THREE_TEAM_10PT: TeaserOdds(130, 100, 100/130),
    }
    
    print("Comparing Odds Structures...")
    games = integration.create_sample_nfl_week(args.week)
    
    print(f"\n{'='*80}")
    print("STANDARD ODDS ANALYSIS")
    print(f"{'='*80}")
    standard_recs = analyzer.generate_teaser_recommendations(games, standard_odds)
    print_recommendation_summary(standard_recs, 5)
    
    print(f"\n{'='*80}")
    print("MAJOR BOOK ODDS ANALYSIS")
    print(f"{'='*80}")
    major_recs = analyzer.generate_teaser_recommendations(games, major_book_odds)
    print_recommendation_summary(major_recs, 5)
    
    # Calculate difference
    print(f"\n{'='*80}")
    print("ODDS COMPARISON SUMMARY")
    print(f"{'='*80}")
    
    for teaser_type in TeaserType:
        standard_odds_obj = standard_odds[teaser_type]
        major_odds_obj = major_book_odds[teaser_type]
        
        print(f"\n{teaser_type.value}:")
        print(f"  Standard: {standard_odds_obj.risk}/{standard_odds_obj.win} ({standard_odds_obj.american_odds:+d})")
        print(f"  Major Book: {major_odds_obj.risk}/{major_odds_obj.win} ({major_odds_obj.american_odds:+d})")
        
        # Find matching recommendations
        standard_rec = next((r for r in standard_recs if r.teaser_type == teaser_type), None)
        major_rec = next((r for r in major_recs if r.teaser_type == teaser_type), None)
        
        if standard_rec and major_rec:
            roi_diff = standard_rec.roi_percentage - major_rec.roi_percentage
            print(f"  ROI Difference: {roi_diff:+.1f}% (Standard advantage)")

def show_criteria_help():
    """Show Wong teaser criteria help"""
    print(f"\n{'='*80}")
    print("WONG TEASER CRITERIA GUIDE")
    print(f"{'='*80}")
    
    print("\nSTRICT WONG RULES (Highest Win Rates):")
    print("  Underdogs: +1.5 to +2.5 (tease to +7.5 to +8.5)")
    print("  Favorites: -7.5 to -8.5 (tease to -1.5 to -2.5)")
    print("  Historical Win Rate: ~75-78%")
    
    print("\nEXPANDED WONG RULES (More Games):")
    print("  Underdogs: +1.5 to +3.0 (tease to +7.5 to +9.0)")
    print("  Favorites: -7.5 to -9.0 (tease to -1.5 to -3.0)")
    print("  Historical Win Rate: ~73-75%")
    
    print("\nSWEETHEART 10-POINT RULES:")
    print("  Underdogs: +1.5 to +2.5 (tease to +11.5 to +12.5)")
    print("  Favorites: -10.0 to -10.5 (tease to PK to -0.5)")
    print("  Historical Win Rate: ~85-90%")
    
    print("\nOPTIMAL FILTERS (Higher Win Rates):")
    print("  • Home underdogs (+1.5 to +2.5)")
    print("  • Road favorites (-7.5 to -8.5)")
    print("  • Game totals under 44")
    print("  • Non-divisional games")
    print("  • Weeks 3-14 (avoid Week 1 and late season)")
    print("  • Avoid primetime games")
    
    print("\nBREAKEVEN WIN RATES:")
    print("  2-Team 6pt (-110): 72.4%")
    print("  3-Team 6pt (+160): 72.7%")
    print("  4-Team 6pt (+300): 73.2%")
    print("  3-Team 10pt (-120): 81.6%")

def main():
    parser = argparse.ArgumentParser(description="Wong Teaser Analysis Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Week analysis command
    week_parser = subparsers.add_parser('week', help='Analyze a specific NFL week')
    week_parser.add_argument('week', type=int, help='NFL week number')
    week_parser.add_argument('--source', choices=['sample', 'pinnacle', 'betbck'], 
                           default='sample', help='Data source')
    week_parser.add_argument('--detailed', action='store_true', 
                           help='Show detailed recommendations')
    week_parser.add_argument('--limit', type=int, default=10, 
                           help='Limit number of recommendations shown')
    week_parser.add_argument('--export', action='store_true', 
                           help='Export results to JSON file')
    
    # Custom odds command
    odds_parser = subparsers.add_parser('odds', help='Analyze with custom odds')
    odds_parser.add_argument('week', type=int, help='NFL week number')
    odds_parser.add_argument('--odds', nargs='+', required=True,
                           help='Custom odds in format: type:risk/win (e.g., 2_team_6pt:110/100)')
    odds_parser.add_argument('--source', choices=['sample', 'pinnacle', 'betbck'], 
                           default='sample', help='Data source')
    odds_parser.add_argument('--limit', type=int, default=10, 
                           help='Limit number of recommendations shown')
    
    # Compare odds command
    compare_parser = subparsers.add_parser('compare', help='Compare different odds structures')
    compare_parser.add_argument('week', type=int, help='NFL week number')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show Wong teaser criteria help')
    
    args = parser.parse_args()
    
    if args.command == 'week':
        analyze_week(args)
    elif args.command == 'odds':
        analyze_custom_odds(args)
    elif args.command == 'compare':
        compare_odds(args)
    elif args.command == 'help':
        show_criteria_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
