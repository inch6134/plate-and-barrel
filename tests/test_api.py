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
