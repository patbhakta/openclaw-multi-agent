"""
Line Tracker - Tracks line movements and detects value opportunities
Monitors market prices and identifies when lines move in value zones
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class PriceSnapshot:
    """A snapshot of a prop's price at a specific time"""
    prop_id: str
    price: float  # Price in cents (0-100)
    volume: int  # Trading volume at this price
    timestamp: datetime
    is_opening: bool = False
    is_current: bool = False


@dataclass
class LineMovement:
    """Represents a significant line movement"""
    prop_id: str
    start_price: float
    end_price: float
    start_time: datetime
    end_time: datetime
    pct_change: float
    volume: int
    movement_type: str  # "UP", "DOWN", "SIDEWAYS"


@dataclass
class ValueOpportunity:
    """A value opportunity detected through line tracking"""
    prop_id: str
    prop_type: str
    title: str
    current_price: float
    our_price: float  # What we believe the fair price is
    edge: float  # Edge in percentage points
    confidence: str  # Confidence in the value
    reason: str
    detected_at: datetime
    line_movement: Optional[LineMovement] = None


class LineTracker:
    """Tracks line movements and detects value opportunities"""

    def __init__(self, history_length: int = 100):
        """
        Initialize line tracker

        Args:
            history_length: Number of price snapshots to keep per prop
        """
        self.history_length = history_length
        self.price_history: Dict[str, deque] = {}
        self.opening_prices: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)

    def add_snapshot(self, prop_id: str, price: float, volume: int, is_opening: bool = False):
        """
        Add a price snapshot

        Args:
            prop_id: Prop ID
            price: Current price in cents
            volume: Trading volume
            is_opening: Whether this is the opening price
        """
        if prop_id not in self.price_history:
            self.price_history[prop_id] = deque(maxlen=self.history_length)

        snapshot = PriceSnapshot(
            prop_id=prop_id,
            price=price,
            volume=volume,
            timestamp=datetime.now(),
            is_opening=is_opening,
            is_current=True
        )

        # Mark previous snapshot as not current
        if self.price_history[prop_id]:
            self.price_history[prop_id][-1].is_current = False

        self.price_history[prop_id].append(snapshot)

        # Store opening price
        if is_opening:
            self.opening_prices[prop_id] = price

    def get_current_price(self, prop_id: str) -> Optional[float]:
        """Get current price for a prop"""
        if prop_id not in self.price_history or not self.price_history[prop_id]:
            return None
        return self.price_history[prop_id][-1].price

    def get_opening_price(self, prop_id: str) -> Optional[float]:
        """Get opening price for a prop"""
        return self.opening_prices.get(prop_id)

    def get_price_history(self, prop_id: str, max_age_hours: int = 24) -> List[PriceSnapshot]:
        """
        Get price history for a prop

        Args:
            prop_id: Prop ID
            max_age_hours: Maximum age of snapshots to return

        Returns:
            List of price snapshots
        """
        if prop_id not in self.price_history:
            return []

        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        return [s for s in self.price_history[prop_id] if s.timestamp >= cutoff]

    def calculate_line_movement(
        self,
        prop_id: str,
        window_minutes: int = 60
    ) -> Optional[LineMovement]:
        """
        Calculate line movement over a time window

        Args:
            prop_id: Prop ID
            window_minutes: Time window in minutes

        Returns:
            LineMovement object or None
        """
        history = self.get_price_history(prop_id, max_age_hours=window_minutes // 60 + 1)

        if len(history) < 2:
            return None

        start = history[0]
        end = history[-1]

        start_price = start.price
        end_price = end.price
        pct_change = (end_price - start_price) / start_price if start_price > 0 else 0

        # Determine movement type
        if abs(pct_change) < 0.02:  # Less than 2% change
            movement_type = "SIDEWAYS"
        elif pct_change > 0:
            movement_type = "UP"
        else:
            movement_type = "DOWN"

        return LineMovement(
            prop_id=prop_id,
            start_price=start_price,
            end_price=end_price,
            start_time=start.timestamp,
            end_time=end.timestamp,
            pct_change=pct_change,
            volume=end.volume,
            movement_type=movement_type
        )

    def detect_value_opportunity(
        self,
        prop_id: str,
        prop_type: str,
        title: str,
        ai_probability: float,
        market_price: float
    ) -> Optional[ValueOpportunity]:
        """
        Detect value opportunity by comparing AI probability to market price

        Args:
            prop_id: Prop ID
            prop_type: Type of prop
            title: Prop title
            ai_probability: Our calculated probability
            market_price: Current market price in cents

        Returns:
            ValueOpportunity or None
        """
        # Convert market price to probability
        market_probability = market_price / 100.0

        # Calculate edge
        edge = ai_probability - market_probability

        # Edge threshold: 5% minimum (from research)
        min_edge = 0.05

        if abs(edge) < min_edge:
            return None

        # Determine confidence based on edge size and line movement
        movement = self.calculate_line_movement(prop_id)
        confidence = self._determine_confidence(edge, movement)

        # Generate reason
        reason = self._generate_value_reason(prop_type, edge, movement)

        # Determine our price
        if edge > 0:
            our_price = market_price + (edge * 100)
        else:
            our_price = market_price - (edge * 100)

        return ValueOpportunity(
            prop_id=prop_id,
            prop_type=prop_type,
            title=title,
            current_price=market_price,
            our_price=our_price,
            edge=edge,
            confidence=confidence,
            reason=reason,
            detected_at=datetime.now(),
            line_movement=movement
        )

    def _determine_confidence(
        self,
        edge: float,
        movement: Optional[LineMovement]
    ) -> str:
        """Determine confidence level in value opportunity"""
        edge_magnitude = abs(edge)

        # High edge = high confidence
        if edge_magnitude >= 0.15:
            return "HIGH"
        elif edge_magnitude >= 0.08:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_value_reason(
        self,
        prop_type: str,
        edge: float,
        movement: Optional[LineMovement]
    ) -> str:
        """Generate reason for value opportunity"""
        reasons = []

        if edge > 0:
            reasons.append(f"AI probability exceeds market by {edge*100:.1f}%")
        else:
            reasons.append(f"Market probability exceeds AI by {abs(edge)*100:.1f}%")

        if movement:
            if movement.movement_type == "UP" and edge > 0:
                reasons.append(f"Line moved up {movement.pct_change*100:.1f}% (following sharp money)")
            elif movement.movement_type == "DOWN" and edge > 0:
                reasons.append(f"Line moved down {movement.pct_change*100:.1f}% (value created)")

        # Add prop-specific reasoning
        if "qb" in prop_type.lower():
            reasons.append("QB passing props have high value")
        elif "wr" in prop_type.lower():
            reasons.append("WR reception props have consistent target volume")

        return ", ".join(reasons)

    def get_all_value_opportunities(
        self,
        props_data: Dict[str, Dict],
        ai_probabilities: Dict[str, float]
    ) -> List[ValueOpportunity]:
        """
        Get all current value opportunities

        Args:
            props_data: Dictionary of prop_id -> prop details
            ai_probabilities: Dictionary of prop_id -> AI probability

        Returns:
            List of value opportunities
        """
        opportunities = []

        for prop_id, prop_details in props_data.items():
            current_price = self.get_current_price(prop_id)
            if current_price is None:
                continue

            ai_prob = ai_probabilities.get(prop_id)
            if ai_prob is None:
                continue

            opportunity = self.detect_value_opportunity(
                prop_id=prop_id,
                prop_type=prop_details.get('prop_type', ''),
                title=prop_details.get('title', ''),
                ai_probability=ai_prob,
                market_price=current_price
            )

            if opportunity:
                opportunities.append(opportunity)

        # Sort by edge (highest first)
        opportunities.sort(key=lambda x: abs(x.edge), reverse=True)

        return opportunities

    def get_market_summary(self) -> Dict:
        """Get summary of market data"""
        summary = {
            'total_props_tracked': len(self.price_history),
            'props_with_opening_price': len(self.opening_prices),
            'recent_movements': []
        }

        # Get recent significant line movements
        for prop_id in self.price_history.keys():
            movement = self.calculate_line_movement(prop_id, window_minutes=60)
            if movement and abs(movement.pct_change) >= 0.05:  # 5%+ movement
                summary['recent_movements'].append({
                    'prop_id': prop_id,
                    'movement_type': movement.movement_type,
                    'pct_change': movement.pct_change * 100,
                    'start_price': movement.start_price,
                    'end_price': movement.end_price
                })

        return summary

    def clear_old_data(self, hours: int = 24):
        """
        Clear old price data

        Args:
            hours: Keep data newer than this many hours
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        for prop_id in list(self.price_history.keys()):
            # Filter out old snapshots
            self.price_history[prop_id] = deque(
                [s for s in self.price_history[prop_id] if s.timestamp >= cutoff],
                maxlen=self.history_length
            )

            # Remove props with no recent data
            if not self.price_history[prop_id]:
                del self.price_history[prop_id]
                if prop_id in self.opening_prices:
                    del self.opening_prices[prop_id]


def test_line_tracker():
    """Test the line tracker"""
    tracker = LineTracker()

    # Simulate price movements
    print("Simulating price movements...")

    # Opening price
    tracker.add_snapshot("prop_1", price=50.0, volume=1000, is_opening=True)
    print(f"Opening: prop_1 @ 50¢")

    # Price moves up
    tracker.add_snapshot("prop_1", price=52.0, volume=1500)
    print(f"Update: prop_1 @ 52¢")

    # Price moves more
    tracker.add_snapshot("prop_1", price=55.0, volume=2000)
    print(f"Update: prop_1 @ 55¢")

    # Check line movement
    movement = tracker.calculate_line_movement("prop_1")
    if movement:
        print(f"\nLine movement: {movement.movement_type} {movement.pct_change*100:.1f}%")

    # Detect value opportunity
    opportunity = tracker.detect_value_opportunity(
        prop_id="prop_1",
        prop_type="qb_passing_yards",
        title="QB Passing Yards Over/Under",
        ai_probability=0.60,  # Our probability: 60%
        market_price=55.0  # Market price: 55%
    )

    if opportunity:
        print(f"\nValue Opportunity Detected!")
        print(f"  Current price: {opportunity.current_price}¢")
        print(f"  Our price: {opportunity.our_price:.1f}¢")
        print(f"  Edge: {opportunity.edge*100:.1f}%")
        print(f"  Confidence: {opportunity.confidence}")
        print(f"  Reason: {opportunity.reason}")

    # Market summary
    summary = tracker.get_market_summary()
    print(f"\nMarket Summary:")
    print(f"  Props tracked: {summary['total_props_tracked']}")
    print(f"  Recent movements: {len(summary['recent_movements'])}")


if __name__ == "__main__":
    test_line_tracker()
