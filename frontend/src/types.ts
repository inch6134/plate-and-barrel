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
