"""
Unit tests for Bet Selector
"""

import pytest
from src.bet_selector import (
    BetSelector, BetAction, BetSelection, SelectionCriteria
)
from src.prop_analysis import (
    PropAnalysisResult, PropValueLevel, PropType, PropData
)


@pytest.fixture
def selector():
    """Create a BetSelector instance"""
    return BetSelector()


@pytest.fixture
def sample_analysis_over():
    """Create sample analysis result for OVER bet"""
    prop = PropData(
        prop_id="test_qb_passing_yards",
        prop_type=PropType.QB_PASSING_YARDS,
        title="Test QB Passing Yards",
        player_team="Chiefs",
        metric="passing_yards",
        line=275.0,
        market_price=52.0,
        market_probability=0.52,
        volume=5000
    )

    return PropAnalysisResult(
        prop=prop,
        ai_probability=0.60,
        market_probability=0.52,
        edge=0.08,
        confidence="MEDIUM",
        recommendation="OVER",
        value_level=PropValueLevel.HIGH,
        reasoning=["Test reasoning"],
        risk_factors=["Test risk"]
    )


@pytest.fixture
def sample_analysis_under():
    """Create sample analysis result for UNDER bet"""
    prop = PropData(
        prop_id="test_wr_receptions",
        prop_type=PropType.WR_RECEPTIONS,
        title="Test WR Receptions",
        player_team="Eagles",
        metric="receptions",
        line=6.5,
        market_price=55.0,
        market_probability=0.55,
        volume=3000
    )

    return PropAnalysisResult(
        prop=prop,
        ai_probability=0.45,
        market_probability=0.55,
        edge=-0.10,
        confidence="MEDIUM",
        recommendation="UNDER",
        value_level=PropValueLevel.HIGH,
        reasoning=["Test reasoning"],
        risk_factors=["Test risk"]
    )


@pytest.fixture
def sample_analysis_no_bet():
    """Create sample analysis result for NO_BET"""
    prop = PropData(
        prop_id="test_coin_toss",
        prop_type=PropType.COIN_TOSS,
        title="Coin Toss",
        player_team="GAME",
        metric="coin_toss",
        line=None,
        market_price=50.0,
        market_probability=0.5,
        volume=10000
    )

    return PropAnalysisResult(
        prop=prop,
        ai_probability=0.50,
        market_probability=0.50,
        edge=0.0,
        confidence="LOW",
        recommendation="NO_BET",
        value_level=PropValueLevel.AVOID,
        reasoning=["Low value prop"],
        risk_factors=["No edge"]
    )


@pytest.fixture
def sample_analysis_low_edge():
    """Create sample analysis result with edge below threshold"""
    prop = PropData(
        prop_id="test_rb_rushing_yards",
        prop_type=PropType.RB_RUSHING_YARDS,
        title="Test RB Rushing Yards",
        player_team="Chiefs",
        metric="rushing_yards",
        line=75.0,
        market_price=50.0,
        market_probability=0.50,
        volume=2000
    )

    return PropAnalysisResult(
        prop=prop,
        ai_probability=0.53,  # Only 3% edge
        market_probability=0.50,
        edge=0.03,
        confidence="LOW",
        recommendation="OVER",
        value_level=PropValueLevel.MEDIUM_HIGH,
        reasoning=["Small edge"],
        risk_factors=["Test risk"]
    )


class TestSelectionCriteria:
    """Test SelectionCriteria dataclass"""

    def test_default_values(self):
        """Test default criteria values"""
        criteria = SelectionCriteria()

        assert criteria.min_edge == 0.05
        assert criteria.min_confidence == "MEDIUM"
        assert criteria.min_market_depth == 1000
        assert criteria.base_unit == 0.02


