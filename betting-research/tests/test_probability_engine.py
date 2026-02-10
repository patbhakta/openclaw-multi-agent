"""
Unit tests for Probability Engine
"""

import pytest
from src.probability_engine import (
    ProbabilityEngine, ProbabilitySignal, ProbabilityEstimate, SignalSource
)


@pytest.fixture
def engine():
    """Create a ProbabilityEngine instance"""
    return ProbabilityEngine()


@pytest.fixture
def sample_prop_data():
    """Sample prop data"""
    return {
        'prop_type': 'qb_passing_yards',
        'line': 275.0,
        'market_probability': 0.52
    }


@pytest.fixture
def sample_player_stats():
    """Sample player stats"""
    return {
        'season_avg': 285.0,
        'recent_5_avg': 295.0,
        'games_played': 16
    }


@pytest.fixture
def sample_game_context():
    """Sample game context"""
    return {
        'venue_type': 'outdoor',
        'weather_forecast': {
            'wind_speed': 10,
            'precipitation': 'clear'
        },
        'game_script_prediction': 'balanced'
    }


@pytest.fixture
def sample_historical_data():
    """Sample historical data"""
    return {
        'first_score_td_rate': 0.60,
        'total_over_rate': 0.40,
        'player_props_over_rate': 0.55
    }


