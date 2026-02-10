"""
Unit tests for Risk Manager
"""

import pytest
from src.risk_manager import (
    RiskManager, RiskParameters, RiskLevel, Position, RiskMetrics
)


@pytest.fixture
def moderate_risk_params():
    """Create moderate risk parameters"""
    return RiskParameters(
        bankroll=1000.0,
        risk_level=RiskLevel.MODERATE
    )


@pytest.fixture
def rm(moderate_risk_params):
    """Create a RiskManager instance"""
    return RiskManager(risk_params=moderate_risk_params)


class TestRiskParameters:
    """Test RiskParameters dataclass"""

    def test_default_values(self):
        """Test default parameter values"""
        params = RiskParameters(bankroll=1000.0)

        assert params.risk_level == RiskLevel.MODERATE
        assert params.max_total_exposure == 0.20
        assert params.max_single_bet == 0.05
        assert params.daily_loss_limit == 0.10
        assert params.stop_loss_pct == 0.10
        assert params.take_profit_pct == 0.15


class TestRiskManager:
    """Test RiskManager functionality"""

    def test_kelly_calculation_positive_edge(self, rm):
        """Test Kelly criterion with positive edge"""
        position_size = rm.calculate_kelly_position(
            edge=0.08,
            probability=0.58,
            odds=1.0
        )

        # Kelly formula: f = (1.0 * 0.58 - 0.42) / 1.0 = 0.16
        # Half Kelly: 0.16 * 0.5 = 0.08 = 8%
        assert position_size > 0
        assert position_size <= rm.risk_params.max_single_bet

    def test_kelly_calculation_negative_edge(self, rm):
        """Test Kelly criterion with negative edge"""
        position_size = rm.calculate_kelly_position(
            edge=-0.05,
            probability=0.45,
            odds=1.0
        )

        # Negative edge = no bet
        assert position_size == 0

    def test_kelly_high_confidence(self, rm):
        """Test Kelly with high edge and probability"""
        position_size = rm.calculate_kelly_position(
            edge=0.20,
            probability=0.70,
            odds=1.0
        )

        # High edge should give larger position
        assert position_size > rm.calculate_kelly_position(
            edge=0.08,
            probability=0.58,
            odds=1.0
        )

    def test_kelly_different_risk_levels(self):
        """Test Kelly with different risk levels"""
        params_conservative = RiskParameters(bankroll=1000.0, risk_level=RiskLevel.CONSERVATIVE)
        params_aggressive = RiskParameters(bankroll=1000.0, risk_level=RiskLevel.AGGRESSIVE)

        rm_conservative = RiskManager(params_conservative)
        rm_aggressive = RiskManager(params_aggressive)

        pos_conservative = rm_conservative.calculate_kelly_position(
            edge=0.08, probability=0.58, odds=1.0
        )
        pos_aggressive = rm_aggressive.calculate_kelly_position(
            edge=0.08, probability=0.58, odds=1.0
        )

        # Aggressive should bet more than conservative
        assert pos_aggressive > pos_conservative

    def test_bet_allowed_within_limits(self, rm):
        """Test checking if bet is allowed within limits"""
        allowed, reason = rm.check_bet_allowed(position_size=20.0)

        assert allowed is True
        assert reason == "OK"

    def test_bet_not_allowed_exceeds_total_exposure(self, rm):
        """Test checking if bet exceeds total exposure"""
        # Open positions to reach max exposure
        rm.open_position("prop_1", "OVER", 50.0, 80)
        rm.open_position("prop_2", "OVER", 50.0, 80)
        rm.open_position("prop_3", "OVER", 50.0, 80)
        rm.open_position("prop_4", "OVER", 50.0, 80)

        # Try to add another position
        allowed, reason = rm.check_bet_allowed(position_size=20.0)

        assert allowed is False
        assert "exceeds max total exposure" in reason.lower()

    def test_bet_not_allowed_exceeds_single_bet(self, rm):
        """Test checking if bet exceeds single bet limit"""
        # Try to bet more than 5% of bankroll
        allowed, reason = rm.check_bet_allowed(position_size=60.0)

        assert allowed is False
        assert "exceeds max single bet" in reason.lower()

    def test_bet_not_allowed_daily_loss_limit(self, rm):
        """Test checking if daily loss limit reached"""
        # Simulate daily loss
        rm.daily_pnl = -150.0  # 15% loss > 10% limit

        allowed, reason = rm.check_bet_allowed(position_size=20.0)

        assert allowed is False
        assert "daily loss limit reached" in reason.lower()

    def test_bet_not_allowed_max_bets_per_day(self, rm):
        """Test checking if max bets per day reached"""
        rm.daily_bets = 25  # Exceeds default of 20

        allowed, reason = rm.check_bet_allowed(position_size=20.0)

        assert allowed is False
        assert "max bets per day" in reason.lower()

    def test_open_position_success(self, rm):
        """Test successfully opening a position"""
        success, message = rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=52.0,
            quantity=10
        )

        assert success is True
        assert len(rm.positions) == 1
        assert rm.positions[0].prop_id == "test_prop"
        assert rm.positions[0].action == "OVER"
        assert rm.positions[0].entry_price == 52.0
        assert rm.positions[0].quantity == 10
        assert rm.daily_bets == 1

    def test_open_position_calculates_cost(self, rm):
        """Test that position cost is calculated correctly"""
        rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=52.0,
            quantity=10
        )

        # Cost = 52 cents * 10 = $5.20
        assert rm.positions[0].cost == 5.20

    def test_open_position_calculates_stop_loss_take_profit_over(self, rm):
        """Test stop loss and take profit calculation for OVER position"""
        rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=50.0,
            quantity=10
        )

        # Stop loss = 50 * (1 - 0.10) = 45
        assert rm.positions[0].stop_loss == 45.0
        # Take profit = 50 * (1 + 0.15) = 57.5
        assert rm.positions[0].take_profit == 57.5

    def test_open_position_calculates_stop_loss_take_profit_under(self, rm):
        """Test stop loss and take profit calculation for UNDER position"""
        rm.open_position(
            prop_id="test_prop",
            action="UNDER",
            price=50.0,
            quantity=10
        )

        # Stop loss = 50 * (1 + 0.10) = 55
        assert rm.positions[0].stop_loss == 55.0
        # Take profit = 50 * (1 - 0.15) = 42.5
        assert rm.positions[0].take_profit == 42.5

    def test_update_positions_with_price_increase(self, rm):
        """Test updating positions with price increase"""
        rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=50.0,
            quantity=10
        )

        market_prices = {"test_prop": 55.0}
        to_close = rm.update_positions(market_prices)

        # Should calculate positive P&L
        assert rm.positions[0].current_price == 55.0
        assert rm.positions[0].unrealized_pnl > 0
        # (55 - 50) / 100 * 10 = $0.50
        assert abs(rm.positions[0].unrealized_pnl - 0.50) < 0.01

    def test_update_positions_with_price_decrease(self, rm):
        """Test updating positions with price decrease"""
        rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=50.0,
            quantity=10
        )

        market_prices = {"test_prop": 45.0}
        to_close = rm.update_positions(market_prices)

        # Should calculate negative P&L
        assert rm.positions[0].current_price == 45.0
        assert rm.positions[0].unrealized_pnl < 0

    def test_update_positions_stop_loss_triggered(self, rm):
        """Test that stop loss is triggered"""
        rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=50.0,
            quantity=10
        )

        # Price goes below stop loss (45)
        market_prices = {"test_prop": 44.0}
        to_close = rm.update_positions(market_prices)

        assert len(to_close) == 1
        assert to_close[0].status == "STOPPED"

    def test_update_positions_take_profit_triggered(self, rm):
        """Test that take profit is triggered"""
        rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=50.0,
            quantity=10
        )

        # Price goes above take profit (57.5)
        market_prices = {"test_prop": 58.0}
        to_close = rm.update_positions(market_prices)

        assert len(to_close) == 1
        assert to_close[0].status == "PROFIT"

    def test_close_position_success(self, rm):
        """Test closing a position"""
        rm.open_position(
            prop_id="test_prop",
            action="OVER",
            price=50.0,
            quantity=10
        )

        success, message = rm.close_position("test_prop", exit_price=55.0)

        assert success is True
        assert len(rm.positions) == 0
        assert len(rm.closed_positions) == 1
        assert rm.closed_positions[0].realized_pnl == 0.50
        assert rm.daily_pnl == 0.50

    def test_close_position_not_found(self, rm):
        """Test closing a position that doesn't exist"""
        success, message = rm.close_position("nonexistent_prop")

        assert success is False
        assert "not found" in message.lower()

    def test_get_risk_metrics(self, rm):
        """Test getting risk metrics"""
        rm.open_position("prop_1", "OVER", 50.0, 10)
        rm.open_position("prop_2", "UNDER", 50.0, 10)

        metrics = rm.get_risk_metrics()

        assert metrics.total_exposure == 10.0  # 2 positions at $5 each
        assert metrics.total_positions == 2
        assert metrics.daily_bets == 2

    def test_check_diversification_proper(self, rm):
        """Test checking diversification with proper spread"""
        prop_ids = [
            "chiefs_qb_passing_yards",
            "eagles_qb_passing_yards",
            "chiefs_wr_receptions",
            "eagles_wr_receptions"
        ]

        diversified, reason = rm.check_diversification(prop_ids)

        assert diversified is True
        assert reason == "Properly diversified"

    def test_check_diversification_too_many_qb(self, rm):
        """Test checking diversification with too many QB props"""
        prop_ids = [
            "chiefs_qb1_passing_yards",
            "chiefs_qb2_passing_yards",
            "eagles_qb_passing_yards",
            "chiefs_qb3_passing_yards"
        ]

        diversified, reason = rm.check_diversification(prop_ids)

        assert diversified is False
        assert "QB" in reason

    def test_check_diversification_not_enough_teams(self, rm):
        """Test checking diversification without enough teams"""
        prop_ids = [
            "chiefs_qb_passing_yards",
            "chiefs_wr_receptions",
            "chiefs_rb_rushing_yards"
        ]

        diversified, reason = rm.check_diversification(prop_ids)

        assert diversified is False
        assert "Not diversified" in reason

    def test_reset_daily(self, rm):
        """Test resetting daily metrics"""
        rm.daily_pnl = 50.0
        rm.daily_bets = 10

        rm.reset_daily()

        assert rm.daily_pnl == 0.0
        assert rm.daily_bets == 0

    def test_get_position_summary(self, rm):
        """Test getting position summary"""
        rm.open_position("prop_1", "OVER", 50.0, 10)
        rm.close_position("prop_1", exit_price=55.0)

        summary = rm.get_position_summary()

        assert summary['open']['count'] == 0
        assert summary['closed']['count'] == 1
        assert summary['closed']['total_pnl'] == 0.50
