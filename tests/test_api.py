from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_players_returns_full_roster():
    players = client.get("/api/players").json()
    assert len(players) == 15
    assert {p["side"] for p in players} == {"L", "R", "S"}


def test_player_detail_reports_ungated_numbers_for_thin_samples():
    rosario = client.get("/api/players/666703").json()
    assert rosario["stats"]["pa"] == 1
    assert rosario["stats"]["batted_balls"] == 1


def test_unknown_batter_is_not_found():
    assert client.get("/api/players/1").status_code == 404


def test_team_baseline_matches_player_stat_shape():
    team = client.get("/api/team").json()
    player = client.get("/api/players/592518").json()["stats"]
    assert team.keys() == player.keys()
    assert round(team["ops"], 3) == 0.736


def test_rate_leaderboard_excludes_below_floor_players():
    entries = client.get("/api/leaderboard", params={"metric": "ops"}).json()
    assert len(entries) == 12
    assert entries[0]["name_last"] == "Bogaerts"
    assert all(e["sample"] >= 20 for e in entries)


def test_count_leaderboard_includes_everyone():
    entries = client.get("/api/leaderboard", params={"metric": "home_runs"}).json()
    assert len(entries) == 15
    assert entries[0]["value"] == 7


def test_ascending_order_ranks_lowest_first():
    entries = client.get(
        "/api/leaderboard", params={"metric": "chase_rate", "order": "asc"}
    ).json()
    assert entries[0]["name_last"] == "Bogaerts"
    assert entries[0]["value"] < entries[-1]["value"]


def test_unknown_metric_is_rejected():
    assert client.get("/api/leaderboard", params={"metric": "nope"}).status_code == 422


def test_splits_return_buckets_in_domain_order():
    splits = client.get(
        "/api/players/592518/splits", params={"dimension": "count"}
    ).json()
    assert [s["bucket"] for s in splits["splits"]] == ["ahead", "even", "behind"]


def test_splits_carry_a_matching_team_baseline():
    splits = client.get(
        "/api/players/592518/splits", params={"dimension": "bases"}
    ).json()
    scoring = next(s for s in splits["splits"] if s["bucket"] == "scoring")
    assert round(scoring["player"]["chase_rate"], 3) == 0.447
    assert round(scoring["team"]["chase_rate"], 3) == 0.356


def test_thin_samples_are_gated_within_each_bucket():
    splits = client.get(
        "/api/players/666703/splits", params={"dimension": "count"}
    ).json()
    assert all(s["player"]["chase_rate"] is None for s in splits["splits"])


def test_outs_split_buckets_by_the_pre_pitch_out_count():
    splits = client.get(
        "/api/players/592518/splits", params={"dimension": "outs"}
    ).json()
    assert [s["bucket"] for s in splits["splits"]] == ["0", "1", "2"]
    assert sum(s["player"]["pitches"] for s in splits["splits"]) == 360


def test_role_split_separates_starters_from_relievers():
    splits = client.get(
        "/api/players/592518/splits", params={"dimension": "role"}
    ).json()
    assert [s["bucket"] for s in splits["splits"]] == ["starter", "reliever"]
    assert [s["player"]["swings"] for s in splits["splits"]] == [121, 75]


def test_spray_chart_returns_every_batted_ball_with_its_trajectory_options():
    spray = client.get("/api/players/592518/spray-chart").json()
    assert len(spray["batted_balls"]) == 69
    assert sum(option["count"] for option in spray["trajectories"]) == 69


def test_spray_chart_carries_a_team_baseline_over_the_same_filter():
    spray = client.get(
        "/api/players/592518/spray-chart", params={"trajectory": "fly_ball"}
    ).json()
    assert spray["player"]["batted_balls"] == len(spray["batted_balls"])
    assert spray["team"]["batted_balls"] == 154


def test_spray_outcome_filter_keeps_only_hits():
    spray = client.get(
        "/api/players/592518/spray-chart", params={"outcome": "hit"}
    ).json()
    assert len(spray["batted_balls"]) == 23
    assert all(ball["is_hit"] for ball in spray["batted_balls"])


def test_spray_trajectory_options_stay_unfiltered_so_pill_counts_hold_still():
    spray = client.get(
        "/api/players/592518/spray-chart", params={"trajectory": "line_drive"}
    ).json()
    assert len(spray["batted_balls"]) == 22
    assert sum(option["count"] for option in spray["trajectories"]) == 69


def test_spray_chart_rejects_an_unknown_trajectory():
    response = client.get(
        "/api/players/592518/spray-chart", params={"trajectory": "nope"}
    )
    assert response.status_code == 422


def test_insights_rank_one_callout_per_metric():
    insights = client.get(
        "/api/insights", params={"batter_id": 592518, "view": "swing"}
    ).json()
    assert len(insights) == 3
    assert len({i["metric"] for i in insights}) == 3
    assert all(i["dimension"] is None and i["scope"] == "overall" for i in insights)


def test_insight_values_match_the_players_own_stat_line():
    insights = client.get(
        "/api/insights", params={"batter_id": 592518, "view": "spray"}
    ).json()
    stats = client.get("/api/players/592518").json()["stats"]
    assert all(i["value"] == stats[i["metric"]] for i in insights)


def test_split_insights_name_the_bucket_they_came_from():
    insights = client.get(
        "/api/insights", params={"batter_id": 592518, "view": "splits"}
    ).json()
    assert all(i["dimension"] is not None for i in insights)
    assert all(i["scope"] != "overall" for i in insights)


def test_gated_player_produces_no_insights():
    insights = client.get(
        "/api/insights", params={"batter_id": 666703, "view": "swing"}
    ).json()
    assert insights == []
