"""
Super Bowl LX Configuration - Matchup Research Integration
Based on Atlas's research from shared/documents/super-bowl-matchup-research.md
Date: February 7, 2026
"""

from dataclasses import dataclass, asdict
from typing import Dict, List
import json


@dataclass
class SuperBowlPlayerStats:
    """Player statistics from Atlas's matchup research"""
    player_name: str
    team: str
    position: str
    season_avg: float
    recent_5_avg: float
    recent_3_avg: float
    key_metric: str  # e.g., "passing_yards", "receiving_yards"
    vs_opponent_avg: float = 0.0
    home_away_avg: float = 0.0
    std_dev: float = 0.0
    games_played: int = 16


@dataclass
class SuperBowlPropEdge:
    """Top betting edges identified by Atlas"""
    rank: int
    bet_type: str
    line: float
    our_estimate: float
    market_implied: float
    edge_percent: float
    confidence: str
    reasoning: str


@dataclass
class SuperBowlGameContext:
    """Game context for Super Bowl LX"""
    venue: str  # "Levi's Stadium"
    location: str  # "Santa Clara, California"
    surface: str  # "grass"
    venue_type: str  # "outdoor"
    weather_forecast: Dict
    spread: float  # Seahawks -4.5
    over_under: float  # 48.5-50.5
    game_script_prediction: str  # "balanced"
    key_injuries: Dict


# Player statistics from Atlas's research
SUPER_BOWL_PLAYER_STATS = {
    "Drake Maye": SuperBowlPlayerStats(
        player_name="Drake Maye",
        team="Patriots",
        position="QB",
        season_avg=274.6,  # 4,394 yards / 16 games
        recent_5_avg=274.6,
        recent_3_avg=274.6,
        key_metric="passing_yards",
        games_played=16
    ),
    "Sam Darnold": SuperBowlPlayerStats(
        player_name="Sam Darnold",
        team="Seahawks",
        position="QB",
        season_avg=253.0,  # 4,048 yards / 16 games
        recent_5_avg=253.0,
        recent_3_avg=253.0,
        key_metric="passing_yards",
        games_played=16
    ),
    "Jaxon Smith-Njigba": SuperBowlPlayerStats(
        player_name="Jaxon Smith-Njigba",
        team="Seahawks",
        position="WR",
        season_avg=112.1,  # 1,793 yards / 16 games
        recent_5_avg=112.1,
        recent_3_avg=112.1,
        key_metric="receiving_yards",
        games_played=16
    ),
    "Cooper Kupp": SuperBowlPlayerStats(
        player_name="Cooper Kupp",
        team="Seahawks",
        position="WR",
        season_avg=63.3,  # 1,013 yards / 16 games
        recent_5_avg=63.3,
        recent_3_avg=63.3,
        key_metric="receiving_yards",
        games_played=16
    ),
    "Stefon Diggs": SuperBowlPlayerStats(
        player_name="Stefon Diggs",
        team="Patriots",
        position="WR",
        season_avg=63.3,  # 1,013 yards / 16 games
        recent_5_avg=63.3,
        recent_3_avg=63.3,
        key_metric="receiving_yards",
        games_played=16
    ),
    "Kenneth Walker III": SuperBowlPlayerStats(
        player_name="Kenneth Walker III",
        team="Seahawks",
        position="RB",
        season_avg=64.2,  # 1,027 yards / 16 games
        recent_5_avg=64.2,
        recent_3_avg=64.2,
        key_metric="rushing_yards",
        games_played=16
    ),
    "TreVeyon Henderson": SuperBowlPlayerStats(
        player_name="TreVeyon Henderson",
        team="Patriots",
        position="RB",
        season_avg=56.9,  # 911 yards / 16 games
        recent_5_avg=56.9,
        recent_3_avg=56.9,
        key_metric="rushing_yards",
        games_played=16
    ),
    "Hunter Henry": SuperBowlPlayerStats(
        player_name="Hunter Henry",
        team="Patriots",
        position="TE",
        season_avg=48.0,  # 768 yards / 16 games
        recent_5_avg=48.0,
        recent_3_avg=48.0,
        key_metric="receiving_yards",
        games_played=16
    ),
}


