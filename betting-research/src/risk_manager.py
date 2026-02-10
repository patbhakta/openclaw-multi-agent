"""
Risk Manager - Implements risk management framework
Kelly criterion, position sizing, diversification
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for betting"""
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


@dataclass
class RiskParameters:
    """Risk management parameters"""
    bankroll: float
    risk_level: RiskLevel = RiskLevel.MODERATE
    max_total_exposure: float = 0.20  # Max 20% of bankroll in play at once
    max_single_bet: float = 0.05  # Max 5% of bankroll on single prop
    daily_loss_limit: float = 0.10  # Stop after 10% daily loss
    max_bets_per_day: int = 20  # Don't over-bet
    stop_loss_pct: float = 0.10  # Exit position at 10% loss
    take_profit_pct: float = 0.15  # Take profit at 15% gain


@dataclass
class Position:
    """A betting position"""
    prop_id: str
    action: str  # "OVER" or "UNDER"
    entry_price: float  # Entry price in cents
    quantity: int  # Number of contracts
    cost: float  # Total cost
    current_price: float  # Current market price
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    status: str = "OPEN"  # OPEN, CLOSED, STOPPED
    entry_time: str = ""
    exit_time: str = ""
    stop_loss: float = 0.0
    take_profit: float = 0.0


@dataclass
class RiskMetrics:
    """Current risk metrics"""
    total_exposure: float  # Total money at risk
    total_positions: int  # Number of open positions
    daily_pnl: float  # Today's P&L
    daily_bets: int  # Today's bets
    max_drawdown: float  # Maximum drawdown
    sharpe_ratio: Optional[float] = None  # Risk-adjusted return
    win_rate: float = 0.0  # Win rate percentage


