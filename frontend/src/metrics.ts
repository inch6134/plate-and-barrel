import type { StatLine } from './types'

type Format = 'rate' | 'slash' | 'decimal' | 'count'


export interface MetricSpec {
  key: keyof StatLine
  label: string
  format: Format
  higherIsBetter: boolean
}

export interface MetricGroup {
  label: string
  metrics: MetricSpec[]
}


const FORMATTERS: Record<Format, (value: number) => string> = {
  rate: (value) => `${(value * 100).toFixed(1)}`,
  slash: (value) => value.toFixed(3).replace(/^0/, ''),
  decimal: (value) => value.toFixed(1),
  count: (value) => value.toFixed(0),
}

export const OPS: MetricSpec = { key: 'ops', label: 'OPS', format: 'slash', higherIsBetter: true }

export const SWING_DECISIONS: MetricGroup = {
  label: 'Swing decisions',
  metrics: [
    { key: 'swing_rate', label: 'Swing%', format: 'rate', higherIsBetter: true },
    { key: 'zone_swing_rate', label: 'Z-Swing%', format: 'rate', higherIsBetter: true },
    { key: 'chase_rate', label: 'Chase%', format: 'rate', higherIsBetter: false },
    { key: 'whiff_rate', label: 'Whiff%', format: 'rate', higherIsBetter: false },
    { key: 'contact_rate', label: 'Contact%', format: 'rate', higherIsBetter: true },
  ],
}

export const METRIC_GROUPS: MetricGroup[] = [
  {
    label: 'Batting line',
    metrics: [
      { key: 'avg', label: 'AVG', format: 'slash', higherIsBetter: true },
      { key: 'obp', label: 'OBP', format: 'slash', higherIsBetter: true },
      { key: 'slg', label: 'SLG', format: 'slash', higherIsBetter: true },
      OPS,
      { key: 'k_rate', label: 'K%', format: 'rate', higherIsBetter: false },
      { key: 'bb_rate', label: 'BB%', format: 'rate', higherIsBetter: true },
    ],
  },

  SWING_DECISIONS,

  {
    label: 'Contact quality',
    metrics: [
      { key: 'avg_exit_velo', label: 'Avg EV', format: 'decimal', higherIsBetter: true },
      { key: 'max_exit_velo', label: 'Max EV', format: 'decimal', higherIsBetter: true },
      { key: 'avg_launch_angle', label: 'Avg LA', format: 'decimal', higherIsBetter: true },
      { key: 'hard_hit_rate', label: 'Hard-Hit%', format: 'rate', higherIsBetter: true },
      { key: 'sweet_spot_rate', label: 'Sweet Spot%', format: 'rate', higherIsBetter: true },
      { key: 'barrel_rate', label: 'Barrel%', format: 'rate', higherIsBetter: true },
      { key: 'avg_bat_speed', label: 'Bat Speed', format: 'decimal', higherIsBetter: true },
      { key: 'avg_attack_angle', label: 'Attack Angle', format: 'decimal', higherIsBetter: true },
    ],
  },
  {
    label: 'Counting',
    metrics: [
      { key: 'pa', label: 'PA', format: 'count', higherIsBetter: true },
      { key: 'ab', label: 'AB', format: 'count', higherIsBetter: true },
      { key: 'hits', label: 'H', format: 'count', higherIsBetter: true },
      { key: 'doubles', label: '2B', format: 'count', higherIsBetter: true },
      { key: 'triples', label: '3B', format: 'count', higherIsBetter: true },
      { key: 'home_runs', label: 'HR', format: 'count', higherIsBetter: true },
      { key: 'total_walks', label: 'BB', format: 'count', higherIsBetter: true },
      { key: 'strikeouts', label: 'K', format: 'count', higherIsBetter: false },
    ],
  },
]


export const formatValue = (value: number | null, format: Format) =>
  value === null ? '-' : FORMATTERS[format](value)
