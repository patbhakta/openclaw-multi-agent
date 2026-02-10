"""
Unit tests for Line Tracker
"""

import pytest
from datetime import datetime, timedelta
from src.line_tracker import (
    LineTracker, PriceSnapshot, LineMovement, ValueOpportunity
)


@pytest.fixture
def tracker():
    """Create a LineTracker instance"""
    return LineTracker(history_length=100)


class TestPriceSnapshot:
    """Test PriceSnapshot dataclass"""

    def test_create_snapshot(self):
        """Test creating a price snapshot"""
        snapshot = PriceSnapshot(
            prop_id="test_prop",
            price=50.0,
            volume=1000,
            timestamp=datetime.now()
        )

        assert snapshot.prop_id == "test_prop"
        assert snapshot.price == 50.0
        assert snapshot.volume == 1000
        assert snapshot.is_opening is False
        assert snapshot.is_current is False


class TestLineTracker:
    """Test LineTracker functionality"""

    def test_add_snapshot(self, tracker):
        """Test adding a price snapshot"""
        tracker.add_snapshot(
            prop_id="test_prop",
            price=50.0,
            volume=1000
        )

        assert "test_prop" in tracker.price_history
        assert len(tracker.price_history["test_prop"]) == 1
        assert tracker.price_history["test_prop"][0].price == 50.0

    def test_add_opening_price(self, tracker):
        """Test adding opening price"""
        tracker.add_snapshot(
            prop_id="test_prop",
            price=50.0,
            volume=1000,
            is_opening=True
        )

        assert "test_prop" in tracker.opening_prices
        assert tracker.opening_prices["test_prop"] == 50.0

    def test_add_multiple_snapshots(self, tracker):
        """Test adding multiple snapshots for same prop"""
        tracker.add_snapshot("test_prop", 50.0, 1000)
        tracker.add_snapshot("test_prop", 52.0, 1500)
        tracker.add_snapshot("test_prop", 55.0, 2000)

        assert len(tracker.price_history["test_prop"]) == 3

        # Check only latest is marked as current
        assert tracker.price_history["test_prop"][2].is_current is True
        assert tracker.price_history["test_prop"][1].is_current is False

    def test_get_current_price(self, tracker):
        """Test getting current price"""
        tracker.add_snapshot("test_prop", 50.0, 1000)
        tracker.add_snapshot("test_prop", 52.0, 1500)

        current = tracker.get_current_price("test_prop")

        assert current == 52.0

    def test_get_current_price_not_found(self, tracker):
        """Test getting current price for non-existent prop"""
        current = tracker.get_current_price("nonexistent")

        assert current is None

    def test_get_opening_price(self, tracker):
        """Test getting opening price"""
        tracker.add_snapshot(
            prop_id="test_prop",
            price=50.0,
            volume=1000,
            is_opening=True
        )
        tracker.add_snapshot("test_prop", 52.0, 1500)

        opening = tracker.get_opening_price("test_prop")

        assert opening == 50.0

    def test_get_price_history(self, tracker):
        """Test getting price history"""
        tracker.add_snapshot("test_prop", 50.0, 1000)
        tracker.add_snapshot("test_prop", 52.0, 1500)
        tracker.add_snapshot("test_prop", 55.0, 2000)

        history = tracker.get_price_history("test_prop", max_age_hours=24)

        assert len(history) == 3
        assert history[0].price == 50.0  # First snapshot
        assert history[2].price == 55.0  # Last snapshot

    def test_get_price_history_with_age_filter(self, tracker):
        """Test getting price history with age filter"""
        # Add old snapshot
        old_time = datetime.now() - timedelta(hours=25)
        tracker.price_history["test_prop"] = [
            PriceSnapshot("test_prop", 50.0, 1000, old_time)
        ]

        # Add recent snapshot
        tracker.add_snapshot("test_prop", 52.0, 1500)

        history = tracker.get_price_history("test_prop", max_age_hours=24)

        # Should only return recent snapshot
        assert len(history) == 1
        assert history[0].price == 52.0

    def test_calculate_line_movement_up(self, tracker):
        """Test calculating upward line movement"""
        tracker.add_snapshot("test_prop", 50.0, 1000, is_opening=True)
        tracker.add_snapshot("test_prop", 52.0, 1500)
        tracker.add_snapshot("test_prop", 55.0, 2000)

        movement = tracker.calculate_line_movement("test_prop", window_minutes=60)

        assert movement is not None
        assert movement.start_price == 50.0
        assert movement.end_price == 55.0
        assert movement.pct_change == 0.10  # 10% increase
        assert movement.movement_type == "UP"

    def test_calculate_line_movement_down(self, tracker):
        """Test calculating downward line movement"""
        tracker.add_snapshot("test_prop", 55.0, 1000, is_opening=True)
        tracker.add_snapshot("test_prop", 52.0, 1500)
        tracker.add_snapshot("test_prop", 50.0, 2000)

        movement = tracker.calculate_line_movement("test_prop", window_minutes=60)

        assert movement is not None
        assert movement.movement_type == "DOWN"
        assert movement.pct_change < 0

    def test_calculate_line_movement_sideways(self, tracker):
        """Test calculating sideways line movement"""
        tracker.add_snapshot("test_prop", 50.0, 1000, is_opening=True)
        tracker.add_snapshot("test_prop", 50.5, 1500)
        tracker.add_snapshot("test_prop", 50.3, 2000)

        movement = tracker.calculate_line_movement("test_prop", window_minutes=60)

        assert movement is not None
        assert movement.movement_type == "SIDEWAYS"
        assert abs(movement.pct_change) < 0.02

    def test_calculate_line_movement_insufficient_data(self, tracker):
        """Test calculating line movement with insufficient data"""
        tracker.add_snapshot("test_prop", 50.0, 1000)

        movement = tracker.calculate_line_movement("test_prop", window_minutes=60)

        assert movement is None

    def test_detect_value_opportunity_positive_edge(self, tracker):
        """Test detecting value opportunity with positive edge"""
        tracker.add_snapshot("test_prop", 50.0, 1000, is_opening=True)

        opportunity = tracker.detect_value_opportunity(
            prop_id="test_prop",
            prop_type="qb_passing_yards",
            title="Test QB Passing Yards",
            ai_probability=0.60,  # Our probability
            market_price=50.0  # Market price
        )

        assert opportunity is not None
        assert opportunity.prop_id == "test_prop"
        assert opportunity.edge == 0.10  # 10% edge
        assert opportunity.confidence in ["LOW", "MEDIUM", "HIGH"]

    def test_detect_value_opportunity_negative_edge(self, tracker):
        """Test detecting value opportunity with negative edge"""
        tracker.add_snapshot("test_prop", 60.0, 1000, is_opening=True)

        opportunity = tracker.detect_value_opportunity(
            prop_id="test_prop",
            prop_type="qb_passing_yards",
            title="Test QB Passing Yards",
            ai_probability=0.50,  # Our probability
            market_price=60.0  # Market price (higher)
        )

        assert opportunity is not None
        assert opportunity.edge == -0.10  # -10% edge

    def test_detect_value_opportunity_no_edge(self, tracker):
        """Test detecting no value opportunity when edge is too small"""
        tracker.add_snapshot("test_prop", 50.0, 1000, is_opening=True)

        opportunity = tracker.detect_value_opportunity(
            prop_id="test_prop",
            prop_type="qb_passing_yards",
            title="Test QB Passing Yards",
            ai_probability=0.53,  # Only 3% edge
            market_price=50.0
        )

        # 3% edge < 5% threshold, so no opportunity
        assert opportunity is None

    def test_get_all_value_opportunities(self, tracker):
        """Test getting all value opportunities"""
        tracker.add_snapshot("prop_1", 50.0, 1000, is_opening=True)
        tracker.add_snapshot("prop_2", 50.0, 1000, is_opening=True)
        tracker.add_snapshot("prop_3", 50.0, 1000, is_opening=True)

        props_data = {
            "prop_1": {"prop_type": "qb_passing_yards", "title": "QB 1"},
            "prop_2": {"prop_type": "qb_passing_yards", "title": "QB 2"},
            "prop_3": {"prop_type": "qb_passing_yards", "title": "QB 3"}
        }

        ai_probabilities = {
            "prop_1": 0.60,  # 10% edge
            "prop_2": 0.53,  # 3% edge (below threshold)
            "prop_3": 0.45,  # -5% edge (meets threshold)
        }

        opportunities = tracker.get_all_value_opportunities(props_data, ai_probabilities)

        # Should find 2 opportunities (prop_1 and prop_3)
        assert len(opportunities) == 2
        # Should be sorted by edge (highest first)
        assert opportunities[0].prop_id == "prop_1"
        assert opportunities[1].prop_id == "prop_3"

    def test_get_market_summary(self, tracker):
        """Test getting market summary"""
        tracker.add_snapshot("prop_1", 50.0, 1000, is_opening=True)
        tracker.add_snapshot("prop_1", 55.0, 2000)
        tracker.add_snapshot("prop_2", 50.0, 1000, is_opening=True)

        summary = tracker.get_market_summary()

        assert summary['total_props_tracked'] == 2
        assert summary['props_with_opening_price'] == 2
        assert len(summary['recent_movements']) == 1  # prop_1 moved 10%

    def test_clear_old_data(self, tracker):
        """Test clearing old price data"""
        # Add old snapshot
        old_time = datetime.now() - timedelta(hours=25)
        tracker.price_history["old_prop"] = [
            PriceSnapshot("old_prop", 50.0, 1000, old_time)
        ]
        tracker.opening_prices["old_prop"] = 50.0

        # Add recent snapshot
        tracker.add_snapshot("new_prop", 50.0, 1000)

        tracker.clear_old_data(hours=24)

        # Old prop should be removed
        assert "old_prop" not in tracker.price_history
        assert "old_prop" not in tracker.opening_prices
        # New prop should remain
        assert "new_prop" in tracker.price_history

    def test_history_length_limit(self, tracker):
        """Test that history is limited to configured length"""
        tracker = LineTracker(history_length=5)

        # Add 10 snapshots
        for i in range(10):
            tracker.add_snapshot("test_prop", float(50 + i), 1000)

        # Should only keep last 5
        assert len(tracker.price_history["test_prop"]) == 5