class TestBetSelector:
    """Test BetSelector functionality"""

    def test_select_bets_filters_by_edge(
        self,
        selector,
        sample_analysis_over,
        sample_analysis_low_edge
    ):
        """Test that bets below edge threshold are filtered"""
        analyses = [sample_analysis_over, sample_analysis_low_edge]
        selections, summary = selector.select_bets(analyses, bankroll=1000.0)

        assert len(selections) == 1
        assert selections[0].prop_id == sample_analysis_over.prop_id
        assert summary['rejected_edge'] == 1

    def test_select_bets_filters_by_confidence(
        self,
        selector,
        sample_analysis_over
    ):
        """Test that bets below confidence threshold are filtered"""
        # Modify analysis to have LOW confidence
        sample_analysis_over.confidence = "LOW"

        selections, summary = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        assert len(selections) == 0
        assert summary['rejected_confidence'] == 1

    def test_select_bets_filters_by_volume(self, selector, sample_analysis_over):
        """Test that bets with low volume are filtered"""
        # Modify prop to have low volume
        sample_analysis_over.prop.volume = 500

        selections, summary = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        assert len(selections) == 0
        assert summary['rejected_volume'] == 1

    def test_select_bets_filters_by_extreme_odds(self, selector, sample_analysis_over):
        """Test that bets with extreme odds are filtered"""
        # Modify prop to have extreme odds
        sample_analysis_over.market_probability = 0.95  # 95% favorite

        selections, summary = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        assert len(selections) == 0
        assert summary['rejected_odds'] == 1

    def test_select_bets_passes_all_criteria(
        self,
        selector,
        sample_analysis_over
    ):
        """Test that bets passing all criteria are selected"""
        selections, summary = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        assert len(selections) == 1
        assert summary['recommended'] == 1

        selection = selections[0]
        assert selection.prop_id == sample_analysis_over.prop_id
        assert selection.action == BetAction.BET_OVER
        assert selection.edge == sample_analysis_over.edge
        assert selection.confidence == sample_analysis_over.confidence

    def test_select_bets_calculates_position_size(self, selector, sample_analysis_over):
        """Test that position size is calculated correctly"""
        selections, _ = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        # Default base unit is 2% = $20
        # MEDIUM confidence with 8% edge should be close to base
        assert selections[0].recommended_size > 0
        assert selections[0].recommended_size <= 50  # Max 5% = $50

    def test_select_bets_high_confidence_multiplier(self, selector, sample_analysis_over):
        """Test that high confidence gets position multiplier"""
        sample_analysis_over.confidence = "HIGH"

        selections_high, _ = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        # Reset to MEDIUM
        sample_analysis_over.confidence = "MEDIUM"
        selections_med, _ = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        # High confidence should have larger position
        assert selections_high[0].recommended_size > selections_med[0].recommended_size

    def test_select_bets_edge_multiplier(self, selector):
        """Test that larger edge gets larger position"""
        # Create two analyses with different edges
        prop = PropData(
            prop_id="test_prop",
            prop_type=PropType.QB_PASSING_YARDS,
            title="Test",
            player_team="Test",
            metric="test",
            line=100.0,
            market_price=50.0,
            market_probability=0.50,
            volume=5000
        )

        analysis_small_edge = PropAnalysisResult(
            prop=prop,
            ai_probability=0.55,  # 5% edge
            market_probability=0.50,
            edge=0.05,
            confidence="MEDIUM",
            recommendation="OVER",
            value_level=PropValueLevel.HIGH,
            reasoning=[],
            risk_factors=[]
        )

        analysis_large_edge = PropAnalysisResult(
            prop=prop,
            ai_probability=0.70,  # 20% edge
            market_probability=0.50,
            edge=0.20,
            confidence="HIGH",
            recommendation="OVER",
            value_level=PropValueLevel.HIGH,
            reasoning=[],
            risk_factors=[]
        )

        selections, _ = selector.select_bets(
            [analysis_small_edge, analysis_large_edge],
            bankroll=1000.0
        )

        # Large edge should have larger position
        large_edge_selection = next(s for s in selections if s.edge == 0.20)
        small_edge_selection = next(s for s in selections if s.edge == 0.05)

        assert large_edge_selection.recommended_size > small_edge_selection.recommended_size

    def test_select_bets_calculates_max_price(self, selector, sample_analysis_over):
        """Test that max price is calculated correctly"""
        selections, _ = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        # Market price is 52 cents, max should be 57 (52 + 5)
        assert selections[0].max_price <= 57
        assert selections[0].max_price > 52

    def test_select_bets_for_under(self, selector, sample_analysis_under):
        """Test selecting UNDER bets"""
        selections, _ = selector.select_bets([sample_analysis_under], bankroll=1000.0)

        assert len(selections) == 1
        assert selections[0].action == BetAction.BET_UNDER
        # Market price 55, max should be 50 (55 - 5)
        assert selections[0].max_price < 55

    def test_select_bets_no_bet(self, selector, sample_analysis_no_bet):
        """Test that NO_BET recommendation is not selected"""
        selections, _ = selector.select_bets([sample_analysis_no_bet], bankroll=1000.0)

        assert len(selections) == 0

    def test_select_bets_sorted_by_edge(self, selector):
        """Test that selected bets are sorted by edge"""
        analyses = []
        for i, edge in enumerate([0.05, 0.15, 0.08, 0.12]):
            prop = PropData(
                prop_id=f"prop_{i}",
                prop_type=PropType.QB_PASSING_YARDS,
                title=f"Prop {i}",
                player_team="Test",
                metric="test",
                line=100.0,
                market_price=50.0,
                market_probability=0.50,
                volume=5000
            )

            analyses.append(PropAnalysisResult(
                prop=prop,
                ai_probability=0.50 + edge,
                market_probability=0.50,
                edge=edge,
                confidence="HIGH",
                recommendation="OVER",
                value_level=PropValueLevel.HIGH,
                reasoning=[],
                risk_factors=[]
            ))

        selections, _ = selector.select_bets(analyses, bankroll=1000.0)

        # Should be sorted by edge descending
        for i in range(len(selections) - 1):
            assert selections[i].edge >= selections[i+1].edge

    def test_filter_by_category(self, selector):
        """Test filtering by category"""
        analyses = []
        # Create multiple props of same type
        for i in range(5):
            prop = PropData(
                prop_id=f"qb_prop_{i}",
                prop_type=PropType.QB_PASSING_YARDS,
                title=f"QB Prop {i}",
                player_team="Test",
                metric="test",
                line=100.0,
                market_price=50.0,
                market_probability=0.50,
                volume=5000
            )

            analyses.append(PropAnalysisResult(
                prop=prop,
                ai_probability=0.60,
                market_probability=0.50,
                edge=0.10,
                confidence="HIGH",
                recommendation="OVER",
                value_level=PropValueLevel.HIGH,
                reasoning=[],
                risk_factors=[]
            ))

        # Filter to max 2 per category
        filtered = selector.filter_by_category(analyses, max_per_category=2)

        # Should only have 2 QB props
        qb_count = sum(1 for a in filtered if a.prop.prop_type == PropType.QB_PASSING_YARDS)
        assert qb_count == 2

    def test_check_correlation_qb_props(self, selector):
        """Test correlation check for QB props"""
        correlation = selector.check_correlation("chiefs_qb_passing", "eagles_qb_passing")

        # QB props on different teams should have some correlation
        assert correlation > 0

    def test_check_correlation_wr_props(self, selector):
        """Test correlation check for WR props"""
        correlation = selector.check_correlation("chiefs_wr_receptions", "chiefs_wr_yards")

        # WR props on same team should have correlation
        assert correlation > 0

    def test_check_correlation_player_and_game(self, selector):
        """Test correlation check for player and game props"""
        correlation = selector.check_correlation("chiefs_qb_passing", "chiefs_team_total")

        # Player and game props should have some correlation
        assert correlation > 0

    def test_get_selection_summary(self, selector, sample_analysis_over):
        """Test getting selection summary"""
        selections, _ = selector.select_bets([sample_analysis_over], bankroll=1000.0)

        summary = selector.get_selection_summary(selections)

        assert summary['total_bets'] == 1
        assert summary['total_exposure'] > 0
        assert summary['avg_edge'] == sample_analysis_over.edge
        assert summary['medium_confidence'] == 1
        assert summary['high_confidence'] == 0
        assert 'qb_passing_yards' in summary['by_category']

    def test_get_selection_summary_empty(self, selector):
        """Test getting summary for empty selections"""
        summary = selector.get_selection_summary([])

        assert summary['total_bets'] == 0
        assert summary['total_exposure'] == 0
        assert summary['avg_edge'] == 0
