"""
Wong Teaser Analyzer - Comprehensive NFL Teaser Analysis System

Based on Stanford Wong's teaser strategy from "Sharp Sports Betting"
Analyzes NFL games for optimal teaser opportunities with multiple criteria ranking.

Key Features:
- Strict and expanded Wong criteria checking
- Multiple teaser type support (2-team 6pt, 3-team 6pt, 4-team 6pt, 3-team 10pt)
- EV calculations for different odds structures
- Criteria-based ranking system
- Weekly NFL analysis and recommendations
"""

import math
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class TeaserType(Enum):
    TWO_TEAM_6PT = "2_team_6pt"
    THREE_TEAM_6PT = "3_team_6pt" 
    FOUR_TEAM_6PT = "4_team_6pt"
    THREE_TEAM_10PT = "3_team_10pt"

class CriteriaType(Enum):
    STRICT = "strict"
    EXPANDED = "expanded"

@dataclass
class TeaserOdds:
    """Teaser odds configuration"""
    risk: int  # Amount risked
    win: int   # Amount won if successful
    payout_ratio: float  # win/risk ratio
    
    @property
    def american_odds(self) -> int:
        """Convert to American odds format"""
        # For negative odds (risk > win), calculate as negative
        if self.risk > self.win:
            return int(-100 * self.risk / self.win)
        else:
            return int(100 * self.win / self.risk)

@dataclass
class GameData:
    """NFL game data structure"""
    home_team: str
    away_team: str
    home_spread: float
    away_spread: float
    total: Optional[float] = None
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None
    game_date: Optional[str] = None
    week: Optional[int] = None
    is_divisional: bool = False
    is_primetime: bool = False

@dataclass
class TeaserLeg:
    """Individual teaser leg"""
    team: str
    original_spread: float
    teased_spread: float
    is_home: bool
    is_underdog: bool
    leg_type: str  # "underdog" or "favorite"
    criteria_score: int  # How many criteria this leg meets
    win_rate_estimate: float  # Historical win rate for this type of leg
    criteria_met: List[str] = None  # List of criteria this leg meets
    optimal_filters: List[str] = None  # List of optimal filters this leg meets
    
    def __post_init__(self):
        if self.criteria_met is None:
            self.criteria_met = []
        if self.optimal_filters is None:
            self.optimal_filters = []

@dataclass
class TeaserRecommendation:
    """Complete teaser recommendation"""
    legs: List[TeaserLeg]
    teaser_type: TeaserType
    odds: TeaserOdds
    expected_win_rate: float
    expected_value: float
    roi_percentage: float
    criteria_score: int
    total_criteria_met: int
    max_possible_criteria: int
    confidence_level: str  # "High", "Medium", "Low"
    reasoning: List[str]

