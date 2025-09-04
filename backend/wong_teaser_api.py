"""
Wong Teaser API Endpoints

FastAPI endpoints for Wong teaser analysis, integrated with existing betting system.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from wong_teaser_analyzer import (
    WongTeaserAnalyzer, TeaserType, TeaserOdds, GameData, 
    TeaserRecommendation, CriteriaType
)
from wong_data_integration import WongDataIntegration

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/wong-teaser", tags=["Wong Teaser Analysis"])

# Initialize components
analyzer = WongTeaserAnalyzer()
integration = WongDataIntegration()

# Pydantic models for API
class GameDataRequest(BaseModel):
    home_team: str
    away_team: str
    home_spread: float
    away_spread: float
    total: Optional[float] = None
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None
    week: Optional[int] = None
    is_divisional: bool = False
    is_primetime: bool = False

class TeaserOddsRequest(BaseModel):
    risk: int = Field(..., description="Amount risked")
    win: int = Field(..., description="Amount won if successful")
    
    def to_teaser_odds(self) -> TeaserOdds:
        return TeaserOdds(self.risk, self.win, self.win / self.risk)

class CustomOddsRequest(BaseModel):
    two_team_6pt: Optional[TeaserOddsRequest] = None
    three_team_6pt: Optional[TeaserOddsRequest] = None
    four_team_6pt: Optional[TeaserOddsRequest] = None
    three_team_10pt: Optional[TeaserOddsRequest] = None
    
    def to_dict(self) -> Dict[TeaserType, TeaserOdds]:
        odds_dict = {}
        if self.two_team_6pt:
            odds_dict[TeaserType.TWO_TEAM_6PT] = self.two_team_6pt.to_teaser_odds()
        if self.three_team_6pt:
            odds_dict[TeaserType.THREE_TEAM_6PT] = self.three_team_6pt.to_teaser_odds()
        if self.four_team_6pt:
            odds_dict[TeaserType.FOUR_TEAM_6PT] = self.four_team_6pt.to_teaser_odds()
        if self.three_team_10pt:
            odds_dict[TeaserType.THREE_TEAM_10PT] = self.three_team_10pt.to_teaser_odds()
        return odds_dict

class TeaserRecommendationResponse(BaseModel):
    teaser_type: str
    legs: List[Dict[str, Any]]
    odds: Dict[str, Any]
    expected_win_rate: float
    expected_value: float
    roi_percentage: float
    criteria_score: int
    confidence_level: str
    reasoning: List[str]

class WeeklyAnalysisResponse(BaseModel):
    week: int
    total_games: int
    qualifying_games: int
    recommendations: List[TeaserRecommendationResponse]
    summary: Dict[str, Any]

# API Endpoints

@router.get("/criteria", response_model=Dict[str, Any])
async def get_wong_criteria():
    """Get Wong teaser criteria information"""
    return {
        "strict_rules": {
            "underdogs": "Spread +1.5 to +2.5 (tease to +7.5 to +8.5)",
            "favorites": "Spread -7.5 to -8.5 (tease to -1.5 to -2.5)",
            "historical_win_rate": "75-78%"
        },
        "expanded_rules": {
            "underdogs": "Spread +1.5 to +3.0 (tease to +7.5 to +9.0)",
            "favorites": "Spread -7.5 to -9.0 (tease to -1.5 to -3.0)",
            "historical_win_rate": "73-75%"
        },
        "sweetheart_rules": {
            "underdogs": "Spread +1.5 to +2.5 (tease to +11.5 to +12.5)",
            "favorites": "Spread -10.0 to -10.5 (tease to PK to -0.5)",
            "historical_win_rate": "85-90%"
        },
        "optimal_filters": [
            "Home underdogs",
            "Road favorites", 
            "Game totals under 44",
            "Non-divisional games",
            "Weeks 3-14",
            "Avoid primetime games"
        ],
        "breakeven_rates": {
            "2_team_6pt": 0.724,
            "3_team_6pt": 0.727,
            "4_team_6pt": 0.732,
            "3_team_10pt": 0.806
        }
    }

@router.post("/analyze-game", response_model=Dict[str, Any])
async def analyze_single_game(game_data: GameDataRequest):
    """Analyze a single game for Wong teaser criteria"""
    try:
        # Convert to GameData object
        game = GameData(
            home_team=game_data.home_team,
            away_team=game_data.away_team,
            home_spread=game_data.home_spread,
            away_spread=game_data.away_spread,
            total=game_data.total,
            home_moneyline=game_data.home_moneyline,
            away_moneyline=game_data.away_moneyline,
            week=game_data.week,
            is_divisional=game_data.is_divisional,
            is_primetime=game_data.is_primetime
        )
        
        # Check criteria
        strict_result = analyzer.check_wong_criteria(game, CriteriaType.STRICT)
        expanded_result = analyzer.check_wong_criteria(game, CriteriaType.EXPANDED)
        sweetheart_result = analyzer.check_sweetheart_criteria(game)
        
        return {
            "game": {
                "home_team": game.home_team,
                "away_team": game.away_team,
                "home_spread": game.home_spread,
                "away_spread": game.away_spread,
                "total": game.total
            },
            "strict_criteria": {
                "qualifies": strict_result["qualifies"],
                "underdog_leg": strict_result["underdog_leg"].__dict__ if strict_result["underdog_leg"] else None,
                "favorite_leg": strict_result["favorite_leg"].__dict__ if strict_result["favorite_leg"] else None,
                "criteria_score": strict_result["criteria_score"]
            },
            "expanded_criteria": {
                "qualifies": expanded_result["qualifies"],
                "underdog_leg": expanded_result["underdog_leg"].__dict__ if expanded_result["underdog_leg"] else None,
                "favorite_leg": expanded_result["favorite_leg"].__dict__ if expanded_result["favorite_leg"] else None,
                "criteria_score": expanded_result["criteria_score"]
            },
            "sweetheart_criteria": {
                "qualifies": sweetheart_result["qualifies"],
                "underdog_leg": sweetheart_result["underdog_leg"].__dict__ if sweetheart_result["underdog_leg"] else None,
                "favorite_leg": sweetheart_result["favorite_leg"].__dict__ if sweetheart_result["favorite_leg"] else None,
                "criteria_score": sweetheart_result["criteria_score"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-games", response_model=List[TeaserRecommendationResponse])
async def analyze_multiple_games(
    games: List[GameDataRequest],
    custom_odds: Optional[CustomOddsRequest] = None,
    limit: int = Query(10, description="Maximum number of recommendations to return")
):
    """Analyze multiple games and return teaser recommendations"""
    try:
        # Convert to GameData objects
        game_data_list = []
        for game_req in games:
            game = GameData(
                home_team=game_req.home_team,
                away_team=game_req.away_team,
                home_spread=game_req.home_spread,
                away_spread=game_req.away_spread,
                total=game_req.total,
                home_moneyline=game_req.home_moneyline,
                away_moneyline=game_req.away_moneyline,
                week=game_req.week,
                is_divisional=game_req.is_divisional,
                is_primetime=game_req.is_primetime
            )
            game_data_list.append(game)
        
        # Get custom odds if provided
        odds_dict = custom_odds.to_dict() if custom_odds else None
        
        # Generate recommendations
        recommendations = analyzer.generate_teaser_recommendations(game_data_list, odds_dict)
        
        # Convert to response format
        response = []
        for rec in recommendations[:limit]:
            response.append(TeaserRecommendationResponse(
                teaser_type=rec.teaser_type.value,
                legs=[{
                    "team": leg.team,
                    "original_spread": leg.original_spread,
                    "teased_spread": leg.teased_spread,
                    "is_home": leg.is_home,
                    "is_underdog": leg.is_underdog,
                    "leg_type": leg.leg_type,
                    "criteria_score": leg.criteria_score,
                    "win_rate_estimate": leg.win_rate_estimate,
                    "criteria_met": leg.criteria_met
                } for leg in rec.legs],
                odds={
                    "risk": rec.odds.risk,
                    "win": rec.odds.win,
                    "american_odds": rec.odds.american_odds
                },
                expected_win_rate=rec.expected_win_rate,
                expected_value=rec.expected_value,
                roi_percentage=rec.roi_percentage,
                criteria_score=rec.criteria_score,
                confidence_level=rec.confidence_level,
                reasoning=rec.reasoning
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing games: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-analysis/{week}", response_model=WeeklyAnalysisResponse)
async def get_weekly_analysis(
    week: int,
    source: str = Query("sample", description="Data source: sample, pinnacle, or betbck"),
    detailed: bool = Query(False, description="Include detailed recommendations")
):
    """Get comprehensive weekly analysis for a specific NFL week"""
    try:
        analysis = integration.get_weekly_analysis(week, source)
        
        # Convert recommendations to response format
        recommendations = []
        for rec in analysis["recommendations"]:
            recommendations.append(TeaserRecommendationResponse(
                teaser_type=rec.teaser_type.value,
                legs=[{
                    "team": leg.team,
                    "original_spread": leg.original_spread,
                    "teased_spread": leg.teased_spread,
                    "is_home": leg.is_home,
                    "is_underdog": leg.is_underdog,
                    "leg_type": leg.leg_type,
                    "criteria_score": leg.criteria_score,
                    "win_rate_estimate": leg.win_rate_estimate,
                    "criteria_met": leg.criteria_met
                } for leg in rec.legs],
                odds={
                    "risk": rec.odds.risk,
                    "win": rec.odds.win,
                    "american_odds": rec.odds.american_odds
                },
                expected_win_rate=rec.expected_win_rate,
                expected_value=rec.expected_value,
                roi_percentage=rec.roi_percentage,
                criteria_score=rec.criteria_score,
                confidence_level=rec.confidence_level,
                reasoning=rec.reasoning
            ))
        
        # Limit recommendations if not detailed
        if not detailed:
            recommendations = recommendations[:10]
        
        return WeeklyAnalysisResponse(
            week=analysis["week"],
            total_games=analysis["total_games"],
            qualifying_games=analysis["qualifying_games"],
            recommendations=recommendations,
            summary=analysis["summary"]
        )
        
    except Exception as e:
        logger.error(f"Error getting weekly analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-odds", response_model=Dict[str, Any])
async def compare_odds_structures(
    games: List[GameDataRequest],
    standard_odds: CustomOddsRequest,
    comparison_odds: CustomOddsRequest
):
    """Compare two different odds structures"""
    try:
        # Convert to GameData objects
        game_data_list = []
        for game_req in games:
            game = GameData(
                home_team=game_req.home_team,
                away_team=game_req.away_team,
                home_spread=game_req.home_spread,
                away_spread=game_req.away_spread,
                total=game_req.total,
                home_moneyline=game_req.home_moneyline,
                away_moneyline=game_req.away_moneyline,
                week=game_req.week,
                is_divisional=game_req.is_divisional,
                is_primetime=game_req.is_primetime
            )
            game_data_list.append(game)
        
        # Generate recommendations for both odds structures
        standard_recs = analyzer.generate_teaser_recommendations(game_data_list, standard_odds.to_dict())
        comparison_recs = analyzer.generate_teaser_recommendations(game_data_list, comparison_odds.to_dict())
        
        # Calculate comparison
        comparison_results = {}
        for teaser_type in TeaserType:
            standard_rec = next((r for r in standard_recs if r.teaser_type == teaser_type), None)
            comparison_rec = next((r for r in comparison_recs if r.teaser_type == teaser_type), None)
            
            if standard_rec and comparison_rec:
                comparison_results[teaser_type.value] = {
                    "standard_roi": standard_rec.roi_percentage,
                    "comparison_roi": comparison_rec.roi_percentage,
                    "roi_difference": standard_rec.roi_percentage - comparison_rec.roi_percentage,
                    "standard_ev": standard_rec.expected_value,
                    "comparison_ev": comparison_rec.expected_value,
                    "ev_difference": standard_rec.expected_value - comparison_rec.expected_value
                }
        
        return {
            "standard_odds": {k: {"risk": v.risk, "win": v.win, "american_odds": v.american_odds} 
                            for k, v in standard_odds.to_dict().items()},
            "comparison_odds": {k: {"risk": v.risk, "win": v.win, "american_odds": v.american_odds} 
                              for k, v in comparison_odds.to_dict().items()},
            "comparison_results": comparison_results
        }
        
    except Exception as e:
        logger.error(f"Error comparing odds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-weekly/{week}")
async def export_weekly_report(week: int):
    """Export weekly analysis to JSON file"""
    try:
        filename = integration.export_weekly_report(week)
        return {"message": f"Weekly analysis exported to {filename}", "filename": filename}
    except Exception as e:
        logger.error(f"Error exporting weekly report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
