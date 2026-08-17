export interface Player {
  batter_bam_id: number
  name_first: string
  name_last: string
  side: string
  number: string
  position: string
  height: string
  weight: number
  age: number
  debut_date: string
  throws: string
}

export interface StatLine {
  pitches: number
  zone_pitches: number
  out_of_zone_pitches: number
  swings: number
  zone_swings: number
  chases: number
  contacts: number
  whiffs: number
  batted_balls: number
  hard_hits: number
  sweet_spots: number
  barrels: number
  pulled: number
  up_the_middle: number
  opposite: number
  pa: number
  ab: number
  hits: number
  singles: number
  doubles: number
  triples: number
  home_runs: number
  walks: number
  intentional_walks: number
  total_walks: number
  hit_by_pitches: number
  strikeouts: number
  sac_flies: number
  sac_bunts: number
  total_bases: number
  swing_rate: number | null
  zone_swing_rate: number | null
  chase_rate: number | null
  whiff_rate: number | null
  contact_rate: number | null
  avg_exit_velo: number | null
  max_exit_velo: number | null
  avg_launch_angle: number | null
  hard_hit_rate: number | null
  sweet_spot_rate: number | null
  barrel_rate: number | null
  pull_rate: number | null
  center_rate: number | null
  oppo_rate: number | null
  avg_bat_speed: number | null
  avg_attack_angle: number | null
  avg: number | null
  obp: number | null
  slg: number | null
  ops: number | null
  k_rate: number | null
  bb_rate: number | null
}

export interface PlayerDetail {
  player: Player
  stats: StatLine
}

export interface LeaderboardEntry {
  batter_bam_id: number
  name_first: string
  name_last: string
  value: number
  sample: number
}

export interface Swing {
  bat_speed: number
  attack_angle: number | null
  pitch_type: string
  in_zone: boolean
  result: 'in_play' | 'foul' | 'whiff'
  event_type: string | null
  exit_velo: number | null
  launch_angle: number | null
  distance: number | null
  hard_hit: boolean
  barrel: boolean
}

export interface FilterOption {
  code: string
  count: number
}

export interface SwingProfile {
  player: StatLine
  team: StatLine
  swings: Swing[]
  pitch_types: FilterOption[]
}

export interface BattedBall {
  bearing: number
  distance: number
  exit_velo: number
  launch_angle: number
  trajectory: string
  event_type: string
  pitch_type: string
  game_date: string
  is_hit: boolean
  hard_hit: boolean
  barrel: boolean
}

export interface SprayChart {
  player: StatLine
  team: StatLine
  batted_balls: BattedBall[]
  trajectories: FilterOption[]
}

export interface Split {
  bucket: string
  player: StatLine
  team: StatLine
}

export interface Splits {
  dimension: string
  splits: Split[]
}

export interface Insight {
  metric: string
  dimension: string | null
  scope: string
  value: number
  baseline: number
  sample: number
  sample_column: string
}
