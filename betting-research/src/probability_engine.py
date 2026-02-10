"""
Probability Engine - Calculates probabilities for prop bets
Uses multiple signals: historical data, player stats, game context, market signals
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class SignalSource(Enum):
    """Sources of probability signals"""
    HISTORICAL = "historical"  # Historical Super Bowl patterns
    PLAYER_STATS = "player_stats"  # Individual player performance
    GAME_CONTEXT = "game_context"  # Game situation (weather, venue, etc.)
    MARKET_MOVEMENT = "market_movement"  # Line movement analysis
    INJURY_ADJUSTMENT = "injury_adjustment"  # Injury impact


@dataclass
class ProbabilitySignal:
    """A single probability signal with confidence"""
    source: SignalSource
    probability: float  # Probability estimate (0-1)
    confidence: float  # Confidence in this signal (0-1)
    weight: float  # Weight in final calculation (0-1)
    reason: str  # Explanation for this signal


@dataclass
class ProbabilityEstimate:
    """Final probability estimate with breakdown"""
    final_probability: float  # Weighted average probability
    signals: List[ProbabilitySignal]  # All signals used
    confidence: float  # Overall confidence (0-1)
    signal_breakdown: Dict[str, float]  # Contribution of each signal source


class ProbabilityEngine:
    """Calculates prop bet probabilities using multiple signals"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Default weights for different signal sources
        self.default_weights = {
            SignalSource.HISTORICAL: 0.15,
            SignalSource.PLAYER_STATS: 0.35,
            SignalSource.GAME_CONTEXT: 0.20,
            SignalSource.MARKET_MOVEMENT: 0.20,
            SignalSource.INJURY_ADJUSTMENT: 0.10,
        }

    def calculate_probability(
        self,
        prop_data: Dict,
        historical_data: Optional[Dict] = None,
        player_stats: Optional[Dict] = None,
        game_context: Optional[Dict] = None,
        market_data: Optional[Dict] = None,
        injuries: Optional[Dict] = None,
        custom_weights: Optional[Dict[SignalSource, float]] = None
    ) -> ProbabilityEstimate:
        """
        Calculate final probability for a prop using multiple signals

        Args:
            prop_data: Dictionary with prop details (type, line, etc.)
            historical_data: Historical Super Bowl patterns
            player_stats: Player statistics
            game_context: Game situation context
            market_data: Market data (line movement, etc.)
            injuries: Injury report data
            custom_weights: Custom weights for signal sources

        Returns:
            ProbabilityEstimate with final probability and breakdown
        """
        weights = custom_weights or self.default_weights
        signals = []

        # Generate signals from different sources
        hist_signal = self._historical_signal(prop_data, historical_data)
        if hist_signal:
            signals.append(hist_signal)

        stats_signal = self._player_stats_signal(prop_data, player_stats)
        if stats_signal:
            signals.append(stats_signal)

        context_signal = self._game_context_signal(prop_data, game_context)
        if context_signal:
            signals.append(context_signal)

        market_signal = self._market_movement_signal(prop_data, market_data)
        if market_signal:
            signals.append(market_signal)

        injury_signal = self._injury_adjustment_signal(prop_data, injuries)
        if injury_signal:
            signals.append(injury_signal)

        # If no signals generated, use market probability
        if not signals:
            market_prob = prop_data.get('market_probability', 0.5)
            return ProbabilityEstimate(
                final_probability=market_prob,
                signals=[],
                confidence=0.3,
                signal_breakdown={"market_default": market_prob}
            )

        # Calculate weighted average
        weighted_sum = 0
        weight_sum = 0
        signal_breakdown = {}

        for signal in signals:
            weight = weights.get(signal.source, 0.1) * signal.confidence
            weighted_sum += signal.probability * weight
            weight_sum += weight
            signal_breakdown[signal.source.value] = signal.probability * weight

        # Normalize
        final_probability = weighted_sum / weight_sum if weight_sum > 0 else 0.5

        # Calculate overall confidence
        overall_confidence = sum(signal.confidence * weights.get(signal.source, 0.1) for signal in signals)

        return ProbabilityEstimate(
            final_probability=final_probability,
            signals=signals,
            confidence=min(overall_confidence, 1.0),
            signal_breakdown=signal_breakdown
        )

    def _historical_signal(self, prop_data: Dict, historical_data: Optional[Dict]) -> Optional[ProbabilitySignal]:
        """Generate signal from historical Super Bowl patterns"""
        if not historical_data:
            return None

        prop_type = prop_data.get('prop_type')

        if prop_type == 'first_score':
            # Historical pattern: 60% TD first
            td_rate = historical_data.get('first_score_td_rate', 0.60)
            return ProbabilitySignal(
                source=SignalSource.HISTORICAL,
                probability=td_rate,
                confidence=0.7,
                weight=self.default_weights[SignalSource.HISTORICAL],
                reason=f"Recent SBs: TD first {td_rate*100:.0f}% of time"
            )

        elif prop_type == 'total_points':
            # Historical over/under rates
            over_rate = historical_data.get('total_over_rate', 0.50)
            return ProbabilitySignal(
                source=SignalSource.HISTORICAL,
                probability=over_rate,
                confidence=0.6,
                weight=self.default_weights[SignalSource.HISTORICAL],
                reason=f"Recent SBs: Over hit {over_rate*100:.0f}% of time"
            )

        elif prop_type in ['qb_passing_yards', 'wr_receptions']:
            # Historical over rate for player props
            over_rate = historical_data.get('player_props_over_rate', 0.55)
            return ProbabilitySignal(
                source=SignalSource.HISTORICAL,
                probability=over_rate,
                confidence=0.5,
                weight=self.default_weights[SignalSource.HISTORICAL],
                reason="Player props tend to hit overs in high-scoring games"
            )

        return None

    def _player_stats_signal(self, prop_data: Dict, player_stats: Optional[Dict]) -> Optional[ProbabilitySignal]:
        """Generate signal from player statistics"""
        if not player_stats:
            return None

        line = prop_data.get('line', 0)
        season_avg = player_stats.get('season_avg', 0)
        recent_avg = player_stats.get('recent_5_avg', 0)

        # Calculate probability based on historical performance vs line
        if season_avg == 0:
            return None

        # Simple model: if season avg > line, higher probability of over
        pct_diff = (season_avg - line) / line if line > 0 else 0

        # Base probability
        base_prob = 0.5 + (pct_diff * 0.5)  # Convert to 0-1 range

        # Adjust for recent form
        if recent_avg > season_avg:
            base_prob += 0.05  # Hot player bonus
        elif recent_avg < season_avg:
            base_prob -= 0.05  # Cold player penalty

        # Calculate confidence based on sample size
        games_played = player_stats.get('games_played', 0)
        confidence = min(games_played / 16.0, 1.0)  # Full season = full confidence

        return ProbabilitySignal(
            source=SignalSource.PLAYER_STATS,
            probability=max(0.1, min(0.9, base_prob)),
            confidence=confidence,
            weight=self.default_weights[SignalSource.PLAYER_STATS],
            reason=f"Season avg {season_avg:.1f} vs line {line:.1f}"
        )

    def _game_context_signal(self, prop_data: Dict, game_context: Optional[Dict]) -> Optional[ProbabilitySignal]:
        """Generate signal from game context (weather, venue, etc.)"""
        if not game_context:
            return None

        prop_type = prop_data.get('prop_type')
        adjustments = []
        prob_adjustment = 0.5  # Start neutral

        # Venue type
        venue = game_context.get('venue_type')
        weather = game_context.get('weather_forecast', {})
        game_script = game_context.get('game_script_prediction', 'balanced')

        if prop_type in ['qb_passing_yards', 'wr_receptions', 'wr_yards']:
            if venue == 'outdoor':
                wind = weather.get('wind_speed', 0)
                if wind > 15:
                    prob_adjustment -= 0.08  # High wind hurts passing
                    adjustments.append(f"High wind ({wind} mph)")

                if weather.get('precipitation') in ['rain', 'snow']:
                    prob_adjustment -= 0.05  # Precip hurts passing
                    adjustments.append("Precipitation")

            if game_script == 'pass_heavy':
                prob_adjustment += 0.06
                adjustments.append("Pass-heavy game script")
            elif game_script == 'run_heavy':
                prob_adjustment -= 0.06
                adjustments.append("Run-heavy game script")

        elif prop_type == 'rb_rushing_yards':
            if game_script == 'pass_heavy':
                prob_adjustment -= 0.08
                adjustments.append("Pass-heavy game script")
            elif game_script == 'run_heavy':
                prob_adjustment += 0.08
                adjustments.append("Run-heavy game script")

        elif prop_type in ['first_half_totals', 'team_totals']:
            # First half totals are less efficient
            prob_adjustment += 0.02
            adjustments.append("First half inefficiency")

        # No significant adjustments
        if not adjustments:
            return None

        # Confidence based on how specific the context is
        confidence = 0.6 if len(adjustments) >= 2 else 0.4

        reason = ", ".join(adjustments)

        return ProbabilitySignal(
            source=SignalSource.GAME_CONTEXT,
            probability=max(0.1, min(0.9, prob_adjustment)),
            confidence=confidence,
            weight=self.default_weights[SignalSource.GAME_CONTEXT],
            reason=reason
        )

    def _market_movement_signal(self, prop_data: Dict, market_data: Optional[Dict]) -> Optional[ProbabilitySignal]:
        """Generate signal from market movement and line tracking"""
        if not market_data:
            return None

        open_price = market_data.get('open_price')
        current_price = market_data.get('current_price')
        prop_type = prop_data.get('prop_type')

        if open_price is None or current_price is None:
            return None

        # Calculate line movement
        price_change = current_price - open_price
        pct_change = abs(price_change / open_price) if open_price > 0 else 0

        # Significant movement suggests sharp money or public bias
        if pct_change < 0.02:  # Less than 2% change
            return None

        # Sharp money tends to move lines in efficient direction
        # Follow the movement with caution
        if current_price > open_price:
            prob = current_price / 100.0
            direction = "up"
        else:
            prob = current_price / 100.0
            direction = "down"

        # Confidence based on movement magnitude
        confidence = min(pct_change * 5, 0.8)

        return ProbabilitySignal(
            source=SignalSource.MARKET_MOVEMENT,
            probability=prob,
            confidence=confidence,
            weight=self.default_weights[SignalSource.MARKET_MOVEMENT],
            reason=f"Line moved {direction} {pct_change*100:.1f}% (sharp money?)"
        )

    def _injury_adjustment_signal(self, prop_data: Dict, injuries: Optional[Dict]) -> Optional[ProbabilitySignal]:
        """Generate signal from injury report"""
        if not injuries:
            return None

        team = prop_data.get('player_team')
        prop_type = prop_data.get('prop_type')

        if not team or team not in injuries:
            return None

        team_injuries = injuries[team]
        adjustment = 0.5
        reasons = []

        # Check for key injuries
        if 'qb' in team_injuries and team_injuries['qb']['status'] == 'out':
            # Starting QB out - big impact on passing props
            if prop_type == 'qb_passing_yards':
                adjustment -= 0.20  # Backup QB = less yards
                reasons.append("Starting QB out")
            elif prop_type in ['wr_receptions', 'wr_yards']:
                adjustment -= 0.10  # Backup QB = worse for WRs
                reasons.append("Starting QB out")
            elif prop_type == 'rb_rushing_yards':
                adjustment += 0.05  # More rushing with backup QB
                reasons.append("Starting QB out (more rushing)")

        if 'wr1' in team_injuries and team_injuries['wr1']['status'] in ['out', 'doubtful']:
            # #1 WR out - helps other WRs
            if prop_type in ['wr_receptions', 'wr_yards']:
                adjustment += 0.10
                reasons.append("#1 WR out (more targets for others)")

        if 'rb1' in team_injuries and team_injuries['rb1']['status'] in ['out', 'doubtful']:
            # Starting RB out
            if prop_type == 'rb_rushing_yards':
                adjustment -= 0.15  # Backup RB = less production
                reasons.append("Starting RB out")

        if not reasons:
            return None

        confidence = 0.7  # High confidence in injury impact

        return ProbabilitySignal(
            source=SignalSource.INJURY_ADJUSTMENT,
            probability=max(0.1, min(0.9, adjustment)),
            confidence=confidence,
            weight=self.default_weights[SignalSource.INJURY_ADJUSTMENT],
            reason=", ".join(reasons)
        )


def test_probability_engine():
    """Test the probability engine with sample data"""
    engine = ProbabilityEngine()

    # Sample prop data
    prop_data = {
        'prop_type': 'qb_passing_yards',
        'line': 275.0,
        'market_probability': 0.52,
    }

    # Sample supporting data
    player_stats = {
        'season_avg': 285.0,
        'recent_5_avg': 295.0,
        'games_played': 16
    }

    game_context = {
        'venue_type': 'outdoor',
        'weather_forecast': {
            'wind_speed': 5,
            'precipitation': 'clear'
        },
        'game_script_prediction': 'balanced'
    }

    historical_data = {
        'player_props_over_rate': 0.55
    }

    # Calculate probability
    estimate = engine.calculate_probability(
        prop_data=prop_data,
        player_stats=player_stats,
        game_context=game_context,
        historical_data=historical_data
    )

    print(f"Final Probability: {estimate.final_probability:.2%}")
    print(f"Confidence: {estimate.confidence:.2%}")
    print("\nSignals:")
    for signal in estimate.signals:
        print(f"  {signal.source.value}: {signal.probability:.2%} (conf: {signal.confidence:.2f}) - {signal.reason}")


if __name__ == "__main__":
    test_probability_engine()
