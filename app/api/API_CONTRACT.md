# API Contract

All responses are JSON. All rates are fractions in [0, 1], not percentages.
A `null` rate means the denominator was zero or the player fell below a sample floor.

## GET /api/players

Full roster, sorted by last name. Batting side is derived from the data:
`S` when a batter appears from both sides in the month.

## GET /api/players/{batter_id}

`{ player, stats }`. Sample floors are NOT applied; a thin sample reports its
real numbers. 404 if the id is not one of the 15 Padres batters.

## GET /api/team

Team totals in the same `stats` shape as a player, for baseline comparison.

## GET /api/leaderboard

| Param    | Required | Values                    |
| -------- | -------- | ------------------------- |
| `metric` | yes      | any rate or count metric  |
| `order`  | no       | `asc` or `desc` (default) |

Ranked best-first by the caller's chosen order, rank implied by array position.
Each entry carries `sample`, the observation count backing the value: swings for
swing-decision metrics, batted balls for contact-quality, PA otherwise.

Rate metrics apply sample floors (20 swings / 10 batted balls / 20 PA) and
below-floor players are omitted, so rate leaderboards return 12 of 15 players.
Count metrics are ungated and return all 15.
