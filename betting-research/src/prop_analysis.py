"""
Prop Analysis Engine - Analyzes player and game props for value detection
Based on Super Bowl research findings from Atlas
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PropType(Enum):
    """Types of prop bets with their expected value levels"""
    QB_PASSING_YARDS = "qb_passing_yards"  # HIGH value
    RB_RUSHING_YARDS = "rb_rushing_yards"  # MED-HIGH value
    WR_RECEPTIONS = "wr_receptions"  # HIGH value
    WR_YARDS = "wr_yards"  # HIGH value
    FIRST_HALF_TOTALS = "first_half_totals"  # HIGH-MED value
    FIRST_SCORE = "first_score"  # MED-HIGH value
    ANYTIME_TD = "anytime_td"  # MED value
    TEAM_TOTALS = "team_totals"  # MED value
    COIN_TOSS = "coin_toss"  # LOW value (avoid)
    GATORADE_COLOR = "gatorade_color"  # LOW value (avoid)


class PropValueLevel(Enum):
    """Value levels for prop categories"""
    HIGH = "HIGH"
    MEDIUM_HIGH = "MEDIUM_HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    AVOID = "AVOID"


@dataclass
class PropData:
    """Data structure for a prop bet"""
    prop_id: str
    prop_type: PropType
    title: str
    player_team: str  # Team name or "GAME" for game props
    metric: str  # e.g., "passing_yards", "receptions"
    line: float  # The over/under line
    market_price: float  # Current market price (0-100 cents)
    market_probability: float  # Implied probability from market
    open_price: Optional[float] = None  # Opening price for line movement tracking
    volume: Optional[int] = None  # Trading volume
    metadata: Dict = None


@dataclass
class PlayerStats:
    """Historical player statistics for analysis"""
    player_name: str
    team: str
    season_avg: float  # Season average for the metric
    recent_5_avg: float  # Average of last 5 games
    recent_3_avg: float  # Average of last 3 games
    vs_opponent_avg: float  # Historical avg against this opponent
    home_away_avg: float  # Performance at home/away
    std_dev: float  # Standard deviation
    games_played: int


@dataclass
class GameContext:
    """Context about the game situation"""
    venue_type: str  # "dome" or "outdoor"
    weather_forecast: Dict  # Wind, rain, temperature
    injury_impact: Dict  # Key injuries
    game_script_prediction: str  # "pass_heavy", "run_heavy", "balanced"
    spread: float  # Point spread
    over_under: float  # Total points over/under


@dataclass
class PropAnalysisResult:
    """Result of prop analysis"""
    prop: PropData
    ai_probability: float  # Our calculated probability
    market_probability: float
    edge: float  # AI probability - market probability (in percentage points)
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    recommendation: str  # "OVER", "UNDER", "NO_BET"
    value_level: PropValueLevel
    reasoning: List[str]  # List of reasons for the recommendation
    risk_factors: List[str]  # List of risk factors


class PropAnalyzer:
    """Analyzes props for betting opportunities"""

    # Value level mapping from research
    VALUE_LEVELS = {
        PropType.QB_PASSING_YARDS: PropValueLevel.HIGH,
        PropType.WR_RECEPTIONS: PropValueLevel.HIGH,
        PropType.WR_YARDS: PropValueLevel.HIGH,
        PropType.FIRST_HALF_TOTALS: PropValueLevel.MEDIUM_HIGH,
        PropType.RB_RUSHING_YARDS: PropValueLevel.MEDIUM_HIGH,
        PropType.FIRST_SCORE: PropValueLevel.MEDIUM_HIGH,
        PropType.ANYTIME_TD: PropValueLevel.MEDIUM,
        PropType.TEAM_TOTALS: PropValueLevel.MEDIUM,
        PropType.COIN_TOSS: PropValueLevel.AVOID,
        PropType.GATORADE_COLOR: PropValueLevel.AVOID,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_prop(
        self,
        prop: PropData,
        player_stats: Optional[PlayerStats] = None,
        game_context: Optional[GameContext] = None,
        historical_performance: Optional[Dict] = None
    ) -> PropAnalysisResult:
        """
        Analyze a prop bet for value

        Args:
            prop: The prop to analyze
            player_stats: Historical stats for player props
            game_context: Game situation context
            historical_performance: Historical patterns from past Super Bowls

        Returns:
            PropAnalysisResult with recommendation
        """
        # Check if we should avoid this prop type
        value_level = self.VALUE_LEVELS.get(prop.prop_type, PropValueLevel.MEDIUM)
        if value_level == PropValueLevel.AVOID:
            return PropAnalysisResult(
                prop=prop,
                ai_probability=prop.market_probability,
                market_probability=prop.market_probability,
                edge=0,
                confidence="LOW",
                recommendation="NO_BET",
                value_level=value_level,
                reasoning=["Low value prop type with no edge"],
                risk_factors=["No statistical advantage possible"]
            )

        # Calculate AI probability based on prop type and available data
        ai_probability = self._calculate_probability(prop, player_stats, game_context, historical_performance)

        # Calculate edge
        edge = ai_probability - prop.market_probability

        # Determine recommendation
        recommendation = self._determine_recommendation(edge, prop)

        # Determine confidence level
        confidence = self._determine_confidence(edge, prop, player_stats)

        # Generate reasoning
        reasoning = self._generate_reasoning(prop, player_stats, game_context, ai_probability, edge)

        # Identify risk factors
        risk_factors = self._identify_risks(prop, player_stats, game_context)

        return PropAnalysisResult(
            prop=prop,
            ai_probability=ai_probability,
            market_probability=prop.market_probability,
            edge=edge,
            confidence=confidence,
            recommendation=recommendation,
            value_level=value_level,
            reasoning=reasoning,
            risk_factors=risk_factors
        )

    def _calculate_probability(
        self,
        prop: PropData,
        player_stats: Optional[PlayerStats],
        game_context: Optional[GameContext],
        historical_performance: Optional[Dict]
    ) -> float:
        """Calculate our probability estimate for the prop"""
        base_probability = prop.market_probability  # Start with market estimate
        adjustments = []

        # For player props, use historical stats
        if player_stats:
            if prop.prop_type in [PropType.QB_PASSING_YARDS, PropType.RB_RUSHING_YARDS]:
                # Yardage props: analyze if line is below/above season average
                if player_stats.season_avg > prop.line:
                    # Line is below average -> OVER has higher probability
                    pct_above = (player_stats.season_avg - prop.line) / prop.line
                    adjustments.append(("Season avg above line", min(pct_above * 0.15, 0.10)))  # Max 10% boost

                if player_stats.recent_5_avg > prop.line:
                    pct_above = (player_stats.recent_5_avg - prop.line) / prop.line
                    adjustments.append(("Recent form strong", min(pct_above * 0.10, 0.07)))

            elif prop.prop_type in [PropType.WR_RECEPTIONS, PropType.WR_YARDS]:
                # Reception props: target volume is key
                if player_stats.season_avg > prop.line:
                    pct_above = (player_stats.season_avg - prop.line) / prop.line
                    adjustments.append(("Target volume strong", min(pct_above * 0.12, 0.08)))

        # For game props, use historical Super Bowl patterns
        if historical_performance:
            if prop.prop_type == PropType.FIRST_SCORE:
                # 60% of recent SBs had TD first
                td_rate = historical_performance.get('first_score_td_rate', 0.60)
                adjustments.append(("Historical TD rate", (td_rate - 0.50) * 0.5))

            elif prop.prop_type == PropType.FIRST_HALF_TOTALS:
                # Less efficient than full game
                adjustments.append(("First half edge", 0.02))  # Small edge

        # Adjust for game context
        if game_context:
            if prop.prop_type in [PropType.QB_PASSING_YARDS, PropType.WR_YARDS]:
                if game_context.venue_type == "outdoor":
                    wind = game_context.weather_forecast.get('wind_speed', 0)
                    if wind > 15:
                        adjustments.append(("High wind reduces passing", -0.08))
                    if game_context.weather_forecast.get('precipitation') in ['rain', 'snow']:
                        adjustments.append(("Precipitation reduces passing", -0.05))

                if game_context.game_script_prediction == "pass_heavy":
                    adjustments.append(("Pass-heavy game script", 0.06))
                elif game_context.game_script_prediction == "run_heavy":
                    adjustments.append(("Run-heavy game script", -0.06))

            elif prop.prop_type == PropType.RB_RUSHING_YARDS:
                if game_context.game_script_prediction == "pass_heavy":
                    adjustments.append(("Pass-heavy game script", -0.08))
                elif game_context.game_script_prediction == "run_heavy":
                    adjustments.append(("Run-heavy game script", 0.08))

        # Apply adjustments
        for reason, adj in adjustments:
            base_probability += adj

        # Ensure probability stays in valid range
        return max(0.01, min(0.99, base_probability))

    def _determine_recommendation(self, edge: float, prop: PropData) -> str:
        """Determine bet recommendation based on edge"""
        # Edge threshold: 5% minimum (from research)
        if edge >= 0.05:
            return "OVER"
        elif edge <= -0.05:
            return "UNDER"
        else:
            return "NO_BET"

    def _determine_confidence(
        self,
        edge: float,
        prop: PropData,
        player_stats: Optional[PlayerStats]
    ) -> str:
        """Determine confidence level"""
        if abs(edge) >= 0.15:
            return "HIGH"
        elif abs(edge) >= 0.08:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_reasoning(
        self,
        prop: PropData,
        player_stats: Optional[PlayerStats],
        game_context: Optional[GameContext],
        ai_probability: float,
        edge: float
    ) -> List[str]:
        """Generate reasoning for the recommendation"""
        reasons = []

        if prop.prop_type == PropType.QB_PASSING_YARDS:
            reasons.append(f"QB passing props have HIGH value (research finding)")
            if player_stats:
                if player_stats.season_avg > prop.line:
                    reasons.append(f"Season avg {player_stats.season_avg:.1f} > line {prop.line}")
                if player_stats.recent_5_avg > player_stats.season_avg:
                    reasons.append("Recent form exceeds season average")

        elif prop.prop_type in [PropType.WR_RECEPTIONS, PropType.WR_YARDS]:
            reasons.append(f"WR props have HIGH value (consistent target volume)")
            if player_stats:
                if player_stats.season_avg > prop.line:
                    reasons.append(f"Target volume {player_stats.season_avg:.1f} > line {prop.line}")

        elif prop.prop_type == PropType.FIRST_SCORE:
            reasons.append("First score has MEDIUM-HIGH value")
            reasons.append("Historical pattern: 60% of recent SBs had TD first")

        elif prop.prop_type == PropType.FIRST_HALF_TOTALS:
            reasons.append("First half totals have HIGH-MED value (less efficient than full game)")

        if game_context and game_context.venue_type == "outdoor":
            wind = game_context.weather_forecast.get('wind_speed', 0)
            if wind > 15:
                reasons.append(f"High wind ({wind} mph) impacts passing metrics")

        if edge >= 0.05:
            reasons.append(f"Edge of {edge*100:.1f}% exceeds 5% threshold")
        elif edge <= -0.05:
            reasons.append(f"Negative edge of {edge*100:.1f}% - market line favored")

        return reasons

    def _identify_risks(
        self,
        prop: PropData,
        player_stats: Optional[PlayerStats],
        game_context: Optional[GameContext]
    ) -> List[str]:
        """Identify risk factors for the prop"""
        risks = []

        # Injury risk
        if player_stats and game_context:
            injuries = game_context.injury_impact
            if prop.player_team in injuries:
                risks.append(f"Teammate injuries may affect game script")

        # Game script uncertainty
        if game_context:
            if game_context.game_script_prediction == "balanced":
                risks.append("Balanced game script introduces uncertainty")

        # Low volume risk
        if prop.volume and prop.volume < 1000:
            risks.append(f"Low market volume ({prop.volume}) - limited liquidity")

        # Volatile metrics
        if prop.prop_type == PropType.RB_RUSHING_YARDS:
            risks.append("RB yardage is highly dependent on game flow")

        # Weather risk for outdoor games
        if game_context and game_context.venue_type == "outdoor":
            weather = game_context.weather_forecast
            if weather.get('precipitation') in ['rain', 'snow']:
                risks.append("Precipitation increases unpredictability")

        return risks if risks else ["Standard betting risks apply"]

    def batch_analyze(
        self,
        props: List[PropData],
        player_stats_dict: Optional[Dict[str, PlayerStats]] = None,
        game_context: Optional[GameContext] = None,
        historical_performance: Optional[Dict] = None
    ) -> List[PropAnalysisResult]:
        """
        Analyze multiple props in batch

        Args:
            props: List of props to analyze
            player_stats_dict: Mapping of player name to stats
            game_context: Game situation context
            historical_performance: Historical patterns

        Returns:
            List of analysis results
        """
        results = []
        for prop in props:
            player_stats = None
            if player_stats_dict and prop.player_team != "GAME":
                # Try to find player stats
                for player_name, stats in player_stats_dict.items():
                    if player_name in prop.title:
                        player_stats = stats
                        break

            result = self.analyze_prop(prop, player_stats, game_context, historical_performance)
            results.append(result)

        return results


def create_test_prop(prop_type: PropType, line: float, market_price: float) -> PropData:
    """Helper function to create a test prop"""
    return PropData(
        prop_id=f"test_{prop_type.value}",
        prop_type=prop_type,
        title=f"Test {prop_type.value} prop",
        player_team="TEST_TEAM",
        metric=prop_type.value,
        line=line,
        market_price=market_price,
        market_probability=market_price / 100.0,
        open_price=market_price,
        volume=5000
    )
