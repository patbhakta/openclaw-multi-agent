"""
Unit tests for Prop Analysis Engine
"""

import pytest
from src.prop_analysis import (
    PropAnalyzer, PropType, PropValueLevel, PropData,
    PlayerStats, GameContext, PropAnalysisResult
)


@pytest.fixture
def analyzer():
    """Create a PropAnalyzer instance"""
    return PropAnalyzer()


@pytest.fixture
def sample_qb_prop():
    """Create a sample QB passing yards prop"""
    return PropData(
        prop_id="test_qb_passing_yards",
        prop_type=PropType.QB_PASSING_YARDS,
        title="Patrick Mahomes Passing Yards",
        player_team="Chiefs",
        metric="passing_yards",
        line=275.0,
        market_price=52.0,  # 52 cents = 52% probability
        market_probability=0.52,
        open_price=50.0,
        volume=5000
    )


@pytest.fixture
def sample_player_stats():
    """Create sample player stats"""
    return PlayerStats(
        player_name="Patrick Mahomes",
        team="Chiefs",
        season_avg=285.0,
        recent_5_avg=295.0,
        recent_3_avg=290.0,
        vs_opponent_avg=280.0,
        home_away_avg=282.0,
        std_dev=25.0,
        games_played=16
    )


@pytest.fixture
def sample_game_context():
    """Create sample game context"""
    return GameContext(
        venue_type="outdoor",
        weather_forecast={
            'wind_speed': 10,
            'precipitation': 'clear',
            'temperature': 65
        },
        injury_impact={},
        game_script_prediction="balanced",
        spread=3.0,
        over_under=48.5
    )


class TestPropValueLevel:
    """Test value level mapping"""

    def test_qb_passing_yards_high_value(self, analyzer):
        """QB passing yards should be HIGH value"""
        level = analyzer.VALUE_LEVELS[PropType.QB_PASSING_YARDS]
        assert level == PropValueLevel.HIGH

    def test_wr_receptions_high_value(self, analyzer):
        """WR receptions should be HIGH value"""
        level = analyzer.VALUE_LEVELS[PropType.WR_RECEPTIONS]
        assert level == PropValueLevel.HIGH

    def test_coin_toss_avoid(self, analyzer):
        """Coin toss should be AVOID"""
        level = analyzer.VALUE_LEVELS[PropType.COIN_TOSS]
        assert level == PropValueLevel.AVOID

    def test_gatorade_color_avoid(self, analyzer):
        """Gatorade color should be AVOID"""
        level = analyzer.VALUE_LEVELS[PropType.GATORADE_COLOR]
        assert level == PropValueLevel.AVOID


