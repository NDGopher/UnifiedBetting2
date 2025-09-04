"""
Wong Teaser BetBCK Scraper

Scrapes NFL odds from BetBCK specifically for Wong teaser analysis.
Integrates with existing BetBCK scraping infrastructure.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from wong_teaser_analyzer import WongTeaserAnalyzer, GameData, TeaserType, TeaserOdds
from team_utils import normalize_team_name_for_matching

logger = logging.getLogger(__name__)

class WongTeaserBetBCKScraper:
    """Scraper for BetBCK NFL odds specifically for Wong teaser analysis"""
    
    def __init__(self):
        self.analyzer = WongTeaserAnalyzer()
        self.base_url = "https://betbck.com/Qubic/PlayerGameSelection.php"
        
        # Your book's odds configuration
        self.your_odds = {
            TeaserType.TWO_TEAM_6PT: TeaserOdds(110, 100, 100/110),  # -110
            TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 160, 160/100),  # +160
            TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 300, 300/100),  # +300
            TeaserType.THREE_TEAM_10PT: TeaserOdds(120, 100, 100/120),  # -120
        }
    
    def scrape_nfl_odds(self) -> List[Dict[str, Any]]:
        """
        Scrape NFL odds from BetBCK using the existing payload structure
        
        Returns:
            List of game data dictionaries
        """
        try:
            logger.info("🔧 Importing BetBCKAsyncScraper...")
            # Use the existing BetBCK async scraper to get NFL games
            from betbck_async_scraper import BetBCKAsyncScraper
            
            logger.info("🏈 Getting NFL games from BetBCK...")
            
            # Create BetBCK scraper instance
            betbck_scraper = BetBCKAsyncScraper()
            logger.info("✅ BetBCK scraper instance created")
            
            # Use the existing NFL payload
            payload = {
                'keyword_search': '',
                'inetWagerNumber': '0.12609183243816996',
                'inetSportSelection': 'sport',
                'contestType1': '',
                'contestType2': '',
                'contestType3': '',
                'correlatedID': '',
                'FOOTBALL_NFL_Game_': 'on'
            }
            
            # Run the scraper to get NFL games - handle event loop properly
            import asyncio
            try:
                # Check if we're already in an event loop
                loop = asyncio.get_running_loop()
                logger.info("🔄 Already in event loop, using run_in_executor...")
                # We're in an async context, need to use a different approach
                import concurrent.futures
                import threading
                
                def run_scraper():
                    # Create a new event loop in a separate thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self._scrape_nfl_games_async(betbck_scraper, payload))
                    finally:
                        new_loop.close()
                
                # Run in a separate thread to avoid event loop conflicts
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_scraper)
                    games = future.result(timeout=60)  # 60 second timeout
                    
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                logger.info("🔄 No event loop running, using asyncio.run...")
                games = asyncio.run(self._scrape_nfl_games_async(betbck_scraper, payload))
            
            logger.info(f"Successfully scraped {len(games)} NFL games")
            return games
            
        except Exception as e:
            logger.error(f"Error scraping BetBCK NFL odds: {e}")
            return []
    
    async def _scrape_nfl_games_async(self, betbck_scraper, payload) -> List[Dict[str, Any]]:
        """
        Async method to scrape NFL games using the existing BetBCK scraper
        """
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Login to BetBCK
                await betbck_scraper.login(session)
                
                # Get the selection page
                await betbck_scraper.fetch_selection_page(session)
                
                # Fetch NFL games
                html = await betbck_scraper.fetch_games_page(session, payload)
                
                # Parse the games
                games = betbck_scraper.parse_games(html)
                
                # Filter for NFL games only and clean team names
                nfl_games = []
                for game in games:
                    home_team = game.get('betbck_site_home_team', '')
                    away_team = game.get('betbck_site_away_team', '')
                    odds_data = game.get('betbck_site_odds', {})
                    
                    # Clean team names (remove numbers prefix)
                    if home_team and away_team:
                        # Remove numbers from team names (e.g., "451Dallas Cowboys" -> "Dallas Cowboys")
                        import re
                        home_team = re.sub(r'^\d+', '', home_team).strip()
                        away_team = re.sub(r'^\d+', '', away_team).strip()
                        
                        nfl_games.append({
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_spread': self._extract_main_spread(odds_data.get('site_top_team_spreads', [])),
                            'away_spread': self._extract_main_spread(odds_data.get('site_bottom_team_spreads', [])),
                            'total': odds_data.get('game_total_line'),
                            'home_moneyline': odds_data.get('site_top_team_moneyline_american'),
                            'away_moneyline': odds_data.get('site_bottom_team_moneyline_american'),
                            'scraped_at': datetime.now().isoformat()
                        })
                
                return nfl_games
                
        except Exception as e:
            logger.error(f"Error in async NFL scraping: {e}")
            return []
    
    def _extract_main_spread(self, spreads) -> Optional[float]:
        """Extract the main spread from a list of spreads"""
        if not spreads or len(spreads) == 0:
            return None
        
        # Get the first spread (usually the main one)
        main_spread = spreads[0]
        if isinstance(main_spread, dict):
            return main_spread.get('line')
        return main_spread
    
    def _parse_nfl_games(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse NFL games from BetBCK HTML
        
        Args:
            soup: BeautifulSoup object of the HTML response
            
        Returns:
            List of game data dictionaries
        """
        games = []
        
        try:
            # Look for game containers - adjust selectors based on BetBCK's HTML structure
            game_containers = soup.find_all('div', class_='game-container') or \
                            soup.find_all('tr', class_='game-row') or \
                            soup.find_all('div', class_='betting-line')
            
            for container in game_containers:
                game_data = self._extract_game_data(container)
                if game_data:
                    games.append(game_data)
            
            # If no specific containers found, try alternative parsing
            if not games:
                games = self._parse_alternative_structure(soup)
                
        except Exception as e:
            logger.error(f"Error parsing NFL games: {e}")
        
        return games
    
    def _extract_game_data(self, container) -> Optional[Dict[str, Any]]:
        """
        Extract game data from a single game container
        
        Args:
            container: BeautifulSoup element containing game data
            
        Returns:
            Game data dictionary or None
        """
        try:
            # Extract team names
            home_team = self._extract_team_name(container, 'home')
            away_team = self._extract_team_name(container, 'away')
            
            if not home_team or not away_team:
                return None
            
            # Extract spreads
            home_spread, away_spread = self._extract_spreads(container)
            
            # Extract totals
            game_total = self._extract_total(container)
            
            # Extract moneylines
            home_ml, away_ml = self._extract_moneylines(container)
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_spread': home_spread,
                'away_spread': away_spread,
                'total': game_total,
                'home_moneyline': home_ml,
                'away_moneyline': away_ml,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting game data: {e}")
            return None
    
    def _extract_team_name(self, container, team_type: str) -> Optional[str]:
        """Extract team name from container"""
        # Try multiple selectors for team names
        selectors = [
            f'.{team_type}-team',
            f'.team-{team_type}',
            f'[data-team="{team_type}"]',
            f'.{team_type}'
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_spreads(self, container) -> tuple:
        """Extract spread data from container"""
        # Try to find spread elements
        spread_elements = container.find_all(['span', 'div'], class_=lambda x: x and 'spread' in x.lower())
        
        home_spread = None
        away_spread = None
        
        for element in spread_elements:
            text = element.get_text(strip=True)
            try:
                spread_value = float(text.replace('+', '').replace('-', ''))
                if '-' in text:
                    spread_value = -spread_value
                
                # Determine if this is home or away spread based on context
                # This might need adjustment based on BetBCK's actual HTML structure
                if 'home' in element.get('class', []) or 'left' in element.get('class', []):
                    home_spread = spread_value
                else:
                    away_spread = spread_value
                    
            except ValueError:
                continue
        
        return home_spread, away_spread
    
    def _extract_total(self, container) -> Optional[float]:
        """Extract total from container"""
        total_elements = container.find_all(['span', 'div'], class_=lambda x: x and 'total' in x.lower())
        
        for element in total_elements:
            text = element.get_text(strip=True)
            try:
                return float(text)
            except ValueError:
                continue
        
        return None
    
    def _extract_moneylines(self, container) -> tuple:
        """Extract moneyline data from container"""
        ml_elements = container.find_all(['span', 'div'], class_=lambda x: x and 'moneyline' in x.lower())
        
        home_ml = None
        away_ml = None
        
        for element in ml_elements:
            text = element.get_text(strip=True)
            try:
                ml_value = int(text.replace('+', '').replace('-', ''))
                if '-' in text:
                    ml_value = -ml_value
                
                # Determine if this is home or away ML based on context
                if 'home' in element.get('class', []) or 'left' in element.get('class', []):
                    home_ml = ml_value
                else:
                    away_ml = ml_value
                    
            except ValueError:
                continue
        
        return home_ml, away_ml
    
    def _parse_alternative_structure(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Alternative parsing method if standard structure doesn't work
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of game data dictionaries
        """
        games = []
        
        try:
            # Look for any elements that might contain game data
            # This is a fallback method - adjust based on actual BetBCK structure
            potential_games = soup.find_all(['tr', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['game', 'match', 'line', 'bet']
            ))
            
            for element in potential_games:
                # Try to extract any recognizable game data
                text_content = element.get_text()
                
                # Look for patterns that might indicate NFL teams
                # This is a simplified approach - you might need to enhance this
                if any(keyword in text_content.lower() for keyword in ['vs', 'at', '@']):
                    game_data = self._extract_game_data(element)
                    if game_data:
                        games.append(game_data)
                        
        except Exception as e:
            logger.error(f"Error in alternative parsing: {e}")
        
        return games
    
    def convert_to_game_data(self, scraped_games: List[Dict[str, Any]]) -> List[GameData]:
        """
        Convert scraped game data to GameData objects
        
        Args:
            scraped_games: List of scraped game dictionaries
            
        Returns:
            List of GameData objects
        """
        game_data_list = []
        
        for game in scraped_games:
            try:
                # Determine week (you might want to add logic to determine this)
                week = self._determine_week(game)
                
                # Determine if divisional (you might want to add logic for this)
                is_divisional = self._is_divisional_game(game)
                
                # Determine if primetime (you might want to add logic for this)
                is_primetime = self._is_primetime_game(game)
                
                game_data = GameData(
                    home_team=game['home_team'],
                    away_team=game['away_team'],
                    home_spread=game.get('home_spread', 0),
                    away_spread=game.get('away_spread', 0),
                    total=game.get('total'),
                    home_moneyline=game.get('home_moneyline'),
                    away_moneyline=game.get('away_moneyline'),
                    week=week,
                    is_divisional=is_divisional,
                    is_primetime=is_primetime
                )
                
                game_data_list.append(game_data)
                
            except Exception as e:
                logger.error(f"Error converting game data: {e}")
                continue
        
        return game_data_list
    
    def _determine_week(self, game: Dict[str, Any]) -> int:
        """Determine NFL week from game data"""
        # You might want to implement logic to determine the current week
        # For now, return a default week
        return 1
    
    def _is_divisional_game(self, game: Dict[str, Any]) -> bool:
        """Determine if game is divisional"""
        # You might want to implement logic to check if teams are in same division
        # For now, return False
        return False
    
    def _is_primetime_game(self, game: Dict[str, Any]) -> bool:
        """Determine if game is primetime"""
        # You might want to implement logic to check game time
        # For now, return False
        return False
    
    def _create_sample_nfl_games(self) -> List[Dict[str, Any]]:
        """Create sample NFL games for testing when real scraping fails"""
        return [
            {
                'home_team': 'Houston Texans',
                'away_team': 'Indianapolis Colts',
                'home_spread': -1.5,
                'away_spread': 1.5,
                'total': 44.5,
                'home_moneyline': -110,
                'away_moneyline': -110,
                'scraped_at': datetime.now().isoformat()
            },
            {
                'home_team': 'New York Giants',
                'away_team': 'Minnesota Vikings',
                'home_spread': -1.5,
                'away_spread': 1.5,
                'total': 42.0,
                'home_moneyline': -110,
                'away_moneyline': -110,
                'scraped_at': datetime.now().isoformat()
            },
            {
                'home_team': 'New England Patriots',
                'away_team': 'Cincinnati Bengals',
                'home_spread': 8.5,
                'away_spread': -8.5,
                'total': 41.5,
                'home_moneyline': 300,
                'away_moneyline': -400,
                'scraped_at': datetime.now().isoformat()
            },
            {
                'home_team': 'Buffalo Bills',
                'away_team': 'Arizona Cardinals',
                'home_spread': -7.0,
                'away_spread': 7.0,
                'total': 45.0,
                'home_moneyline': -300,
                'away_moneyline': 250,
                'scraped_at': datetime.now().isoformat()
            },
            {
                'home_team': 'Kansas City Chiefs',
                'away_team': 'Baltimore Ravens',
                'home_spread': -3.0,
                'away_spread': 3.0,
                'total': 48.5,
                'home_moneyline': -150,
                'away_moneyline': 130,
                'scraped_at': datetime.now().isoformat()
            }
        ]
    
    def analyze_wong_teasers(self) -> Dict[str, Any]:
        """
        Main method to scrape NFL odds and analyze for Wong teasers
        
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info("🔍 Starting NFL odds scraping...")
            # Scrape NFL odds
            scraped_games = self.scrape_nfl_odds()
            logger.info(f"📊 Scraped {len(scraped_games)} games from BetBCK")
            
            # If no games found from scraping, return error
            if not scraped_games:
                logger.error("❌ No games found from BetBCK scraping")
                return {
                    'success': False,
                    'message': 'No NFL games found from BetBCK scraping',
                    'games': [],
                    'recommendations': []
                }
            
            # Convert to GameData objects
            game_data_list = self.convert_to_game_data(scraped_games)
            
            # Generate Wong teaser recommendations
            recommendations = self.analyzer.generate_teaser_recommendations(
                game_data_list, 
                self.your_odds
            )
            
            # Convert recommendations to serializable format
            serializable_recommendations = []
            for rec in recommendations:
                serializable_recommendations.append({
                    'teaser_type': rec.teaser_type.value,
                    'legs': [
                        {
                            'team': leg.team,
                            'original_spread': leg.original_spread,
                            'teased_spread': leg.teased_spread,
                            'is_home': leg.is_home,
                            'is_underdog': leg.is_underdog,
                            'leg_type': leg.leg_type,
                            'criteria_score': leg.criteria_score,
                            'win_rate_estimate': leg.win_rate_estimate,
                            'criteria_met': leg.criteria_met,
                            'optimal_filters': leg.optimal_filters
                        }
                        for leg in rec.legs
                    ],
                    'odds': {
                        'risk': rec.odds.risk,
                        'win': rec.odds.win,
                        'american_odds': rec.odds.american_odds
                    },
                    'expected_win_rate': rec.expected_win_rate,
                    'expected_value': rec.expected_value,
                    'roi_percentage': rec.roi_percentage,
                    'criteria_score': rec.criteria_score,
                    'total_criteria_met': rec.total_criteria_met,
                    'max_possible_criteria': rec.max_possible_criteria,
                    'confidence_level': rec.confidence_level,
                    'reasoning': rec.reasoning
                })
            
            return {
                'success': True,
                'message': f'Analyzed {len(game_data_list)} games, found {len(recommendations)} recommendations',
                'games': [
                    {
                        'home_team': game.home_team,
                        'away_team': game.away_team,
                        'home_spread': game.home_spread,
                        'away_spread': game.away_spread,
                        'total': game.total,
                        'week': game.week
                    }
                    for game in game_data_list
                ],
                'recommendations': serializable_recommendations,
                'summary': {
                    'total_games': len(game_data_list),
                    'total_recommendations': len(recommendations),
                    'top_recommendation': serializable_recommendations[0] if serializable_recommendations else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Wong teaser analysis: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'games': [],
                'recommendations': []
            }
