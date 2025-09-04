"""
Wong Teaser Data Integration Module

Integrates with existing betting system to fetch NFL game data and convert
to Wong teaser analyzer format. Works with Pinnacle, BetBCK, and other data sources.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from wong_teaser_analyzer import GameData, WongTeaserAnalyzer, TeaserRecommendation
from team_utils import normalize_team_name_for_matching

logger = logging.getLogger(__name__)

class WongDataIntegration:
    """Integrates Wong teaser analysis with existing betting data sources"""
    
    def __init__(self):
        self.analyzer = WongTeaserAnalyzer()
        
    def convert_pinnacle_to_game_data(self, pinnacle_data: Dict[str, Any]) -> Optional[GameData]:
        """
        Convert Pinnacle API data to GameData format
        
        Args:
            pinnacle_data: Raw Pinnacle API response
            
        Returns:
            GameData object or None if conversion fails
        """
        try:
            # Extract basic game info
            data = pinnacle_data.get('data', {})
            home_team = data.get('home', '')
            away_team = data.get('away', '')
            
            if not home_team or not away_team:
                logger.warning("Missing team names in Pinnacle data")
                return None
            
            # Extract spreads from full game period
            periods = data.get('periods', {})
            full_game = periods.get('num_0', {})
            spreads = full_game.get('spreads', {})
            
            home_spread = None
            away_spread = None
            
            # Find the main spread (usually the first one)
            for spread_data in spreads.values():
                if isinstance(spread_data, dict):
                    hdp = spread_data.get('hdp')
                    if hdp is not None:
                        # Pinnacle uses home team perspective
                        home_spread = float(hdp)
                        away_spread = -float(hdp)
                        break
            
            if home_spread is None:
                logger.warning(f"No spread data found for {home_team} vs {away_team}")
                return None
            
            # Extract totals
            totals = full_game.get('totals', {})
            game_total = None
            
            for total_data in totals.values():
                if isinstance(total_data, dict):
                    points = total_data.get('points')
                    if points is not None:
                        game_total = float(points)
                        break
            
            # Extract moneylines
            money_line = full_game.get('money_line', {})
            home_ml = None
            away_ml = None
            
            if isinstance(money_line, dict):
                home_ml = money_line.get('home')
                away_ml = money_line.get('away')
            
            # Extract game date/time
            game_date = data.get('starts')
            
            return GameData(
                home_team=home_team,
                away_team=away_team,
                home_spread=home_spread,
                away_spread=away_spread,
                total=game_total,
                home_moneyline=home_ml,
                away_moneyline=away_ml,
                game_date=game_date,
                week=None,  # Will need to be set separately
                is_divisional=False,  # Will need to be determined separately
                is_primetime=False   # Will need to be determined separately
            )
            
        except Exception as e:
            logger.error(f"Error converting Pinnacle data: {e}")
            return None
    
    def convert_betbck_to_game_data(self, betbck_data: Dict[str, Any]) -> Optional[GameData]:
        """
        Convert BetBCK scraper data to GameData format
        
        Args:
            betbck_data: Raw BetBCK scraper response
            
        Returns:
            GameData object or None if conversion fails
        """
        try:
            # Extract basic game info
            data = betbck_data.get('data', betbck_data)
            home_team = data.get('home_team', '')
            away_team = data.get('away_team', '')
            
            if not home_team or not away_team:
                logger.warning("Missing team names in BetBCK data")
                return None
            
            # Extract spreads
            home_spreads = data.get('home_spreads', [])
            away_spreads = data.get('away_spreads', [])
            
            home_spread = None
            away_spread = None
            
            # Get the main spread (usually the first one)
            if home_spreads:
                main_home_spread = home_spreads[0]
                home_spread = float(main_home_spread.get('line', 0))
            
            if away_spreads:
                main_away_spread = away_spreads[0]
                away_spread = float(main_away_spread.get('line', 0))
            
            if home_spread is None and away_spread is None:
                logger.warning(f"No spread data found for {home_team} vs {away_team}")
                return None
            
            # If we only have one spread, calculate the other
            if home_spread is None and away_spread is not None:
                home_spread = -away_spread
            elif away_spread is None and home_spread is not None:
                away_spread = -home_spread
            
            # Extract totals
            game_total = data.get('game_total_line')
            if game_total is not None:
                game_total = float(game_total)
            
            # Extract moneylines
            home_ml = data.get('home_moneyline_american')
            away_ml = data.get('away_moneyline_american')
            
            if home_ml:
                home_ml = int(home_ml)
            if away_ml:
                away_ml = int(away_ml)
            
            return GameData(
                home_team=home_team,
                away_team=away_team,
                home_spread=home_spread,
                away_spread=away_spread,
                total=game_total,
                home_moneyline=home_ml,
                away_moneyline=away_ml,
                game_date=None,  # BetBCK doesn't typically provide this
                week=None,
                is_divisional=False,
                is_primetime=False
            )
            
        except Exception as e:
            logger.error(f"Error converting BetBCK data: {e}")
            return None
    
    def load_nfl_schedule_data(self, schedule_file: str) -> Dict[str, Any]:
        """
        Load NFL schedule data to determine weeks, divisional games, etc.
        
        Args:
            schedule_file: Path to NFL schedule JSON file
            
        Returns:
            Dict with schedule information
        """
        try:
            with open(schedule_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading NFL schedule: {e}")
            return {}
    
    def enhance_game_data_with_schedule(self, game_data: GameData, 
                                      schedule_data: Dict[str, Any]) -> GameData:
        """
        Enhance GameData with schedule information (week, divisional, primetime)
        
        Args:
            game_data: Base game data
            schedule_data: NFL schedule information
            
        Returns:
            Enhanced GameData
        """
        # Find matching game in schedule
        home_normalized = normalize_team_name_for_matching(game_data.home_team)
        away_normalized = normalize_team_name_for_matching(game_data.away_team)
        
        for week_data in schedule_data.get('weeks', []):
            week_num = week_data.get('week')
            games = week_data.get('games', [])
            
            for game in games:
                schedule_home = normalize_team_name_for_matching(game.get('home_team', ''))
                schedule_away = normalize_team_name_for_matching(game.get('away_team', ''))
                
                # Check if this is our game
                if ((schedule_home == home_normalized and schedule_away == away_normalized) or
                    (schedule_home == away_normalized and schedule_away == home_normalized)):
                    
                    # Update game data with schedule info
                    game_data.week = week_num
                    game_data.is_divisional = game.get('is_divisional', False)
                    game_data.is_primetime = game.get('is_primetime', False)
                    game_data.game_date = game.get('game_date')
                    
                    return game_data
        
        return game_data
    
    def analyze_games_from_pinnacle(self, pinnacle_games: List[Dict[str, Any]], 
                                  schedule_data: Optional[Dict[str, Any]] = None) -> List[TeaserRecommendation]:
        """
        Analyze games from Pinnacle data source
        
        Args:
            pinnacle_games: List of Pinnacle API responses
            schedule_data: Optional NFL schedule data
            
        Returns:
            List of teaser recommendations
        """
        game_data_list = []
        
        for pinnacle_data in pinnacle_games:
            game_data = self.convert_pinnacle_to_game_data(pinnacle_data)
            if game_data:
                if schedule_data:
                    game_data = self.enhance_game_data_with_schedule(game_data, schedule_data)
                game_data_list.append(game_data)
        
        return self.analyzer.generate_teaser_recommendations(game_data_list)
    
    def analyze_games_from_betbck(self, betbck_games: List[Dict[str, Any]], 
                                schedule_data: Optional[Dict[str, Any]] = None) -> List[TeaserRecommendation]:
        """
        Analyze games from BetBCK data source
        
        Args:
            betbck_games: List of BetBCK scraper responses
            schedule_data: Optional NFL schedule data
            
        Returns:
            List of teaser recommendations
        """
        game_data_list = []
        
        for betbck_data in betbck_games:
            game_data = self.convert_betbck_to_game_data(betbck_data)
            if game_data:
                if schedule_data:
                    game_data = self.enhance_game_data_with_schedule(game_data, schedule_data)
                game_data_list.append(game_data)
        
        return self.analyzer.generate_teaser_recommendations(game_data_list)
    
    def create_sample_nfl_week(self, week: int = 1) -> List[GameData]:
        """
        Create sample NFL week data for testing
        
        Args:
            week: NFL week number
            
        Returns:
            List of sample GameData objects
        """
        # Sample Week 1 2025 games based on the conversation
        sample_games = [
            GameData(
                home_team="Houston Texans",
                away_team="Indianapolis Colts", 
                home_spread=-1.5,
                away_spread=1.5,
                total=44.5,
                week=week,
                is_divisional=True,
                is_primetime=False
            ),
            GameData(
                home_team="New York Giants",
                away_team="Minnesota Vikings",
                home_spread=-1.5,
                away_spread=1.5,
                total=42.0,
                week=week,
                is_divisional=False,
                is_primetime=False
            ),
            GameData(
                home_team="New England Patriots",
                away_team="Cincinnati Bengals",
                home_spread=8.5,
                away_spread=-8.5,
                total=41.5,
                week=week,
                is_divisional=False,
                is_primetime=False
            ),
            GameData(
                home_team="Buffalo Bills",
                away_team="Arizona Cardinals",
                home_spread=-7.0,
                away_spread=7.0,
                total=45.0,
                week=week,
                is_divisional=False,
                is_primetime=False
            ),
            GameData(
                home_team="Kansas City Chiefs",
                away_team="Baltimore Ravens",
                home_spread=-3.0,
                away_spread=3.0,
                total=48.5,
                week=week,
                is_divisional=False,
                is_primetime=True
            )
        ]
        
        return sample_games
    
    def get_weekly_analysis(self, week: int, data_source: str = "sample") -> Dict[str, Any]:
        """
        Get comprehensive weekly analysis
        
        Args:
            week: NFL week number
            data_source: "sample", "pinnacle", or "betbck"
            
        Returns:
            Weekly analysis results
        """
        if data_source == "sample":
            games = self.create_sample_nfl_week(week)
        else:
            # TODO: Implement actual data fetching
            games = []
        
        return self.analyzer.analyze_weekly_games(games, week)
    
    def export_weekly_report(self, week: int, output_file: Optional[str] = None) -> str:
        """
        Export comprehensive weekly report
        
        Args:
            week: NFL week number
            output_file: Optional output filename
            
        Returns:
            Path to exported file
        """
        analysis = self.get_weekly_analysis(week)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"wong_teaser_week_{week}_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        return output_file
