# Wong Teaser Analysis System

A comprehensive NFL teaser analysis system based on Stanford Wong's strategy from "Sharp Sports Betting". This system analyzes NFL games for optimal teaser opportunities, ranks them by multiple criteria, and provides betting recommendations with expected value calculations.

## Features

- **Multiple Teaser Types**: 2-team 6pt, 3-team 6pt, 4-team 6pt, and 3-team 10pt (sweetheart) teasers
- **Strict & Expanded Criteria**: Both original Wong rules and expanded ranges for more opportunities
- **Criteria-Based Ranking**: Ranks bets by how many optimal criteria they meet
- **EV Calculations**: Expected value and ROI calculations for different odds structures
- **Weekly Analysis**: Comprehensive weekly NFL analysis and recommendations
- **Custom Odds Support**: Analyze with your book's specific odds
- **Multiple Interfaces**: CLI, API, and integration with existing betting system

## Wong Teaser Rules

### Strict Wong Rules (Highest Win Rates)
- **Underdogs**: +1.5 to +2.5 (tease to +7.5 to +8.5)
- **Favorites**: -7.5 to -8.5 (tease to -1.5 to -2.5)
- **Historical Win Rate**: ~75-78%

### Expanded Wong Rules (More Games)
- **Underdogs**: +1.5 to +3.0 (tease to +7.5 to +9.0)
- **Favorites**: -7.5 to -9.0 (tease to -1.5 to -3.0)
- **Historical Win Rate**: ~73-75%

### Sweetheart 10-Point Rules
- **Underdogs**: +1.5 to +2.5 (tease to +11.5 to +12.5)
- **Favorites**: -10.0 to -10.5 (tease to PK to -0.5)
- **Historical Win Rate**: ~85-90%

### Optimal Filters (Higher Win Rates)
- Home underdogs (+1.5 to +2.5)
- Road favorites (-7.5 to -8.5)
- Game totals under 44
- Non-divisional games
- Weeks 3-14 (avoid Week 1 and late season)
- Avoid primetime games

## Installation

The system integrates with your existing betting infrastructure. No additional installation required.

## Usage

### Command Line Interface

```bash
# Analyze Week 1 with sample data
python wong_teaser_cli.py week 1 --detailed

# Analyze with custom odds
python wong_teaser_cli.py odds 1 --odds 2_team_6pt:110/100 3_team_6pt:100/160

# Compare different odds structures
python wong_teaser_cli.py compare 1

# Show criteria help
python wong_teaser_cli.py help
```

### API Endpoints

```python
# Add to your main.py FastAPI app
from wong_teaser_api import router
app.include_router(router)

# Available endpoints:
# GET /wong-teaser/criteria - Get Wong criteria information
# POST /wong-teaser/analyze-game - Analyze single game
# POST /wong-teaser/analyze-games - Analyze multiple games
# GET /wong-teaser/weekly-analysis/{week} - Get weekly analysis
# POST /wong-teaser/compare-odds - Compare odds structures
```

### Python Integration

```python
from wong_teaser_analyzer import WongTeaserAnalyzer, GameData, TeaserOdds, TeaserType
from wong_data_integration import WongDataIntegration

# Initialize
analyzer = WongTeaserAnalyzer()
integration = WongDataIntegration()

# Create sample games
games = integration.create_sample_nfl_week(1)

# Generate recommendations
recommendations = analyzer.generate_teaser_recommendations(games)

# Custom odds
custom_odds = {
    TeaserType.TWO_TEAM_6PT: TeaserOdds(110, 100, 100/110),  # -110
    TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 160, 160/100),  # +160
    TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 300, 300/100),  # +300
    TeaserType.THREE_TEAM_10PT: TeaserOdds(120, 100, 100/120),  # -120
}

custom_recommendations = analyzer.generate_teaser_recommendations(games, custom_odds)
```

## Your Book's Odds Analysis

Based on your conversation with Grok, your book offers:

- **2-Team 6pt**: -110 (Risk 110 to Win 100)
- **3-Team 6pt**: +160 (Risk 100 to Win 160)  
- **4-Team 6pt**: +300 (Risk 100 to Win 300)
- **3-Team 10pt**: -120 (Risk 120 to Win 100)

### Expected ROI by Type (Historical)

- **2-Team 6pt (-110)**: ~8.6% ROI
- **3-Team 6pt (+160)**: ~11.5% ROI
- **4-Team 6pt (+300)**: ~29.6% ROI (your +300 is better than typical +250)
- **3-Team 10pt (-120)**: ~16.6% ROI

### Recommended Strategy

1. **Prioritize 4-Team 6pt** when 4+ qualifiers available (highest ROI)
2. **Use 3-Team 10pt** when 3 sweetheart qualifiers available (consistent EV)
3. **Fall back to 3-Team 6pt** for 3 regular qualifiers
4. **Use 2-Team 6pt** as last resort (still +EV)

## Weekly Process

1. **Monitor Lines** (Tuesday-Friday): Check NFL spreads mid-week
2. **Wait for Closing Lines** (Saturday/Sunday): Confirm qualifiers with sharp lines
3. **Identify Qualifiers**: Use Wong criteria to find qualifying games
4. **Apply Filters**: Prioritize home dogs, road favs, low totals, non-divisional
5. **Generate Recommendations**: Rank by criteria score and EV
6. **Place Bets**: Use recommended bankroll allocation (1-2% per teaser)

## Bankroll Management

- **2-Team**: 2% of bankroll
- **3-Team**: 1.5% of bankroll  
- **4-Team**: 1% of bankroll (higher variance)

## Integration with Existing System

The system integrates with your existing:
- Pinnacle odds fetching
- BetBCK scraping
- Team name normalization
- EV calculation infrastructure

## Testing

```bash
# Run test script
python test_wong_teaser.py

# This will demonstrate:
# - Individual game analysis
# - Recommendation generation
# - Custom odds analysis
# - Weekly analysis
# - Odds comparison
```

## Files

- `wong_teaser_analyzer.py` - Core analysis engine
- `wong_data_integration.py` - Data integration with existing system
- `wong_teaser_cli.py` - Command line interface
- `wong_teaser_api.py` - FastAPI endpoints
- `test_wong_teaser.py` - Test and demonstration script

## Historical Performance

Based on Grok's analysis using Pinnacle closing spreads:

- **2018**: 17.9% ROI (2-team)
- **2019**: 6.6% ROI
- **2020**: 27.5% ROI
- **2021**: 23.8% ROI
- **2022**: 3.9% ROI
- **Long-term Average**: ~9.8% ROI

Your -110 odds provide significant advantage over major books at -135.

## Support

The system is designed to work with your existing betting infrastructure. All components are modular and can be customized for your specific needs.