class RiskManager:
    """Manages betting risk using Kelly criterion and risk controls"""

    # Risk level configurations
    RISK_CONFIGS = {
        RiskLevel.CONSERVATIVE: {
            'max_total_exposure': 0.10,
            'max_single_bet': 0.02,
            'kelly_fraction': 0.25,  # Quarter Kelly
        },
        RiskLevel.MODERATE: {
            'max_total_exposure': 0.20,
            'max_single_bet': 0.05,
            'kelly_fraction': 0.50,  # Half Kelly
        },
        RiskLevel.AGGRESSIVE: {
            'max_total_exposure': 0.30,
            'max_single_bet': 0.08,
            'kelly_fraction': 0.75,  # Three-quarter Kelly
        },
    }

    def __init__(self, risk_params: Optional[RiskParameters] = None):
        self.risk_params = risk_params or RiskParameters(bankroll=1000.0)
        self.positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.daily_pnl = 0.0
        self.daily_bets = 0
        self.logger = logging.getLogger(__name__)

    def calculate_kelly_position(
        self,
        edge: float,
        probability: float,
        odds: float = 1.0
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion

        Kelly Criterion: f = (bp - q) / b
        Where:
        - f = fraction of bankroll to bet
        - b = odds (decimal)
        - p = probability of winning
        - q = probability of losing (1 - p)

        Args:
            edge: Edge as decimal (e.g., 0.08 for 8%)
            probability: Probability of winning (0-1)
            odds: Decimal odds (default 1:1 for prediction markets)

        Returns:
            Fraction of bankroll to bet (0-1)
        """
        q = 1 - probability

        # Kelly formula
        if odds <= 0:
            return 0.0

        f = (odds * probability - q) / odds

        # Ensure non-negative
        f = max(0, f)

        # Apply Kelly fraction based on risk level
        config = self.RISK_CONFIGS[self.risk_params.risk_level]
        kelly_fraction = config['kelly_fraction']

        return min(f * kelly_fraction, self.risk_params.max_single_bet)

    def check_bet_allowed(self, position_size: float) -> Tuple[bool, str]:
        """
        Check if a bet is allowed given current risk parameters

        Args:
            position_size: Proposed position size in $

        Returns:
            Tuple of (allowed, reason)
        """
        # Check total exposure
        current_exposure = sum(p.cost for p in self.positions)
        new_exposure = current_exposure + position_size
        max_exposure = self.risk_params.bankroll * self.risk_params.max_total_exposure

        if new_exposure > max_exposure:
            return False, f"Would exceed max total exposure ({new_exposure:.2f} > {max_exposure:.2f})"

        # Check single bet size
        max_single = self.risk_params.bankroll * self.risk_params.max_single_bet
        if position_size > max_single:
            return False, f"Position size exceeds max single bet ({position_size:.2f} > {max_single:.2f})"

        # Check daily loss limit
        if self.daily_pnl < -(self.risk_params.bankroll * self.risk_params.daily_loss_limit):
            return False, f"Daily loss limit reached (${self.daily_pnl:.2f})"

        # Check max bets per day
        if self.daily_bets >= self.risk_params.max_bets_per_day:
            return False, f"Max bets per day reached ({self.daily_bets})"

        return True, "OK"

    def open_position(
        self,
        prop_id: str,
        action: str,
        price: float,
        quantity: int
    ) -> Tuple[bool, str]:
        """
        Open a new position

        Args:
            prop_id: Prop ID
            action: "OVER" or "UNDER"
            price: Entry price in cents
            quantity: Number of contracts

        Returns:
            Tuple of (success, message)
        """
        cost = (price / 100.0) * quantity

        # Check if bet is allowed
        allowed, reason = self.check_bet_allowed(cost)
        if not allowed:
            return False, reason

        # Calculate stop loss and take profit
        if action == "OVER":
            stop_loss = price * (1 - self.risk_params.stop_loss_pct)
            take_profit = price * (1 + self.risk_params.take_profit_pct)
        else:  # UNDER
            stop_loss = price * (1 + self.risk_params.stop_loss_pct)
            take_profit = price * (1 - self.risk_params.take_profit_pct)

        position = Position(
            prop_id=prop_id,
            action=action,
            entry_price=price,
            quantity=quantity,
            cost=cost,
            current_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        self.positions.append(position)
        self.daily_bets += 1

        return True, f"Position opened: {prop_id} {action} @ {price}¢"

    def update_positions(self, market_prices: Dict[str, float]) -> List[Dict]:
        """
        Update all positions with current market prices

        Args:
            market_prices: Dictionary of prop_id -> current_price

        Returns:
            List of positions that hit stop loss or take profit
        """
        positions_to_close = []

        for position in self.positions:
            if position.prop_id in market_prices:
                position.current_price = market_prices[position.prop_id]

                # Calculate unrealized P&L
                if position.action == "OVER":
                    # Long position
                    pnl = (position.current_price - position.entry_price) / 100.0 * position.quantity
                else:  # UNDER
                    # Short position
                    pnl = (position.entry_price - position.current_price) / 100.0 * position.quantity

                position.unrealized_pnl = pnl

                # Check stop loss
                if position.action == "OVER" and position.current_price <= position.stop_loss:
                    position.status = "STOPPED"
                    positions_to_close.append(position)

                elif position.action == "UNDER" and position.current_price >= position.stop_loss:
                    position.status = "STOPPED"
                    positions_to_close.append(position)

                # Check take profit
                if position.action == "OVER" and position.current_price >= position.take_profit:
                    position.status = "PROFIT"
                    positions_to_close.append(position)

                elif position.action == "UNDER" and position.current_price <= position.take_profit:
                    position.status = "PROFIT"
                    positions_to_close.append(position)

        return positions_to_close

    def close_position(self, prop_id: str, exit_price: Optional[float] = None) -> Tuple[bool, str]:
        """
        Close a position

        Args:
            prop_id: Prop ID to close
            exit_price: Exit price (uses current_price if None)

        Returns:
            Tuple of (success, message)
        """
        position = None
        for i, pos in enumerate(self.positions):
            if pos.prop_id == prop_id:
                position = pos
                break

        if not position:
            return False, f"Position not found: {prop_id}"

        if exit_price is None:
            exit_price = position.current_price

        # Calculate realized P&L
        if position.action == "OVER":
            pnl = (exit_price - position.entry_price) / 100.0 * position.quantity
        else:  # UNDER
            pnl = (position.entry_price - exit_price) / 100.0 * position.quantity

        position.realized_pnl = pnl
        position.current_price = exit_price
        position.status = "CLOSED"

        # Move to closed positions
        self.positions.remove(position)
        self.closed_positions.append(position)
        self.daily_pnl += pnl

        return True, f"Position closed: {prop_id} P&L: ${pnl:.2f}"

    def get_risk_metrics(self) -> RiskMetrics:
        """Get current risk metrics"""
        total_exposure = sum(p.cost for p in self.positions)

        # Calculate max drawdown from closed positions
        if self.closed_positions:
            peak = max(self.daily_pnl for _ in self.closed_positions)
            max_drawdown = min(p.realized_pnl for p in self.closed_positions) - peak
        else:
            max_drawdown = 0.0

        # Calculate win rate
        wins = sum(1 for p in self.closed_positions if p.realized_pnl > 0)
        total = len(self.closed_positions)
        win_rate = wins / total if total > 0 else 0.0

        return RiskMetrics(
            total_exposure=total_exposure,
            total_positions=len(self.positions),
            daily_pnl=self.daily_pnl,
            daily_bets=self.daily_bets,
            max_drawdown=max_drawdown,
            win_rate=win_rate
        )

    def check_diversification(self, prop_ids: List[str]) -> Tuple[bool, str]:
        """
        Check if adding these props would maintain proper diversification

        Args:
            prop_ids: List of prop IDs being considered

        Returns:
            Tuple of (diversified, reason)
        """
        # Count props by type
        prop_types = {}
        for prop_id in prop_ids:
            if 'qb' in prop_id.lower():
                prop_type = 'QB'
            elif 'wr' in prop_id.lower():
                prop_type = 'WR'
            elif 'rb' in prop_id.lower():
                prop_type = 'RB'
            elif 'team' in prop_id.lower():
                prop_type = 'TEAM'
            else:
                prop_type = 'OTHER'

            prop_types[prop_type] = prop_types.get(prop_type, 0) + 1

        # Check if any category has too many positions
        for prop_type, count in prop_types.items():
            if count > 3:
                return False, f"Too many {prop_type} props ({count} > 3)"

        # Check team diversification (simplified)
        teams = set()
        for prop_id in prop_ids:
            if 'chiefs' in prop_id.lower():
                teams.add('CHIEFS')
            elif 'eagles' in prop_id.lower():
                teams.add('EAGLES')

        if len(teams) < 2:
            return False, f"Not diversified enough ({len(teams)} teams)"

        return True, "Properly diversified"

    def reset_daily(self):
        """Reset daily metrics (called at start of new day)"""
        self.daily_pnl = 0.0
        self.daily_bets = 0

    def get_position_summary(self) -> Dict:
        """Get summary of all positions"""
        open_positions = {
            'count': len(self.positions),
            'total_cost': sum(p.cost for p in self.positions),
            'unrealized_pnl': sum(p.unrealized_pnl for p in self.positions),
            'positions': [
                {
                    'prop_id': p.prop_id,
                    'action': p.action,
                    'entry_price': p.entry_price,
                    'current_price': p.current_price,
                    'quantity': p.quantity,
                    'unrealized_pnl': p.unrealized_pnl,
                    'status': p.status
                }
                for p in self.positions
            ]
        }

        closed_positions = {
            'count': len(self.closed_positions),
            'total_pnl': sum(p.realized_pnl for p in self.closed_positions),
            'positions': [
                {
                    'prop_id': p.prop_id,
                    'action': p.action,
                    'entry_price': p.entry_price,
                    'exit_price': p.current_price,
                    'realized_pnl': p.realized_pnl,
                    'status': p.status
                }
                for p in self.closed_positions
            ]
        }

        return {
            'open': open_positions,
            'closed': closed_positions
        }


def test_risk_manager():
    """Test the risk manager"""
    risk_params = RiskParameters(bankroll=1000.0, risk_level=RiskLevel.MODERATE)
    rm = RiskManager(risk_params)

    # Test Kelly calculation
    kelly_pos = rm.calculate_kelly_position(edge=0.08, probability=0.58)
    print(f"Kelly position: {kelly_pos*100:.2f}% of bankroll (${kelly_pos*1000:.2f})")

    # Test opening position
    success, msg = rm.open_position(
        prop_id="test_qb_passing_yards",
        action="OVER",
        price=52.0,
        quantity=10
    )
    print(f"Open position: {success} - {msg}")

    # Check risk metrics
    metrics = rm.get_risk_metrics()
    print(f"\nRisk Metrics:")
    print(f"  Total exposure: ${metrics.total_exposure:.2f}")
    print(f"  Open positions: {metrics.total_positions}")
    print(f"  Daily bets: {metrics.daily_bets}")

    # Test position update
    market_prices = {"test_qb_passing_yards": 55.0}
    to_close = rm.update_positions(market_prices)
    print(f"\nPositions to close: {len(to_close)}")

    # Close position
    success, msg = rm.close_position("test_qb_passing_yards")
    print(f"Close position: {success} - {msg}")


if __name__ == "__main__":
    test_risk_manager()
