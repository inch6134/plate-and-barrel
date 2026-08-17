# Plate & Barrel

A batting analytics dashboard over one month of San Diego Padres pitch-level data:
every pitch from the 22 games between July 2 and July 31, 2024, scoped to the 15
Padres batters who appear in it.

It attempts to answer the following questions:

1. **Is this batter making good swing decisions?** Where pitches arrived, which he
   offered at, and what came of it.
2. **When he does swing, how good is the contact?** Where the ball went, how hard,
   and how that compares to the rest of the roster.

Every number a player is shown against is the team baseline over the same filter,
because a rate on 176 swings means little without something to read it against.

## Running it

Requires **Python 3.14+**, **Node 22.12+**, and [uv](https://docs.astral.sh/uv/).
From a clean clone:

```bash
# 1. Backend dependencies
uv sync

# 2. Frontend dependencies and build
cd frontend && npm install && npm run build && cd ..

# 3. Serve the API and the built app together on http://127.0.0.1:8000
uv run fastapi run app/main.py
```

There is no database to provision, no migrations, no environment variables, and no network access needed at runtime: the pitch CSV and the player bios are both committed.

### Working on the frontend

For hot reload, run the two halves separately. Vite proxies `/api` to the backend.

```bash
uv run fastapi dev app/main.py      # terminal 1, port 8000
cd frontend && npm run dev       # terminal 2, port 5173
```

### Checks

```bash
uv run pytest                              # 41 tests
cd frontend && npx vue-tsc --noEmit        # typecheck
cd frontend && npm run build               # production build
```

The backend does not need a built frontend. `app/main.py` mounts `frontend/dist`
only when it exists, so `uv run pytest` and API-only development work on a fresh
clone; the one test that asserts the app shell is served skips itself when the
build is absent.

## Technology Stack

| Layer | Choice | Why |
| --- | --- | --- |
| Data | Polars over the CSV, read once behind an `lru_cache` | 3,354 rows is one flat table with no schema evolution. A database would be added at scale. |
| API | FastAPI, stateless and read-only | Pydantic response models make the contract explicit and typed at the boundary. |
| Frontend | Vue 3, `<script setup>`, TypeScript, Vite | Three tabs behind a component switch need no router and no store. |
| Charts | D3 for scales and field geometry, SVG rendered by Vue | The two centrepiece charts are custom geometry that no chart library draws. D3 does the math; Vue does the DOM. |
| Styling | Scoped SFC styles and CSS custom properties | No framework, no component library. |

Aggregation costs about 5ms over the full frame, so there is no caching layer
beyond the CSV load. If the data ever outgrew one process the swap point is the
load function, not the filtering or aggregation downstream of it.

**One aggregation entry point.** `summarize(frame, by)` takes any frame and any
group-by and returns counts plus rates. `by=[]` gives a team total, `by=["batter_bam_id"]`
gives per-player, `by=["count_state"]` gives a split. Every endpoint composes
filters onto a frame and calls it, which is why the team baseline in every view is
guaranteed to be the same computation as the player line it sits beside.

Counts and rates are computed in separate phases and every rate ships with its
numerator and denominator, so the UI can show a sample size without a second
request.

## Data Notes

**`hit_exit_speed` is populated on foul balls, not just balls in play.** Filtering
on `hit_exit_speed.is_not_null()` alone gives 1,251 rows. Contact-quality metrics
filter on a derived `batted_ball` column, `in_play & hit_exit_speed.is_not_null()`,
which gives the correct **626**.

**76 rows have `is_pitch == False`.** They are excluded from pitch-level
denominators by null propagation rather than dropped at load, because two
intentional walks terminate on those rows and dropping them would lose 2 PA.

**PA is 830, not 831.** It is `terminating & event_type not in BASERUNNING_EVENTS`.
One `caught_stealing_2b` row is terminating but is not a plate appearance.

**`hit_bearing` runs from -118.7 to +162.1 degrees**, well past the foul lines, so
balls caught in foul territory plot outside the wedge and two plot behind home
plate. The spray chart frame is sized to the data, not to the field. Negative is
left field, verified against fielder positions. `hit_horizontal_angle` is a
different column and is not loaded.

**`plate_x` is mirrored from the Statcast convention.** In this file the
right-handed batter's box sits on the *positive* side. Two independent checks fix
the sign:

| Check | Right-handed | Left-handed |
| --- | --- | --- |
| The five hit-by-pitches, which must be on the batter's own side | +2.17 to +2.57 | -1.28 to -1.20 |
| Mean `plate_x` on pulled balls (inside pitches get pulled) | +0.018 | -0.108 |

The API negates `plate_x` once on the way out so clients receive a conventional
catcher's view. Drawn raw, inside and outside would be backwards on every chart.

**The strike zone is exactly reproducible.** `in_zone` is matched perfectly by
`|plate_x| <= 0.83` within the batter's own `strikezone_top` and `strikezone_bot`,
on **all 3,278 pitches**. 0.83 feet is the only half width that agrees (0.82 and
0.84 both fail), being half the plate plus a ball radius. Each batter's zone is
constant across the month. This is why the drawn zone box and the chase and
zone-swing rates beside it can never disagree.

**`batter_side` varies per plate appearance.** Profar and Johnson bat from both
sides, so player-level side is derived as `S` and nothing ever groups by
`batter_bam_id, batter_side`. The zone plot draws a label for each side a batter
actually used, with the pitch count each saw.

**`infer_schema_length=None` is required on the CSV read.** `hit_distance` is
whole-numbered for several hundred rows before turning fractional, so a sampled
inference reads it as an integer column and throws.

## Metric definitions

Standard definitions throughout, verified against the data rather than assumed.

| Metric | Definition |
| --- | --- |
| Whiff% | `swinging_strike / swing` |
| Chase% | `chase / pitches outside the zone` |
| Contact% | `contact / swing` |
| Z-Swing% | swings at in-zone pitches / in-zone pitches |
| Avg / Max EV | mean and max `hit_exit_speed` over batted balls |
| Hard-Hit% | share of batted balls at 95 mph or more |
| Sweet Spot% | share with launch angle between 8 and 32 degrees |
| Barrel% | share meeting the barrel window below |
| Pull / Center / Oppo% | share by spray direction, centre being within 15 degrees of dead centre, handedness-aware |
| Bat Speed, Attack Angle | mean over non-bunt swings with tracking |
| PA | terminating rows, excluding baserunning events |
| AB | PA minus walks, HBP, sacrifice flies and sacrifice bunts |
| AVG / OBP / SLG / OPS | standard |
| K% / BB% | strikeouts and total walks over PA |

**The barrel window** is `exit velocity >= 98` with launch angle between
`max(124 - v, 8)` and `min(round(30 + (10/9)(v - 98)), 50)`.

**Stolen bases are absent** because `stolen_base` never appears as an `event_type`
anywhere in the file. That is a data limitation, not a scope decision.

## Sample floors

Set from the actual per-batter counts:

- **20 swings** for swing-decision and bat-tracking metrics
- **10 batted balls** for contact quality
- **20 PA** for the batting line

Rate leaderboards return 12 of the 15 batters; count leaderboards return all 15.
Floors apply per bucket in splits, so a thin bucket reports no rate rather than a
misleading one.

## Future Improvements

- **A pitching dashboard.** The file has full pitcher data, movement and release
  included, and the same aggregation layer would serve it unchanged.
- **Per-batter zone heat maps** rather than raw scatter, once there are enough
  pitches per cell.
- **Real caching and a database** if the data grew past one team-month, swapping
  the load function and leaving everything downstream alone.
