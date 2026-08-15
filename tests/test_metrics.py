import polars as pl

from app.data import batting
from app.metrics import apply_floors, is_barrel, summarize


def team() -> dict:
    return summarize(batting(), []).row(0, named=True)


def test_team_batting_line_balances():
    line = team()
    assert (line["pa"], line["ab"], line["hits"], line["total_bases"]) == (
        830,
        770,
        208,
        324,
    )
    assert round(line["avg"], 3) == 0.270
    assert round(line["obp"], 3) == 0.315
    assert round(line["slg"], 3) == 0.421
    assert round(line["ops"], 3) == 0.736


def test_at_bats_exclude_non_at_bat_outcomes():
    line = team()
    assert line["ab"] == line["pa"] - (
        line["total_walks"]
        + line["hit_by_pitches"]
        + line["sac_flies"]
        + line["sac_bunts"]
    )


def test_swing_denominators_ignore_non_pitch_rows():
    line = team()
    assert line["pitches"] == 3278
    assert line["zone_pitches"] + line["out_of_zone_pitches"] == line["pitches"]


def test_contact_metrics_use_balls_in_play_only():
    line = team()
    assert line["batted_balls"] == 626
    assert round(line["avg_exit_velo"], 1) == 88.0


def test_barrel_window_matches_published_anchors():
    cases = pl.DataFrame(
        {
            "hit_exit_speed": [97.9, 98.0, 98.0, 98.0, 99.0, 99.0, 116.0, 120.0, 120.0],
            "hit_vertical_angle": [28.0, 25.9, 26.0, 30.0, 25.0, 31.0, 8.0, 8.0, 50.1],
        }
    )
    assert cases.select(is_barrel)["hit_exit_speed"].to_list() == [
        False,
        False,
        True,
        True,
        True,
        True,
        True,
        True,
        False,
    ]


def test_undefined_rates_are_null_not_nan():
    players = summarize(batting(), ["batter_bam_id"])
    rosario = players.filter(pl.col("batter_bam_id") == 666703).row(0, named=True)
    assert rosario["out_of_zone_pitches"] == 0
    assert rosario["chase_rate"] is None


def test_floors_gate_only_thin_samples():
    players = apply_floors(summarize(batting(), ["batter_bam_id"]))
    gated = players.filter(pl.col("chase_rate").is_null())["batter_bam_id"].to_list()
    assert sorted(gated) == sorted([642180, 664954, 666703])
    assert (
        players.filter(pl.col("batter_bam_id") == 642180).row(0, named=True)["swings"]
        == 19
    )