# Top 5 edges from Atlas's research
SUPER_BOWL_TOP_EDGES = [
    SuperBowlPropEdge(
        rank=1,
        bet_type="OVER Total Points",
        line=49.5,
        our_estimate=0.62,
        market_implied=0.50,
        edge_percent=14.0,
        confidence="High",
        reasoning="Both teams top-3 in scoring, ideal weather conditions"
    ),
    SuperBowlPropEdge(
        rank=2,
        bet_type="Drake Maye OVER Passing Yards",
        line=245.5,
        our_estimate=0.64,
        market_implied=0.50,
        edge_percent=16.0,
        confidence="High",
        reasoning="Maye led AFC with 4,394 yards, 72% completion rate led NFL"
    ),
    SuperBowlPropEdge(
        rank=3,
        bet_type="Jaxon Smith-Njigba OVER Receiving Yards",
        line=95.5,
        our_estimate=0.62,
        market_implied=0.50,
        edge_percent=14.0,
        confidence="High",
        reasoning="JSN led NFL with 1,793 receiving yards, favorable matchup"
    ),
    SuperBowlPropEdge(
        rank=4,
        bet_type="Sam Darnold OVER Completions",
        line=25.5,
        our_estimate=0.60,
        market_implied=0.50,
        edge_percent=12.0,
        confidence="High",
        reasoning="Darnold 67.7% completion rate, 25 completions avg per game"
    ),
    SuperBowlPropEdge(
        rank=5,
        bet_type="First Score = Touchdown",
        line=0.0,
        our_estimate=0.60,
        market_implied=0.50,
        edge_percent=12.0,
        confidence="Medium-High",
        reasoning="Historical pattern: 60% of recent SBs had TD first"
    ),
]


# Game context for Super Bowl LX
SUPER_BOWL_GAME_CONTEXT = SuperBowlGameContext(
    venue="Levi's Stadium",
    location="Santa Clara, California",
    surface="grass",
    venue_type="outdoor",
    weather_forecast={
        "temperature": "60°F",
        "condition": "sunny/partly cloudy",
        "wind_speed": 8,  # mph
        "precipitation": "none"
    },
    spread=-4.5,  # Seahawks favored by 4.5
    over_under=49.5,  # Midpoint of 48.5-50.5
    game_script_prediction="balanced",  # Both offenses strong
    key_injuries={
        "Seahawks": {
            "Zach Charbonnet": {"position": "RB", "status": "OUT", "reason": "ACL (playoffs)"},
            "Sam Darnold": {"position": "QB", "status": "QUESTIONABLE", "reason": "Oblique"}
        },
        "Patriots": {
            # No major injuries reported
        }
    }
)


# Historical Super Bowl patterns (from Atlas's research)
SUPER_BOWL_HISTORICAL_PATTERNS = {
    "first_score_td_rate": 0.60,  # 60% of recent SBs had TD first
    "total_over_rate": 0.55,  # Over tends to hit 55% of time
    "player_props_over_rate": 0.56,  # Player props tend to hit overs
    "first_half_inefficiency_edge": 0.02,  # Small edge on first half totals
}


def get_player_stats(player_name: str) -> SuperBowlPlayerStats:
    """Get player stats by name"""
    return SUPER_BOWL_PLAYER_STATS.get(player_name)


def get_player_stats_by_team(team: str) -> List[SuperBowlPlayerStats]:
    """Get all player stats for a team"""
    return [
        stats for stats in SUPER_BOWL_PLAYER_STATS.values()
        if stats.team == team
    ]


def get_game_context() -> SuperBowlGameContext:
    """Get game context"""
    return SUPER_BOWL_GAME_CONTEXT


def get_top_edges() -> List[SuperBowlPropEdge]:
    """Get top betting edges"""
    return SUPER_BOWL_TOP_EDGES


def get_historical_patterns() -> Dict:
    """Get historical Super Bowl patterns"""
    return SUPER_BOWL_HISTORICAL_PATTERNS


def export_to_json(filepath: str = "/tmp/super_bowl_config.json"):
    """Export configuration to JSON for API access"""
    config = {
        "players": {
            name: asdict(stats)
            for name, stats in SUPER_BOWL_PLAYER_STATS.items()
        },
        "top_edges": [asdict(edge) for edge in SUPER_BOWL_TOP_EDGES],
        "game_context": asdict(SUPER_BOWL_GAME_CONTEXT),
        "historical_patterns": SUPER_BOWL_HISTORICAL_PATTERNS
    }

    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)

    return filepath


if __name__ == "__main__":
    # Test the configuration
    print("Super Bowl LX Configuration")
    print("=" * 50)

    print("\nTop 5 Edges:")
    for edge in get_top_edges():
        print(f"{edge.rank}. {edge.bet_type}")
        print(f"   Line: {edge.line}, Edge: {edge.edge_percent}%, Confidence: {edge.confidence}")
        print(f"   Reasoning: {edge.reasoning}")

    print("\nGame Context:")
    ctx = get_game_context()
    print(f"Venue: {ctx.venue}")
    print(f"Spread: Seahawks {ctx.spread}")
    print(f"Over/Under: {ctx.over_under}")
    print(f"Weather: {ctx.weather_forecast}")

    print("\nExporting to JSON...")
    export_to_json()
    print("Done!")