class TestProbabilityEngine:
    """Test ProbabilityEngine functionality"""

    def test_calculate_probability_with_all_signals(
        self,
        engine,
        sample_prop_data,
        sample_player_stats,
        sample_game_context,
        sample_historical_data
    ):
        """Test calculating probability with all signals"""
        estimate = engine.calculate_probability(
            prop_data=sample_prop_data,
            player_stats=sample_player_stats,
            game_context=sample_game_context,
            historical_data=sample_historical_data
        )

        assert isinstance(estimate, ProbabilityEstimate)
        assert 0 <= estimate.final_probability <= 1
        assert 0 <= estimate.confidence <= 1
        assert len(estimate.signals) > 0

    def test_calculate_probability_with_no_signals(self, engine, sample_prop_data):
        """Test calculating probability with no signals (uses market prob)"""
        estimate = engine.calculate_probability(prop_data=sample_prop_data)

        assert isinstance(estimate, ProbabilityEstimate)
        assert estimate.final_probability == sample_prop_data['market_probability']
        assert len(estimate.signals) == 0
        assert estimate.confidence == 0.3  # Low confidence default

    def test_historical_signal_first_score(self, engine):
        """Test historical signal for first score"""
        prop_data = {'prop_type': 'first_score'}
        historical = {'first_score_td_rate': 0.60}

        signal = engine._historical_signal(prop_data, historical)

        assert signal is not None
        assert signal.source == SignalSource.HISTORICAL
        assert signal.probability == 0.60
        assert signal.confidence > 0.5

    def test_historical_signal_total_points(self, engine):
        """Test historical signal for total points"""
        prop_data = {'prop_type': 'total_points'}
        historical = {'total_over_rate': 0.40}

        signal = engine._historical_signal(prop_data, historical)

        assert signal is not None
        assert signal.probability == 0.40

    def test_player_stats_signal_above_line(self, engine):
        """Test player stats signal when avg > line"""
        prop_data = {'prop_type': 'qb_passing_yards', 'line': 275.0}
        stats = {'season_avg': 285.0, 'recent_5_avg': 295.0, 'games_played': 16}

        signal = engine._player_stats_signal(prop_data, stats)

        assert signal is not None
        assert signal.source == SignalSource.PLAYER_STATS
        assert signal.probability > 0.5  # Above line = higher prob

    def test_player_stats_signal_below_line(self, engine):
        """Test player stats signal when avg < line"""
        prop_data = {'prop_type': 'qb_passing_yards', 'line': 275.0}
        stats = {'season_avg': 260.0, 'recent_5_avg': 255.0, 'games_played': 16}

        signal = engine._player_stats_signal(prop_data, stats)

        assert signal is not None
        assert signal.probability < 0.5  # Below line = lower prob

    def test_player_stats_confidence(self, engine):
        """Test player stats confidence based on games played"""
        prop_data = {'prop_type': 'qb_passing_yards', 'line': 275.0}

        # Full season = high confidence
        stats_full = {'season_avg': 285.0, 'recent_5_avg': 295.0, 'games_played': 16}
        signal_full = engine._player_stats_signal(prop_data, stats_full)
        assert signal_full.confidence >= 0.9

        # Half season = medium confidence
        stats_half = {'season_avg': 285.0, 'recent_5_avg': 295.0, 'games_played': 8}
        signal_half = engine._player_stats_signal(prop_data, stats_half)
        assert signal_half.confidence >= 0.4 and signal_half.confidence < 0.9

    def test_game_context_signal_wind(self, engine):
        """Test game context signal with high wind"""
        prop_data = {'prop_type': 'qb_passing_yards'}
        context = {
            'venue_type': 'outdoor',
            'weather_forecast': {'wind_speed': 20, 'precipitation': 'clear'},
            'game_script_prediction': 'balanced'
        }

        signal = engine._game_context_signal(prop_data, context)

        assert signal is not None
        assert signal.source == SignalSource.GAME_CONTEXT
        assert signal.probability < 0.5  # High wind hurts passing

    def test_game_context_signal_precipitation(self, engine):
        """Test game context signal with rain"""
        prop_data = {'prop_type': 'qb_passing_yards'}
        context = {
            'venue_type': 'outdoor',
            'weather_forecast': {'wind_speed': 10, 'precipitation': 'rain'},
            'game_script_prediction': 'balanced'
        }

        signal = engine._game_context_signal(prop_data, context)

        assert signal is not None
        assert signal.probability < 0.5  # Rain hurts passing

    def test_game_context_signal_pass_heavy(self, engine):
        """Test game context signal with pass-heavy script"""
        prop_data = {'prop_type': 'qb_passing_yards'}
        context = {
            'venue_type': 'outdoor',
            'weather_forecast': {'wind_speed': 5, 'precipitation': 'clear'},
            'game_script_prediction': 'pass_heavy'
        }

        signal = engine._game_context_signal(prop_data, context)

        assert signal is not None
        assert signal.probability > 0.5  # Pass-heavy helps passing props

    def test_game_context_signal_run_heavy_qb(self, engine):
        """Test game context signal with run-heavy script for QB prop"""
        prop_data = {'prop_type': 'qb_passing_yards'}
        context = {
            'venue_type': 'outdoor',
            'weather_forecast': {'wind_speed': 5, 'precipitation': 'clear'},
            'game_script_prediction': 'run_heavy'
        }

        signal = engine._game_context_signal(prop_data, context)

        assert signal is not None
        assert signal.probability < 0.5  # Run-heavy hurts passing props

    def test_game_context_signal_run_heavy_rb(self, engine):
        """Test game context signal with run-heavy script for RB prop"""
        prop_data = {'prop_type': 'rb_rushing_yards'}
        context = {
            'venue_type': 'outdoor',
            'weather_forecast': {'wind_speed': 5, 'precipitation': 'clear'},
            'game_script_prediction': 'run_heavy'
        }

        signal = engine._game_context_signal(prop_data, context)

        assert signal is not None
        assert signal.probability > 0.5  # Run-heavy helps RB props

    def test_game_context_no_adjustments(self, engine):
        """Test game context signal with no significant adjustments"""
        prop_data = {'prop_type': 'coin_toss'}
        context = {
            'venue_type': 'dome',
            'weather_forecast': {},
            'game_script_prediction': 'balanced'
        }

        signal = engine._game_context_signal(prop_data, context)

        # Should return None for irrelevant prop types or no adjustments
        assert signal is None

    def test_market_movement_signal_up(self, engine):
        """Test market movement signal with upward movement"""
        prop_data = {'prop_type': 'qb_passing_yards'}
        market = {
            'open_price': 50.0,
            'current_price': 55.0
        }

        signal = engine._market_movement_signal(prop_data, market)

        assert signal is not None
        assert signal.source == SignalSource.MARKET_MOVEMENT
        assert signal.probability == 0.55  # 55 cents

    def test_market_movement_signal_no_movement(self, engine):
        """Test market movement signal with no significant movement"""
        prop_data = {'prop_type': 'qb_passing_yards'}
        market = {
            'open_price': 50.0,
            'current_price': 50.5
        }

        signal = engine._market_movement_signal(prop_data, market)

        # Should return None for insignificant movement
        assert signal is None

    def test_injury_adjustment_qb_out(self, engine):
        """Test injury adjustment signal when QB is out"""
        prop_data = {'prop_type': 'qb_passing_yards', 'player_team': 'Chiefs'}
        injuries = {
            'Chiefs': {
                'qb': {'status': 'out'}
            }
        }

        signal = engine._injury_adjustment_signal(prop_data, injuries)

        assert signal is not None
        assert signal.source == SignalSource.INJURY_ADJUSTMENT
        assert signal.probability < 0.5  # Backup QB = less yards
        assert "Starting QB out" in signal.reason

    def test_injury_adjustment_wr1_out(self, engine):
        """Test injury adjustment signal when #1 WR is out"""
        prop_data = {'prop_type': 'wr_receptions', 'player_team': 'Chiefs'}
        injuries = {
            'Chiefs': {
                'wr1': {'status': 'out'}
            }
        }

        signal = engine._injury_adjustment_signal(prop_data, injuries)

        assert signal is not None
        assert signal.probability > 0.5  # More targets for other WRs
        assert "#1 WR out" in signal.reason

    def test_injury_adjustment_no_injuries(self, engine):
        """Test injury adjustment signal with no injuries"""
        prop_data = {'prop_type': 'qb_passing_yards', 'player_team': 'Chiefs'}
        injuries = {
            'Chiefs': {}
        }

        signal = engine._injury_adjustment_signal(prop_data, injuries)

        assert signal is None

    def test_custom_weights(self, engine, sample_prop_data):
        """Test using custom weights for signals"""
        custom_weights = {
            SignalSource.PLAYER_STATS: 0.8,
            SignalSource.GAME_CONTEXT: 0.2,
            SignalSource.HISTORICAL: 0.0,
            SignalSource.MARKET_MOVEMENT: 0.0,
            SignalSource.INJURY_ADJUSTMENT: 0.0,
        }

        estimate = engine.calculate_probability(
            prop_data=sample_prop_data,
            player_stats=sample_player_stats,
            game_context=sample_game_context,
            custom_weights=custom_weights
        )

        # Player stats should have highest contribution
        assert estimate.signal_breakdown.get('player_stats', 0) > estimate.signal_breakdown.get('game_context', 0)

    def test_confidence_calculation(self, engine):
        """Test overall confidence calculation"""
        prop_data = {'prop_type': 'qb_passing_yards', 'line': 275.0}

        # High confidence signals
        stats = {'season_avg': 285.0, 'recent_5_avg': 295.0, 'games_played': 16}

        estimate = engine.calculate_probability(
            prop_data=prop_data,
            player_stats=stats
        )

        # Should have reasonable confidence
        assert estimate.confidence > 0
