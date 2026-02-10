"""
Super Bowl LX Integration Script
Integrates Atlas's matchup research into the Phase 2 betting system
Usage: python -m src.super_bowl_integration
"""

import sys
import json
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from super_bowl_config import (
    get_player_stats,
    get_top_edges,
    get_game_context,
    get_historical_patterns,
    SUPER_BOWL_PLAYER_STATS,
    SUPER_BOWL_TOP_EDGES,
    SUPER_BOWL_GAME_CONTEXT,
    SUPER_BOWL_HISTORICAL_PATTERNS
)

from prop_analysis import (
    PropData,
    PropType,
    PlayerStats,
    GameContext,
    PropAnalyzer,
    PropValueLevel
)

from probability_engine import (
    ProbabilityEngine
)


def convert_player_stats(super_bowl_stats) -> PlayerStats:
    """Convert SuperBowlPlayerStats to PlayerStats"""
    return PlayerStats(
        player_name=super_bowl_stats.player_name,
        team=super_bowl_stats.team,
        season_avg=super_bowl_stats.season_avg,
        recent_5_avg=super_bowl_stats.recent_5_avg,
        recent_3_avg=super_bowl_stats.recent_3_avg,
        vs_opponent_avg=super_bowl_stats.vs_opponent_avg,
        home_away_avg=super_bowl_stats.home_away_avg,
        std_dev=super_bowl_stats.std_dev,
        games_played=super_bowl_stats.games_played
    )


def convert_game_context(super_bowl_context) -> GameContext:
    """Convert SuperBowlGameContext to GameContext"""
    return GameContext(
        venue_type=super_bowl_context.venue_type,
        weather_forecast=super_bowl_context.weather_forecast,
        injury_impact=super_bowl_context.key_injuries,
        game_script_prediction=super_bowl_context.game_script_prediction,
        spread=super_bowl_context.spread,
        over_under=super_bowl_context.over_under
    )


def create_props_from_edges(edges: List) -> List[PropData]:
    """Create PropData objects from top edges"""
    props = []

    for edge in edges:
        bet_type = edge.bet_type

        if "Total Points" in bet_type:
            prop = PropData(
                prop_id=f"super_bowl_total_{edge.rank}",
                prop_type=PropType.FIRST_HALF_TOTALS,  # Use game totals
                title=f"Super Bowl LX - Total Points",
                player_team="GAME",
                metric="total_points",
                line=edge.line,
                market_price=50.0,  # Even money implied
                market_probability=0.50,
                volume=10000
            )

        elif "Drake Maye" in bet_type:
            prop = PropData(
                prop_id=f"super_bowl_mayne_pass_{edge.rank}",
                prop_type=PropType.QB_PASSING_YARDS,
                title=f"Super Bowl LX - Drake Maye Passing Yards",
                player_team="Patriots",
                metric="passing_yards",
                line=edge.line,
                market_price=50.0,
                market_probability=0.50,
                volume=5000
            )

        elif "Jaxon Smith-Njigba" in bet_type:
            prop = PropData(
                prop_id=f"super_bowl_jsn_rec_{edge.rank}",
                prop_type=PropType.WR_YARDS,
                title=f"Super Bowl LX - Jaxon Smith-Njigba Receiving Yards",
                player_team="Seahawks",
                metric="receiving_yards",
                line=edge.line,
                market_price=50.0,
                market_probability=0.50,
                volume=5000
            )

        elif "Sam Darnold" in bet_type and "Completions" in bet_type:
            prop = PropData(
                prop_id=f"super_bowl_darnold_comp_{edge.rank}",
                prop_type=PropType.WR_RECEPTIONS,  # Use receptions for completions
                title=f"Super Bowl LX - Sam Darnold Completions",
                player_team="Seahawks",
                metric="completions",
                line=edge.line,
                market_price=50.0,
                market_probability=0.50,
                volume=5000
            )

        elif "First Score" in bet_type:
            prop = PropData(
                prop_id=f"super_bowl_first_score_{edge.rank}",
                prop_type=PropType.FIRST_SCORE,
                title=f"Super Bowl LX - First Score Method",
                player_team="GAME",
                metric="first_score",
                line=0.0,
                market_price=50.0,
                market_probability=0.50,
                volume=8000
            )
        else:
            continue  # Skip unsupported prop types

        props.append(prop)

    return props


