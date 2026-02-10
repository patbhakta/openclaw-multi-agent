"""
Bet Selector - Selects which props to bet on based on edge and criteria
Implements bet selection framework from research
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .prop_analysis import PropAnalysisResult, PropValueLevel

logger = logging.getLogger(__name__)


class BetAction(Enum):
    """Possible actions for a prop"""
    BET_OVER = "BET_OVER"
    BET_UNDER = "BET_UNDER"
    NO_BET = "NO_BET"
    WAIT = "WAIT"  # Waiting for more info


@dataclass
class BetSelection:
    """A selected bet with details"""
    prop_id: str
    action: BetAction
    prop_type: str
    title: str
    ai_probability: float
    market_probability: float
    edge: float
    confidence: str
    value_level: PropValueLevel
    recommended_size: float  # % of bankroll
    max_price: float  # Maximum price to pay
    min_volume: int  # Minimum volume requirement
    reasons: List[str]
    risks: List[str]


@dataclass
class SelectionCriteria:
    """Criteria for bet selection"""
    min_edge: float = 0.05  # Minimum 5% edge (from research)
    min_confidence: str = "MEDIUM"  # Minimum confidence level
    min_market_depth: int = 1000  # Minimum trading volume
    max_odds: float = 0.90  # Don't bet on extreme favorites (90%+)
    min_odds: float = 0.10  # Don't bet on extreme underdogs (10%-)
    max_correlation: float = 0.7  # Don't bet on highly correlated props

    # Position sizing
    base_unit: float = 0.02  # 2% of bankroll for standard bets
    high_confidence_multiplier: float = 1.5  # 3% for high confidence
    max_exposure_per_prop: float = 0.05  # Max 5% of bankroll per prop


class BetSelector:
    """Selects which props to bet on"""

    def __init__(self, criteria: Optional[SelectionCriteria] = None):
        self.criteria = criteria or SelectionCriteria()
        self.logger = logging.getLogger(__name__)

    def select_bets(
        self,
        analyses: List[PropAnalysisResult],
        bankroll: float,
        existing_positions: Optional[List[str]] = None
    ) -> Tuple[List[BetSelection], Dict]:
        """
        Select bets from analysis results

        Args:
            analyses: List of prop analysis results
            bankroll: Current bankroll
            existing_positions: List of prop IDs we already have positions in

        Returns:
            Tuple of (selected_bets, summary_stats)
        """
        selected_bets = []
        summary = {
            'total_analyzed': len(analyses),
            'recommended': 0,
            'rejected_edge': 0,
            'rejected_confidence': 0,
            'rejected_volume': 0,
            'rejected_odds': 0,
            'rejected_correlation': 0
        }

        for analysis in analyses:
            # Check if this prop meets all criteria
            action, rejection_reason = self._evaluate_bet(analysis, existing_positions)

            if action in [BetAction.BET_OVER, BetAction.BET_UNDER]:
                # Calculate position size
                recommended_size = self._calculate_position_size(analysis, bankroll)

                # Determine max price to pay
                if action == BetAction.BET_OVER:
                    max_price = min(analysis.market_probability * 100 + 5, 95)  # Pay up to 5c more than market
                else:
                    max_price = max(analysis.market_probability * 100 - 5, 5)  # Sell at up to 5c less

                selection = BetSelection(
                    prop_id=analysis.prop.prop_id,
                    action=action,
                    prop_type=analysis.prop.prop_type.value,
                    title=analysis.prop.title,
                    ai_probability=analysis.ai_probability,
                    market_probability=analysis.market_probability,
                    edge=analysis.edge,
                    confidence=analysis.confidence,
                    value_level=analysis.value_level,
                    recommended_size=recommended_size,
                    max_price=max_price,
                    min_volume=self.criteria.min_market_depth,
                    reasons=analysis.reasoning,
                    risks=analysis.risk_factors
                )
                selected_bets.append(selection)
                summary['recommended'] += 1
            else:
                summary[rejection_reason] += 1

        # Sort bets by edge (highest first)
        selected_bets.sort(key=lambda x: x.edge, reverse=True)

        return selected_bets, summary

    def _evaluate_bet(
        self,
        analysis: PropAnalysisResult,
        existing_positions: Optional[List[str]]
    ) -> Tuple[BetAction, str]:
        """Evaluate if a bet should be placed"""
        prop = analysis.prop

        # Check if recommendation is valid
        if analysis.recommendation == "OVER":
            action = BetAction.BET_OVER
        elif analysis.recommendation == "UNDER":
            action = BetAction.BET_UNDER
        else:
            return BetAction.NO_BET, "rejected_edge"

        # Check edge threshold
        if abs(analysis.edge) < self.criteria.min_edge:
            return BetAction.NO_BET, "rejected_edge"

        # Check confidence level
        confidence_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        if confidence_order[analysis.confidence] < confidence_order[self.criteria.min_confidence]:
            return BetAction.NO_BET, "rejected_confidence"

        # Check market depth
        if prop.volume and prop.volume < self.criteria.min_market_depth:
            return BetAction.NO_BET, "rejected_volume"

        # Check odds range (avoid extreme favorites/underdogs)
        market_prob = analysis.market_probability
        if market_prob > self.criteria.max_odds or market_prob < self.criteria.min_odds:
            return BetAction.NO_BET, "rejected_odds"

        # Check correlation with existing positions
        # (Simplified version - in real implementation would calculate correlation)
        if existing_positions and prop.prop_id in existing_positions:
            return BetAction.WAIT, "rejected_correlation"

        return action, "recommended"

    def _calculate_position_size(self, analysis: PropAnalysisResult, bankroll: float) -> float:
        """
        Calculate position size based on Kelly Criterion (simplified)

        Formula: f = (bp - q) / b
        Where:
        - f = fraction of bankroll to bet
        - b = odds (decimal)
        - p = probability of winning
        - q = probability of losing (1 - p)

        Simplified: Use edge * confidence as proxy
        """
        # Base unit
        size = self.criteria.base_unit

        # Adjust for confidence
        if analysis.confidence == "HIGH":
            size *= self.criteria.high_confidence_multiplier
        elif analysis.confidence == "MEDIUM":
            size *= 1.0
        else:  # LOW
            size *= 0.5

        # Adjust for edge (larger edge = larger position)
        edge_multiplier = min(abs(analysis.edge) / self.criteria.min_edge, 2.0)
        size *= edge_multiplier

        # Apply to bankroll
        position_amount = bankroll * size

        # Cap at maximum exposure per prop
        max_position = bankroll * self.criteria.max_exposure_per_prop
        return min(position_amount, max_position)

    def filter_by_category(
        self,
        analyses: List[PropAnalysisResult],
        max_per_category: int = 2
    ) -> List[PropAnalysisResult]:
        """
        Filter to limit exposure per category

        Args:
            analyses: List of analysis results
            max_per_category: Maximum number of bets per prop type

        Returns:
            Filtered list of analyses
        """
        filtered = []
        category_counts = {}

        for analysis in analyses:
            prop_type = analysis.prop.prop_type.value
            count = category_counts.get(prop_type, 0)

            if count < max_per_category:
                filtered.append(analysis)
                category_counts[prop_type] = count + 1

        return filtered

    def check_correlation(self, prop1: str, prop2: str) -> float:
        """
        Check correlation between two props (simplified)

        In real implementation, this would calculate statistical correlation
        based on historical data. For now, we use heuristics.
        """
        # QB props on same team are highly correlated
        if 'qb' in prop1.lower() and 'qb' in prop2.lower():
            return 0.8

        # WR props on same team are correlated
        if 'wr' in prop1.lower() and 'wr' in prop2.lower():
            return 0.6

        # Player props and game props are correlated
        if ('qb' in prop1.lower() or 'wr' in prop1.lower()) and 'team' in prop2.lower():
            return 0.5

        return 0.0

    def get_selection_summary(self, selections: List[BetSelection]) -> Dict:
        """Get summary statistics for selected bets"""
        if not selections:
            return {
                'total_bets': 0,
                'total_exposure': 0,
                'avg_edge': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'by_category': {}
            }

        total_exposure = sum(s.recommended_size for s in selections)
        avg_edge = sum(s.edge for s in selections) / len(selections)

        by_category = {}
        for sel in selections:
            category = sel.prop_type
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(sel.recommended_size)

        return {
            'total_bets': len(selections),
            'total_exposure': total_exposure,
            'avg_edge': avg_edge,
            'high_confidence': sum(1 for s in selections if s.confidence == "HIGH"),
            'medium_confidence': sum(1 for s in selections if s.confidence == "MEDIUM"),
            'by_category': {
                cat: len(bets) for cat, bets in by_category.items()
            }
        }


def test_bet_selector():
    """Test the bet selector"""
    from .prop_analysis import create_test_prop, PropType

    selector = BetSelector()

    # Create test analyses
    test_props = [
        (PropType.QB_PASSING_YARDS, 275.0, 52.0),  # Edge: avg 285, so OVER edge
        (PropType.WR_RECEPTIONS, 6.5, 48.0),  # Edge
        (PropType.RB_RUSHING_YARDS, 75.0, 55.0),  # Edge
        (PropType.FIRST_SCORE, None, 60.0),  # TD first
        (PropType.COIN_TOSS, None, 50.0),  # Avoid - low value
    ]

    analyses = []
    for prop_type, line, price in test_props:
        prop = create_test_prop(prop_type, line, price)

        # Mock analysis result
        from .prop_analysis import PropAnalysisResult, PropValueLevel
        ai_prob = price / 100.0 + 0.08  # Simulate edge

        analysis = PropAnalysisResult(
            prop=prop,
            ai_probability=ai_prob,
            market_probability=price / 100.0,
            edge=ai_prob - prop.market_probability,
            confidence="MEDIUM",
            recommendation="OVER" if ai_prob > prop.market_probability else "UNDER",
            value_level=PropValueLevel.HIGH if prop_type not in [PropType.COIN_TOSS, PropType.GATORADE_COLOR] else PropValueLevel.AVOID,
            reasoning=["Test reasoning"],
            risk_factors=[]
        )
        analyses.append(analysis)

    # Select bets
    bankroll = 1000.0
    selections, summary = selector.select_bets(analyses, bankroll)

    print("Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print(f"\nSelected {len(selections)} bets:")
    for sel in selections:
        print(f"  {sel.title}: {sel.action.value} (${sel.recommended_size:.2f}) - Edge: {sel.edge*100:.1f}%")


if __name__ == "__main__":
    test_bet_selector()
