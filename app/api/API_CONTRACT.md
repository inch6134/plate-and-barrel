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

`{ player, team, spread, zone, pitches, contexts, pitch_types }`.

`player` and `team` are `StatLine`s over the same pitch-type scope. `spread` is
the cross-player standard deviation of each rate, the same figure the insight
ranking divides by, so a view can show how much a metric varies across the roster
rather than only the team average.

`pitches` is one row per pitch, takes included, carrying `plate_x`, `plate_z`,
`in_zone`, `pitch_type`, `batter_side`, `result` (`take` / `whiff` / `foul` /
`in_play`), and `bat_speed` and `exit_velo` where they exist.

**`plate_x` is negated on the way out.** In the raw file the right-handed batter's
box sits on the positive side, which is the mirror of the Statcast convention.
Two independent checks fix the sign: the five hit-by-pitches sit at +2.2 to +2.6
for righties and -1.2 to -1.3 for lefties, and pulled balls come off the batter's
own side of the plate. Negating once turns the payload into a conventional
catcher's view, so a client can plot it directly.

`zone` carries the batter's own `top` and `bottom` plus the `half_width` of 0.83
feet, half the plate plus a ball radius. Those three reproduce the `in_zone`
column exactly on all 3,278 pitches, and 0.83 is the only half width that does,
so a drawn zone box and the chase and zone-swing rates can never disagree. `boxes`
lists the sides this batter actually hit from with a pitch count each, so a switch
hitter reports both.

`contexts` is bat tracking cut three ways, each a list of `Split`s in the same
shape the splits endpoint returns:

| Context    | Buckets                                  |
| ---------- | ---------------------------------------- |
| `location` | zone / outside                           |
| `count`    | under_two / two_strikes                  |
| `family`   | fastball / breaking / offspeed           |

Sample floors apply per bucket, so a thin bucket reports a null rate.

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