def run_integration():
    """Run Super Bowl integration"""
    print("=" * 70)
    print("SUPER BOWL LX - MATCHUP RESEARCH INTEGRATION")
    print("=" * 70)
    print(f"Date: February 7, 2026")
    print(f"Matchup: Seattle Seahawks (14-3) vs New England Patriots (14-3)")
    print(f"Location: Levi's Stadium, Santa Clara, CA")
    print("=" * 70)
    print()

    # Get configuration
    game_context_sb = get_game_context()
    historical_patterns = get_historical_patterns()
    top_edges = get_top_edges()

    print("Game Context:")
    print(f"  Venue: {game_context_sb.venue}")
    print(f"  Spread: Seahawks {game_context_sb.spread}")
    print(f"  Total: {game_context_sb.over_under}")
    print(f"  Weather: {game_context_sb.weather_forecast}")
    print(f"  Injuries: {game_context_sb.key_injuries}")
    print()

    # Create prop analyzer
    analyzer = PropAnalyzer()

    # Create probability engine
    prob_engine = ProbabilityEngine()

    # Create props from top edges
    props = create_props_from_edges(top_edges)

    # Convert game context
    game_context = convert_game_context(game_context_sb)

    # Analyze props
    print(f"Analyzing {len(props)} top betting edges...")
    print()

    results = []
    for prop in props:
        # Get player stats if needed
        player_stats_obj = None
        if prop.player_team != "GAME":
            player_name = None

            if "Drake Maye" in prop.title:
                player_name = "Drake Maye"
            elif "Jaxon Smith-Njigba" in prop.title:
                player_name = "Jaxon Smith-Njigba"
            elif "Sam Darnold" in prop.title:
                player_name = "Sam Darnold"

            if player_name:
                sb_stats = get_player_stats(player_name)
                if sb_stats:
                    player_stats_obj = convert_player_stats(sb_stats)

        # Analyze prop
        result = analyzer.analyze_prop(
            prop=prop,
            player_stats=player_stats_obj,
            game_context=game_context,
            historical_performance=historical_patterns
        )

        results.append(result)

    # Print results
    print("=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    print()

    # Sort by edge (descending)
    results_sorted = sorted(results, key=lambda r: r.edge, reverse=True)

    for i, result in enumerate(results_sorted, 1):
        print(f"{i}. {result.prop.title}")
        print(f"   Type: {result.prop.prop_type.value}")
        print(f"   Line: {result.prop.line}")
        print(f"   Market Prob: {result.market_probability:.2%}")
        print(f"   AI Probability: {result.ai_probability:.2%}")
        print(f"   Edge: {result.edge*100:+.1f}%")
        print(f"   Recommendation: {result.recommendation}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Value Level: {result.value_level.value}")
        print(f"   Reasoning:")
        for reason in result.reasoning:
            print(f"     - {reason}")
        if result.risk_factors:
            print(f"   Risk Factors:")
            for risk in result.risk_factors:
                print(f"     - {risk}")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    recommended = [r for r in results_sorted if r.recommendation != "NO_BET"]
    no_bet = [r for r in results_sorted if r.recommendation == "NO_BET"]

    print(f"Total props analyzed: {len(results_sorted)}")
    print(f"Recommended bets: {len(recommended)}")
    print(f"No bet: {len(no_bet)}")
    print()

    if recommended:
        print("Recommended Bets:")
        for r in recommended:
            print(f"  - {r.prop.title}: {r.recommendation} (Edge: {r.edge*100:+.1f}%)")
        print()

    # Export to JSON
    export_data = {
        "matchup": {
            "teams": ["Seattle Seahawks", "New England Patriots"],
            "venue": game_context_sb.venue,
            "spread": game_context_sb.spread,
            "over_under": game_context_sb.over_under
        },
        "analysis_date": "2026-02-07T15:20:00Z",
        "props_analyzed": len(results_sorted),
        "recommended_bets": [
            {
                "title": r.prop.title,
                "recommendation": r.recommendation,
                "edge": r.edge,
                "ai_probability": r.ai_probability,
                "market_probability": r.market_probability,
                "confidence": r.confidence,
                "line": r.prop.line
            }
            for r in recommended
        ],
        "no_bets": [
            {
                "title": r.prop.title,
                "reasoning": r.reasoning[0] if r.reasoning else "No edge"
            }
            for r in no_bet
        ]
    }

    export_path = Path("/root/.openclaw/workspace/shared/documents/super-bowl-analysis-results.json")
    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"Analysis results exported to: {export_path}")
    print()
    print("Integration complete!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(run_integration())
