# API Contract

All responses are JSON. All rates are fractions in [0, 1], not percentages.
A `null` rate means the denominator was zero or the player fell below a sample floor.

`StatLine` is the one stat shape every endpoint below reuses: player, team, and
per-bucket totals are all the same object. Every rate in it ships alongside its
numerator and denominator, so a caller can show a sample size without a second
request.

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

## GET /api/players/{batter_id}/swing-profile

| Param        | Required | Values                                     |
| ------------ | -------- | ------------------------------------------ |
| `pitch_type` | no       | `4S` `2S` `CT` `SL` `SW` `CB` `CH` `SP`    |

`{ player, team, swings, pitch_types }`. `player` and `team` are `StatLine`s over the
same pitch-type scope, so the view can draw a baseline without a second request.

`swings` is one row per non-bunt swing that has a tracked `bat_speed` (1,603 of the
team's 1,610 non-bunt swings), carrying `bat_speed`, `attack_angle`, `pitch_type`,
`in_zone`, `result` (`in_play` / `foul` / `whiff`), and the batted-ball fields
(`exit_velo`, `launch_angle`, `distance`, `hard_hit`, `barrel`) which are null or
false unless the swing produced a tracked ball in play.

`pitch_types` is the filter menu: every pitch type this batter saw and how many
pitches of it, counted over all pitches rather than the filtered scope, so the
counts hold still as the caller filters.

## GET /api/players/{batter_id}/spray-chart

| Param        | Required | Values                                                        |
| ------------ | -------- | ------------------------------------------------------------- |
| `trajectory` | no       | `ground_ball` `line_drive` `fly_ball` `popup` `bunt_grounder` |
| `outcome`    | no       | `hit` or `out`                                                 |

`{ player, team, batted_balls, trajectories }`, over balls in play with a tracked
exit speed. `player` and `team` are `StatLine`s over the same filtered scope, in
the same shape the swing profile returns, so the view can show pull, center and
oppo rates against the team without a second request.

`bearing` is degrees off dead center, negative to left field and positive to right.
`outcome` splits hit versus out rather than by `event_type`, since 8 of the 13
batted-ball event types occur fewer than 8 times team-wide.

`trajectories` is the filter menu and, like `pitch_types` above, is counted before
filtering.

## GET /api/players/{batter_id}/splits

| Param       | Required | Values                                                       |
| ----------- | -------- | ------------------------------------------------------------ |
| `dimension` | no       | `count` (default) `outs` `bases` `inning` `hand` `role`      |

`{ dimension, splits }`, one entry per bucket in a fixed order:

| Dimension | Buckets                                   |
| --------- | ----------------------------------------- |
| `count`   | ahead / even / behind                     |
| `outs`    | `0` / `1` / `2`, from `pre_outs`          |
| `bases`   | empty / on base / scoring position        |
| `inning`  | 1-3 / 4-6 / 7+                            |
| `hand`    | L / R, the pitcher's throwing side        |
| `role`    | starter / reliever, from `pitcher_type`   |

Each entry carries a full `StatLine` for both the player and the team in that
bucket, so switching metrics is client-side and needs no request. Sample floors
apply per bucket, so a rate is null where that bucket is thin.

## GET /api/insights

| Param       | Required | Values                          |
| ----------- | -------- | ------------------------------- |
| `batter_id` | yes      | one of the 15 Padres batters    |
| `view`      | no       | `swing` (default) `spray` `splits` |

Up to three structured facts, strongest first, at most one per metric. Strength is
the player-baseline gap divided by the cross-player standard deviation for that
metric, so a gap counts as notable relative to how much the metric varies across
the team. That score is internal to the ranking and is not part of the response.

Each fact carries `metric`, `value`, `baseline`, `sample` and `sample_column`, plus
`dimension` and `scope`. For `swing` and `spray` the comparison is overall, so
`dimension` is null and `scope` is `"overall"`. For `splits` it is per bucket, so
`dimension` names the split and `scope` names the bucket.

Callers render the sentence. The response is facts, not prose. Metrics below their
sample floor are dropped, so a thin batter returns `[]`.
