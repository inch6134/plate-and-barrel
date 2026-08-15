import polars as pl

from app.data import batting, roster


def test_scopes_to_padres_batters():
    assert batting().height == 3354
    assert batting()["batter_bam_id"].n_unique() == 15


def test_plate_appearances_exclude_baserunning_events():
    assert batting()["terminating"].sum() == 831
    assert batting()["is_pa"].sum() == 830


def test_batted_balls_exclude_tracked_foul_balls():
    batted = batting().filter(pl.col("batted_ball"))
    assert batted.height == 626
    assert batted["in_play"].all()


def test_switch_hitters_resolve_to_a_single_side():
    sides = dict(zip(roster()["batter_bam_id"], roster()["side"]))
    assert sides[595777] == "S"
    assert sides[669369] == "S"
    assert sides[592518] == "R"


def test_base_state_buckets_match_runner_columns():
    counts = dict(batting()["base_state"].value_counts().iter_rows())
    assert counts == {"empty": 1885, "on_base": 705, "scoring": 764}