class WongTeaserAnalyzer:
    """Main Wong teaser analysis engine"""
    
    def __init__(self):
        # Historical win rates based on Grok's analysis
        self.historical_win_rates = {
            "strict_6pt_underdog": 0.758,  # +1.5 to +2.5
            "strict_6pt_favorite": 0.789,  # -7.5 to -8.5
            "expanded_6pt_underdog": 0.752,  # +1.5 to +3
            "expanded_6pt_favorite": 0.765,  # -7.5 to -9
            "strict_10pt_underdog": 0.869,  # +1.5 to +2.5
            "strict_10pt_favorite": 0.911,  # -10 to -10.5
        }
        
        # Breakeven win rates for different teaser types
        self.breakeven_rates = {
            TeaserType.TWO_TEAM_6PT: 0.724,
            TeaserType.THREE_TEAM_6PT: 0.727,
            TeaserType.FOUR_TEAM_6PT: 0.732,
            TeaserType.THREE_TEAM_10PT: 0.806,
        }
        
        # Default odds configurations
        self.default_odds = {
            TeaserType.TWO_TEAM_6PT: TeaserOdds(110, 100, 100/110),
            TeaserType.THREE_TEAM_6PT: TeaserOdds(100, 160, 160/100),
            TeaserType.FOUR_TEAM_6PT: TeaserOdds(100, 300, 300/100),
            TeaserType.THREE_TEAM_10PT: TeaserOdds(120, 100, 100/120),
        }
        
        # Criteria weights for ranking
        self.criteria_weights = {
            "exact_spread": 10,      # Perfect Wong spread
            "home_underdog": 8,      # Home dog advantage
            "road_favorite": 8,      # Road favorite advantage
            "low_total": 6,          # Total under 44
            "non_divisional": 4,     # Non-divisional game
            "mid_season": 3,         # Weeks 3-14
            "avoid_primetime": 2,    # Avoid primetime games
            "spread_range": 5,       # Within optimal range
        }

    def check_wong_criteria(self, game: GameData, criteria_type: CriteriaType = CriteriaType.STRICT) -> Dict[str, Any]:
        """
        Check if a game meets Wong teaser criteria
        
        Returns dict with:
        - qualifies: bool
        - underdog_leg: optional TeaserLeg
        - favorite_leg: optional TeaserLeg
        - criteria_met: list of criteria
        - criteria_score: int
        """
        result = {
            "qualifies": False,
            "underdog_leg": None,
            "favorite_leg": None,
            "criteria_met": [],
            "criteria_score": 0,
            "reasoning": []
        }
        
        # Check underdog criteria
        underdog_leg = self._check_underdog_criteria(game, criteria_type)
        if underdog_leg:
            result["underdog_leg"] = underdog_leg
            result["criteria_met"].extend(underdog_leg.criteria_met)
            result["criteria_score"] += underdog_leg.criteria_score
            
        # Check favorite criteria  
        favorite_leg = self._check_favorite_criteria(game, criteria_type)
        if favorite_leg:
            result["favorite_leg"] = favorite_leg
            result["criteria_met"].extend(favorite_leg.criteria_met)
            result["criteria_score"] += favorite_leg.criteria_score
            
        # Game qualifies if it has at least one qualifying leg
        result["qualifies"] = bool(underdog_leg or favorite_leg)
        
        return result

    def _check_underdog_criteria(self, game: GameData, criteria_type: CriteriaType) -> Optional[TeaserLeg]:
        """Check if underdog side qualifies for Wong teaser"""
        criteria_met = []
        criteria_score = 0
        
        # Check spread ranges
        if criteria_type == CriteriaType.STRICT:
            # Strict: +1.5 to +2.5
            if 1.5 <= game.away_spread <= 2.5:
                criteria_met.append("exact_spread")
                criteria_score += self.criteria_weights["exact_spread"]
            elif 1.5 <= game.home_spread <= 2.5:
                criteria_met.append("exact_spread")
                criteria_score += self.criteria_weights["exact_spread"]
            else:
                return None
        else:
            # Expanded: +1.5 to +3
            if 1.5 <= game.away_spread <= 3.0:
                criteria_met.append("spread_range")
                criteria_score += self.criteria_weights["spread_range"]
            elif 1.5 <= game.home_spread <= 3.0:
                criteria_met.append("spread_range")
                criteria_score += self.criteria_weights["spread_range"]
            else:
                return None
        
        # Determine which team is the underdog
        if game.away_spread > 0:  # Away team is underdog
            team = game.away_team
            original_spread = game.away_spread
            teased_spread = game.away_spread + 6
            is_home = False
        else:  # Home team is underdog
            team = game.home_team
            original_spread = game.home_spread
            teased_spread = game.home_spread + 6
            is_home = True
            
        # Additional criteria
        if is_home:
            criteria_met.append("home_underdog")
            criteria_score += self.criteria_weights["home_underdog"]
            
        if game.total and game.total < 44:
            criteria_met.append("low_total")
            criteria_score += self.criteria_weights["low_total"]
            
        if not game.is_divisional:
            criteria_met.append("non_divisional")
            criteria_score += self.criteria_weights["non_divisional"]
            
        if game.week and 3 <= game.week <= 14:
            criteria_met.append("mid_season")
            criteria_score += self.criteria_weights["mid_season"]
            
        if not game.is_primetime:
            criteria_met.append("avoid_primetime")
            criteria_score += self.criteria_weights["avoid_primetime"]
        
        # Get historical win rate
        win_rate_key = f"{criteria_type.value}_6pt_underdog"
        win_rate = self.historical_win_rates.get(win_rate_key, 0.75)
        
        return TeaserLeg(
            team=team,
            original_spread=original_spread,
            teased_spread=teased_spread,
            is_home=is_home,
            is_underdog=True,
            leg_type="underdog",
            criteria_score=criteria_score,
            win_rate_estimate=win_rate,
            criteria_met=criteria_met
        )

    def _check_favorite_criteria(self, game: GameData, criteria_type: CriteriaType) -> Optional[TeaserLeg]:
        """Check if favorite side qualifies for Wong teaser"""
        criteria_met = []
        criteria_score = 0
        
        # Check spread ranges
        if criteria_type == CriteriaType.STRICT:
            # Strict: -7.5 to -8.5
            if -8.5 <= game.away_spread <= -7.5:
                criteria_met.append("exact_spread")
                criteria_score += self.criteria_weights["exact_spread"]
            elif -8.5 <= game.home_spread <= -7.5:
                criteria_met.append("exact_spread")
                criteria_score += self.criteria_weights["exact_spread"]
            else:
                return None
        else:
            # Expanded: -7.5 to -9
            if -9.0 <= game.away_spread <= -7.5:
                criteria_met.append("spread_range")
                criteria_score += self.criteria_weights["spread_range"]
            elif -9.0 <= game.home_spread <= -7.5:
                criteria_met.append("spread_range")
                criteria_score += self.criteria_weights["spread_range"]
            else:
                return None
        
        # Determine which team is the favorite
        if game.away_spread < 0:  # Away team is favorite
            team = game.away_team
            original_spread = game.away_spread
            teased_spread = game.away_spread + 6
            is_home = False
        else:  # Home team is favorite
            team = game.home_team
            original_spread = game.home_spread
            teased_spread = game.home_spread + 6
            is_home = True
            
        # Additional criteria
        if not is_home:  # Road favorite
            criteria_met.append("road_favorite")
            criteria_score += self.criteria_weights["road_favorite"]
            
        if game.total and game.total < 44:
            criteria_met.append("low_total")
            criteria_score += self.criteria_weights["low_total"]
            
        if not game.is_divisional:
            criteria_met.append("non_divisional")
            criteria_score += self.criteria_weights["non_divisional"]
            
        if game.week and 3 <= game.week <= 14:
            criteria_met.append("mid_season")
            criteria_score += self.criteria_weights["mid_season"]
            
        if not game.is_primetime:
            criteria_met.append("avoid_primetime")
            criteria_score += self.criteria_weights["avoid_primetime"]
        
        # Get historical win rate
        win_rate_key = f"{criteria_type.value}_6pt_favorite"
        win_rate = self.historical_win_rates.get(win_rate_key, 0.75)
        
        return TeaserLeg(
            team=team,
            original_spread=original_spread,
            teased_spread=teased_spread,
            is_home=is_home,
            is_underdog=False,
            leg_type="favorite",
            criteria_score=criteria_score,
            win_rate_estimate=win_rate,
            criteria_met=criteria_met
        )

    def check_sweetheart_criteria(self, game: GameData) -> Dict[str, Any]:
        """Check if game qualifies for 10-point sweetheart teaser"""
        result = {
            "qualifies": False,
            "underdog_leg": None,
            "favorite_leg": None,
            "criteria_met": [],
            "criteria_score": 0,
            "reasoning": []
        }
        
        # Check underdog criteria (strict: +1.5 to +2.5 only)
        if 1.5 <= game.away_spread <= 2.5:
            criteria_met = ["exact_spread"]
            criteria_score = self.criteria_weights["exact_spread"]
            
            if game.total and game.total < 45:
                criteria_met.append("low_total")
                criteria_score += self.criteria_weights["low_total"]
                
            result["underdog_leg"] = TeaserLeg(
                team=game.away_team,
                original_spread=game.away_spread,
                teased_spread=game.away_spread + 10,
                is_home=False,
                is_underdog=True,
                leg_type="underdog",
                criteria_score=criteria_score,
                win_rate_estimate=self.historical_win_rates["strict_10pt_underdog"],
                criteria_met=criteria_met
            )
            
        elif 1.5 <= game.home_spread <= 2.5:
            criteria_met = ["exact_spread", "home_underdog"]
            criteria_score = self.criteria_weights["exact_spread"] + self.criteria_weights["home_underdog"]
            
            if game.total and game.total < 45:
                criteria_met.append("low_total")
                criteria_score += self.criteria_weights["low_total"]
                
            result["underdog_leg"] = TeaserLeg(
                team=game.home_team,
                original_spread=game.home_spread,
                teased_spread=game.home_spread + 10,
                is_home=True,
                is_underdog=True,
                leg_type="underdog",
                criteria_score=criteria_score,
                win_rate_estimate=self.historical_win_rates["strict_10pt_underdog"],
                criteria_met=criteria_met
            )
        
        # Check favorite criteria (strict: -10 to -10.5 only)
        if -10.5 <= game.away_spread <= -10.0:
            criteria_met = ["exact_spread", "road_favorite"]
            criteria_score = self.criteria_weights["exact_spread"] + self.criteria_weights["road_favorite"]
            
            if game.total and game.total < 45:
                criteria_met.append("low_total")
                criteria_score += self.criteria_weights["low_total"]
                
            result["favorite_leg"] = TeaserLeg(
                team=game.away_team,
                original_spread=game.away_spread,
                teased_spread=game.away_spread + 10,
                is_home=False,
                is_underdog=False,
                leg_type="favorite",
                criteria_score=criteria_score,
                win_rate_estimate=self.historical_win_rates["strict_10pt_favorite"],
                criteria_met=criteria_met
            )
            
        elif -10.5 <= game.home_spread <= -10.0:
            criteria_met = ["exact_spread"]
            criteria_score = self.criteria_weights["exact_spread"]
            
            if game.total and game.total < 45:
                criteria_met.append("low_total")
                criteria_score += self.criteria_weights["low_total"]
                
            result["favorite_leg"] = TeaserLeg(
                team=game.home_team,
                original_spread=game.home_spread,
                teased_spread=game.home_spread + 10,
                is_home=True,
                is_underdog=False,
                leg_type="favorite",
                criteria_score=criteria_score,
                win_rate_estimate=self.historical_win_rates["strict_10pt_favorite"],
                criteria_met=criteria_met
            )
        
        # Game qualifies if it has at least one qualifying leg
        result["qualifies"] = bool(result["underdog_leg"] or result["favorite_leg"])
        result["criteria_met"] = []
        result["criteria_score"] = 0
        
        if result["underdog_leg"]:
            result["criteria_met"].extend(result["underdog_leg"].criteria_met)
            result["criteria_score"] += result["underdog_leg"].criteria_score
            
        if result["favorite_leg"]:
            result["criteria_met"].extend(result["favorite_leg"].criteria_met)
            result["criteria_score"] += result["favorite_leg"].criteria_score
        
        return result

    def calculate_teaser_ev(self, legs: List[TeaserLeg], teaser_type: TeaserType, 
                          odds: Optional[TeaserOdds] = None) -> Dict[str, float]:
        """
        Calculate expected value for a teaser
        
        Returns dict with:
        - expected_win_rate: float
        - expected_value: float  
        - roi_percentage: float
        - breakeven_rate: float
        """
        if not legs:
            return {"expected_win_rate": 0, "expected_value": 0, "roi_percentage": 0, "breakeven_rate": 0}
        
        # Use default odds if not provided
        if odds is None:
            odds = self.default_odds[teaser_type]
        
        # Calculate expected win rate (assuming independence)
        expected_win_rate = 1.0
        for leg in legs:
            expected_win_rate *= leg.win_rate_estimate
        
        # Calculate expected value
        payout = odds.win
        risk = odds.risk
        expected_value = (expected_win_rate * payout) - risk
        
        # Calculate ROI percentage
        roi_percentage = (expected_value / risk) * 100
        
        # Get breakeven rate
        breakeven_rate = self.breakeven_rates[teaser_type]
        
        return {
            "expected_win_rate": expected_win_rate,
            "expected_value": expected_value,
            "roi_percentage": roi_percentage,
            "breakeven_rate": breakeven_rate
        }

    def generate_teaser_recommendations(self, games: List[GameData], 
                                      custom_odds: Optional[Dict[TeaserType, TeaserOdds]] = None) -> List[TeaserRecommendation]:
        """
        Generate ranked teaser recommendations for a list of games
        
        Returns list of TeaserRecommendation objects ranked by optimal filters and EV
        """
        recommendations = []
        
        # Use custom odds if provided, otherwise use defaults
        odds_config = custom_odds if custom_odds else self.default_odds
        
        # Find all qualifying legs
        qualifying_legs = []
        
        for game in games:
            # Check 6-point criteria (both strict and expanded)
            strict_result = self.check_wong_criteria(game, CriteriaType.STRICT)
            expanded_result = self.check_wong_criteria(game, CriteriaType.EXPANDED)
            
            # Check 10-point criteria
            sweetheart_result = self.check_sweetheart_criteria(game)
            
            # Add qualifying legs
            for result in [strict_result, expanded_result, sweetheart_result]:
                if result["underdog_leg"]:
                    qualifying_legs.append((result["underdog_leg"], "6pt" if result != sweetheart_result else "10pt"))
                if result["favorite_leg"]:
                    qualifying_legs.append((result["favorite_leg"], "6pt" if result != sweetheart_result else "10pt"))
        
        # Generate all possible teaser combinations
        for teaser_type in TeaserType:
            if teaser_type == TeaserType.THREE_TEAM_10PT:
                # Only use 10-point legs for sweetheart teasers
                available_legs = [leg for leg, leg_type in qualifying_legs if leg_type == "10pt"]
            else:
                # Use 6-point legs for regular teasers
                available_legs = [leg for leg, leg_type in qualifying_legs if leg_type == "6pt"]
            
            # Generate combinations based on teaser type
            if teaser_type == TeaserType.TWO_TEAM_6PT and len(available_legs) >= 2:
                combinations = self._generate_balanced_combinations(available_legs, 2)
            elif teaser_type == TeaserType.THREE_TEAM_6PT and len(available_legs) >= 3:
                combinations = self._generate_balanced_combinations(available_legs, 3)
            elif teaser_type == TeaserType.FOUR_TEAM_6PT and len(available_legs) >= 4:
                combinations = self._generate_balanced_combinations(available_legs, 4)
            elif teaser_type == TeaserType.THREE_TEAM_10PT and len(available_legs) >= 3:
                combinations = self._generate_balanced_combinations(available_legs, 3)
            else:
                continue
            
            # Create recommendations for each combination
            for legs in combinations:
                # Calculate optimal filters score
                optimal_filters_score = self._calculate_optimal_filters_score(legs)
                
                # Calculate total criteria score
                total_criteria_score = sum(leg.criteria_score for leg in legs)
                
                # Ranking score based purely on Wong criteria and optimal filters
                ranking_score = (optimal_filters_score * 10) + (total_criteria_score * 0.5)
                
                # Determine confidence level based on optimal filters only
                if optimal_filters_score >= 5:
                    confidence = "High"
                elif optimal_filters_score >= 3:
                    confidence = "Medium"
                else:
                    confidence = "Low"
                
                # Generate reasoning based on Wong criteria only
                reasoning = self._generate_wong_reasoning(legs, optimal_filters_score)
                
                # Create mock EV data (since we're not using it)
                mock_ev_data = {
                    "expected_win_rate": 0.75,  # Placeholder
                    "expected_value": 0,        # Placeholder
                    "roi_percentage": 0,        # Placeholder
                }
                
                recommendation = TeaserRecommendation(
                    legs=legs,
                    teaser_type=teaser_type,
                    odds=odds_config[teaser_type],
                    expected_win_rate=mock_ev_data["expected_win_rate"],
                    expected_value=mock_ev_data["expected_value"],
                    roi_percentage=mock_ev_data["roi_percentage"],
                    criteria_score=ranking_score,
                    total_criteria_met=optimal_filters_score,
                    max_possible_criteria=6,
                    confidence_level=confidence,
                    reasoning=reasoning
                )
                
                recommendations.append(recommendation)
        
        # Sort by ranking score (optimal filters first, then ROI)
        recommendations.sort(key=lambda x: x.criteria_score, reverse=True)
        
        return recommendations

    def _generate_balanced_combinations(self, legs: List[TeaserLeg], size: int) -> List[List[TeaserLeg]]:
        """Generate balanced combinations to avoid overexposure to one team type"""
        from itertools import combinations
        
        # Separate legs by type
        underdog_legs = [leg for leg in legs if leg.is_underdog]
        favorite_legs = [leg for leg in legs if not leg.is_underdog]
        
        # Sort by criteria score (best legs first)
        underdog_legs.sort(key=lambda x: x.criteria_score, reverse=True)
        favorite_legs.sort(key=lambda x: x.criteria_score, reverse=True)
        
        combinations_list = []
        
        if size == 2:
            # For 2-team teasers, prefer 1 underdog + 1 favorite
            for underdog in underdog_legs[:3]:  # Top 3 underdogs
                for favorite in favorite_legs[:3]:  # Top 3 favorites
                    combinations_list.append([underdog, favorite])
            
            # Also include some same-type combinations if they're very strong
            for i, leg1 in enumerate(legs[:4]):
                for leg2 in legs[i+1:4]:
                    if leg1.team != leg2.team:  # Different teams
                        combinations_list.append([leg1, leg2])
        
        elif size == 3:
            # For 3-team teasers, prefer 2 underdogs + 1 favorite or 1 underdog + 2 favorites
            for underdog1 in underdog_legs[:2]:
                for underdog2 in underdog_legs[:2]:
                    if underdog1.team != underdog2.team:
                        for favorite in favorite_legs[:2]:
                            combinations_list.append([underdog1, underdog2, favorite])
            
            for underdog in underdog_legs[:2]:
                for favorite1 in favorite_legs[:2]:
                    for favorite2 in favorite_legs[:2]:
                        if favorite1.team != favorite2.team:
                            combinations_list.append([underdog, favorite1, favorite2])
        
        elif size == 4:
            # For 4-team teasers, prefer 2 underdogs + 2 favorites
            for underdog1 in underdog_legs[:2]:
                for underdog2 in underdog_legs[:2]:
                    if underdog1.team != underdog2.team:
                        for favorite1 in favorite_legs[:2]:
                            for favorite2 in favorite_legs[:2]:
                                if favorite1.team != favorite2.team:
                                    combinations_list.append([underdog1, underdog2, favorite1, favorite2])
        
        # Remove duplicates and limit to reasonable number
        unique_combinations = []
        seen = set()
        for combo in combinations_list:
            combo_key = tuple(sorted(leg.team for leg in combo))
            if combo_key not in seen:
                seen.add(combo_key)
                unique_combinations.append(combo)
                if len(unique_combinations) >= 10:  # Limit combinations
                    break
        
        return unique_combinations

    def _calculate_optimal_filters_score(self, legs: List[TeaserLeg]) -> int:
        """Calculate how many unique optimal filters this combination meets"""
        optimal_filters = set()
        
        # Collect all unique optimal filters across all legs
        for leg in legs:
            for criteria in leg.criteria_met:
                if criteria in ["exact_spread", "home_underdog", "road_favorite", "low_total", "non_divisional", "mid_season"]:
                    optimal_filters.add(criteria)
        
        # Store optimal filters in the legs for display
        for leg in legs:
            leg.optimal_filters = list(optimal_filters)
        
        return len(optimal_filters)

    def _generate_wong_reasoning(self, legs: List[TeaserLeg], optimal_filters_score: int) -> List[str]:
        """Generate reasoning based on Wong criteria and optimal filters only"""
        reasoning = []
        
        # Optimal filters reasoning
        if optimal_filters_score >= 5:
            reasoning.append(f"🌟 EXCELLENT: {optimal_filters_score}/6 optimal filters met")
        elif optimal_filters_score >= 3:
            reasoning.append(f"✅ GOOD: {optimal_filters_score}/6 optimal filters met")
        else:
            reasoning.append(f"⚠️ BASIC: {optimal_filters_score}/6 optimal filters met")
        
        # Wong criteria reasoning
        perfect_spreads = sum(1 for leg in legs if "exact_spread" in leg.criteria_met)
        if perfect_spreads > 0:
            reasoning.append(f"Perfect Wong spreads: {perfect_spreads}/{len(legs)} legs")
        
        home_dogs = sum(1 for leg in legs if "home_underdog" in leg.criteria_met)
        if home_dogs > 0:
            reasoning.append(f"Home underdog advantage: {home_dogs} legs")
        
        road_favs = sum(1 for leg in legs if "road_favorite" in leg.criteria_met)
        if road_favs > 0:
            reasoning.append(f"Road favorite advantage: {road_favs} legs")
        
        low_totals = sum(1 for leg in legs if "low_total" in leg.criteria_met)
        if low_totals > 0:
            reasoning.append(f"Low total games: {low_totals} legs")
        
        # Balance reasoning
        underdog_count = sum(1 for leg in legs if leg.is_underdog)
        favorite_count = len(legs) - underdog_count
        
        if underdog_count == favorite_count:
            reasoning.append("Perfect balance: Equal underdogs and favorites")
        elif abs(underdog_count - favorite_count) == 1:
            reasoning.append("Good balance: Slightly more of one type")
        else:
            reasoning.append("Imbalanced: Heavy on one type (higher variance)")
        
        
        return reasoning

    def _generate_reasoning(self, legs: List[TeaserLeg], ev_data: Dict[str, float], 
                          criteria_score: int) -> List[str]:
        """Generate reasoning for why this teaser is recommended"""
        reasoning = []
        
        # EV reasoning
        if ev_data["roi_percentage"] > 15:
            reasoning.append(f"Excellent EV: {ev_data['roi_percentage']:.1f}% ROI")
        elif ev_data["roi_percentage"] > 5:
            reasoning.append(f"Good EV: {ev_data['roi_percentage']:.1f}% ROI")
        else:
            reasoning.append(f"Moderate EV: {ev_data['roi_percentage']:.1f}% ROI")
        
        # Criteria reasoning
        if criteria_score > 20:
            reasoning.append(f"Strong criteria match: {criteria_score} points")
        elif criteria_score > 10:
            reasoning.append(f"Good criteria match: {criteria_score} points")
        else:
            reasoning.append(f"Basic criteria match: {criteria_score} points")
        
        # Leg-specific reasoning
        for leg in legs:
            if "exact_spread" in leg.criteria_met:
                reasoning.append(f"{leg.team}: Perfect Wong spread ({leg.original_spread})")
            elif "home_underdog" in leg.criteria_met:
                reasoning.append(f"{leg.team}: Home underdog advantage")
            elif "road_favorite" in leg.criteria_met:
                reasoning.append(f"{leg.team}: Road favorite advantage")
        
        return reasoning

    def analyze_weekly_games(self, games: List[GameData], week: int) -> Dict[str, Any]:
        """
        Analyze all games for a given week and provide comprehensive recommendations
        
        Returns dict with:
        - week: int
        - total_games: int
        - qualifying_games: int
        - recommendations: List[TeaserRecommendation]
        - summary: Dict with key statistics
        """
        # Generate recommendations
        recommendations = self.generate_teaser_recommendations(games)
        
        # Calculate summary statistics
        qualifying_games = len(set(leg.team for rec in recommendations for leg in rec.legs))
        
        # Group by teaser type
        by_type = {}
        for rec in recommendations:
            teaser_type = rec.teaser_type.value
            if teaser_type not in by_type:
                by_type[teaser_type] = []
            by_type[teaser_type].append(rec)
        
        # Calculate average EV by type
        avg_ev_by_type = {}
        for teaser_type, recs in by_type.items():
            if recs:
                avg_ev_by_type[teaser_type] = sum(r.roi_percentage for r in recs) / len(recs)
        
        summary = {
            "total_games": len(games),
            "qualifying_games": qualifying_games,
            "total_recommendations": len(recommendations),
            "recommendations_by_type": {k: len(v) for k, v in by_type.items()},
            "average_ev_by_type": avg_ev_by_type,
            "top_recommendation": recommendations[0] if recommendations else None
        }
        
        return {
            "week": week,
            "total_games": len(games),
            "qualifying_games": qualifying_games,
            "recommendations": recommendations,
            "summary": summary
        }

    def export_recommendations(self, recommendations: List[TeaserRecommendation], 
                             filename: Optional[str] = None) -> str:
        """Export recommendations to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wong_teaser_recommendations_{timestamp}.json"
        
        # Convert recommendations to serializable format
        export_data = []
        for rec in recommendations:
            export_data.append({
                "teaser_type": rec.teaser_type.value,
                "legs": [
                    {
                        "team": leg.team,
                        "original_spread": leg.original_spread,
                        "teased_spread": leg.teased_spread,
                        "is_home": leg.is_home,
                        "is_underdog": leg.is_underdog,
                        "criteria_score": leg.criteria_score,
                        "win_rate_estimate": leg.win_rate_estimate,
                        "criteria_met": leg.criteria_met
                    }
                    for leg in rec.legs
                ],
                "odds": {
                    "risk": rec.odds.risk,
                    "win": rec.odds.win,
                    "american_odds": rec.odds.american_odds
                },
                "expected_win_rate": rec.expected_win_rate,
                "expected_value": rec.expected_value,
                "roi_percentage": rec.roi_percentage,
                "criteria_score": rec.criteria_score,
                "confidence_level": rec.confidence_level,
                "reasoning": rec.reasoning
            })
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