class TestPropAnalyzer:
    """Test PropAnalyzer functionality"""

    def test_analyze_prop_with_stats(
        self,
        analyzer,
        sample_qb_prop,
        sample_player_stats,
        sample_game_context
    ):
        """Test analyzing a prop with player stats"""
        result = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=sample_player_stats,
            game_context=sample_game_context
        )

        assert isinstance(result, PropAnalysisResult)
        assert result.prop.prop_id == sample_qb_prop.prop_id
        assert 0 <= result.ai_probability <= 1
        assert isinstance(result.edge, float)
        assert result.recommendation in ["OVER", "UNDER", "NO_BET"]
        assert result.confidence in ["HIGH", "MEDIUM", "LOW"]

    def test_analyze_prop_without_stats(self, analyzer, sample_qb_prop):
        """Test analyzing a prop without player stats"""
        result = analyzer.analyze_prop(prop=sample_qb_prop)

        assert isinstance(result, PropAnalysisResult)
        assert result.ai_probability == sample_qb_prop.market_probability
        assert result.edge == 0

    def test_analyze_prop_coin_toss(self, analyzer):
        """Test analyzing coin toss (should recommend NO_BET)"""
        prop = PropData(
            prop_id="test_coin_toss",
            prop_type=PropType.COIN_TOSS,
            title="Coin Toss",
            player_team="GAME",
            metric="coin_toss",
            line=None,
            market_price=50.0,
            market_probability=0.5
        )

        result = analyzer.analyze_prop(prop=prop)

        assert result.recommendation == "NO_BET"
        assert result.value_level == PropValueLevel.AVOID

    def test_edge_calculation_with_over(self, sample_qb_prop):
        """Test edge calculation when AI prob > market prob"""
        analyzer = PropAnalyzer()

        # Create scenario where season avg > line
        stats = PlayerStats(
            player_name="Test QB",
            team="Test Team",
            season_avg=290.0,  # Above line
            recent_5_avg=295.0,
            recent_3_avg=290.0,
            vs_opponent_avg=280.0,
            home_away_avg=282.0,
            std_dev=20.0,
            games_played=16
        )

        result = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=stats
        )

        # Should have positive edge (OVER)
        assert result.edge > 0

    def test_edge_calculation_with_under(self, sample_qb_prop):
        """Test edge calculation when AI prob < market prob"""
        analyzer = PropAnalyzer()

        # Create scenario where season avg < line
        stats = PlayerStats(
            player_name="Test QB",
            team="Test Team",
            season_avg=260.0,  # Below line
            recent_5_avg=255.0,
            recent_3_avg=258.0,
            vs_opponent_avg=265.0,
            home_away_avg=262.0,
            std_dev=20.0,
            games_played=16
        )

        result = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=stats
        )

        # Should have negative edge (UNDER)
        assert result.edge < 0

    def test_weather_adjustment(self, analyzer, sample_qb_prop):
        """Test weather adjustment for outdoor games"""
        stats = PlayerStats(
            player_name="Test QB",
            team="Test Team",
            season_avg=280.0,
            recent_5_avg=280.0,
            recent_3_avg=280.0,
            vs_opponent_avg=280.0,
            home_away_avg=280.0,
            std_dev=20.0,
            games_played=16
        )

        # High wind should reduce passing probability
        windy_context = GameContext(
            venue_type="outdoor",
            weather_forecast={'wind_speed': 20, 'precipitation': 'clear', 'temperature': 65},
            injury_impact={},
            game_script_prediction="balanced",
            spread=3.0,
            over_under=48.5
        )

        result_windy = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=stats,
            game_context=windy_context
        )

        # Calm context for comparison
        calm_context = GameContext(
            venue_type="outdoor",
            weather_forecast={'wind_speed': 5, 'precipitation': 'clear', 'temperature': 65},
            injury_impact={},
            game_script_prediction="balanced",
            spread=3.0,
            over_under=48.5
        )

        result_calm = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=stats,
            game_context=calm_context
        )

        # Windy should have lower probability
        assert result_windy.ai_probability < result_calm.ai_probability

    def test_game_script_adjustment(self, analyzer, sample_qb_prop):
        """Test game script adjustment"""
        stats = PlayerStats(
            player_name="Test QB",
            team="Test Team",
            season_avg=280.0,
            recent_5_avg=280.0,
            recent_3_avg=280.0,
            vs_opponent_avg=280.0,
            home_away_avg=280.0,
            std_dev=20.0,
            games_played=16
        )

        # Pass-heavy script
        pass_heavy_context = GameContext(
            venue_type="outdoor",
            weather_forecast={'wind_speed': 5, 'precipitation': 'clear', 'temperature': 65},
            injury_impact={},
            game_script_prediction="pass_heavy",
            spread=3.0,
            over_under=48.5
        )

        result_pass_heavy = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=stats,
            game_context=pass_heavy_context
        )

        # Run-heavy script
        run_heavy_context = GameContext(
            venue_type="outdoor",
            weather_forecast={'wind_speed': 5, 'precipitation': 'clear', 'temperature': 65},
            injury_impact={},
            game_script_prediction="run_heavy",
            spread=3.0,
            over_under=48.5
        )

        result_run_heavy = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=stats,
            game_context=run_heavy_context
        )

        # Pass-heavy should have higher probability for passing props
        assert result_pass_heavy.ai_probability > result_run_heavy.ai_probability

    def test_batch_analyze(self, analyzer):
        """Test batch analysis of multiple props"""
        props = [
            PropData(
                prop_id=f"prop_{i}",
                prop_type=PropType.QB_PASSING_YARDS if i % 2 == 0 else PropType.WR_RECEPTIONS,
                title=f"Prop {i}",
                player_team="Test Team",
                metric="test_metric",
                line=100.0 + i * 10,
                market_price=50.0,
                market_probability=0.5
            )
            for i in range(5)
        ]

        results = analyzer.batch_analyze(props)

        assert len(results) == 5
        assert all(isinstance(r, PropAnalysisResult) for r in results)

    def test_reasoning_generation(self, analyzer, sample_qb_prop):
        """Test reasoning generation"""
        stats = PlayerStats(
            player_name="Test QB",
            team="Test Team",
            season_avg=290.0,
            recent_5_avg=295.0,
            recent_3_avg=290.0,
            vs_opponent_avg=280.0,
            home_away_avg=282.0,
            std_dev=20.0,
            games_played=16
        )

        result = analyzer.analyze_prop(
            prop=sample_qb_prop,
            player_stats=stats
        )

        assert len(result.reasoning) > 0
        assert any("HIGH value" in r for r in result.reasoning)

    def test_risk_identification(self, analyzer, sample_qb_prop):
        """Test risk factor identification"""
        # Add injury impact
        context = GameContext(
            venue_type="outdoor",
            weather_forecast={'wind_speed': 25, 'precipitation': 'rain', 'temperature': 40},
            injury_impact={'Chiefs': ['WR1 out']},
            game_script_prediction="balanced",
            spread=3.0,
            over_under=48.5
        )

        result = analyzer.analyze_prop(
            prop=sample_qb_prop,
            game_context=context
        )

        # Should identify weather and injury risks
        assert len(result.risk_factors) > 0
