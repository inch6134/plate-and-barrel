import type { StatLine } from './types'

type Format = 'rate' | 'slash' | 'decimal' | 'count'


export interface MetricSpec {
  key: keyof StatLine
  label: string
  format: Format
  higherIsBetter: boolean
  unit: string
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

export const OPS: MetricSpec = { key: 'ops', label: 'OPS', format: 'slash', higherIsBetter: true, unit: '' }

export const BATTING_LINE: MetricGroup = {
  label: 'Batting line',
  metrics: [
    { key: 'avg', label: 'AVG', format: 'slash', higherIsBetter: true, unit: '' },
    { key: 'obp', label: 'OBP', format: 'slash', higherIsBetter: true, unit: '' },
    { key: 'slg', label: 'SLG', format: 'slash', higherIsBetter: true, unit: '' },
    OPS,
    { key: 'k_rate', label: 'K%', format: 'rate', higherIsBetter: false, unit: 'pts' },
    { key: 'bb_rate', label: 'BB%', format: 'rate', higherIsBetter: true, unit: 'pts' },
  ],
}

export const SWING_DECISIONS: MetricGroup = {
  label: 'Swing decisions',
  metrics: [
    { key: 'swing_rate', label: 'Swing%', format: 'rate', higherIsBetter: true, unit: 'pts' },
    { key: 'zone_swing_rate', label: 'Z-Swing%', format: 'rate', higherIsBetter: true, unit: 'pts' },
    { key: 'chase_rate', label: 'Chase%', format: 'rate', higherIsBetter: false, unit: 'pts' },
    { key: 'whiff_rate', label: 'Whiff%', format: 'rate', higherIsBetter: false, unit: 'pts' },
    { key: 'contact_rate', label: 'Contact%', format: 'rate', higherIsBetter: true, unit: 'pts' },
  ],
}

export const CONTACT_QUALITY: MetricGroup = {
  label: 'Contact quality',
  metrics: [
    { key: 'avg_exit_velo', label: 'Avg EV', format: 'decimal', higherIsBetter: true, unit: 'mph' },
    { key: 'max_exit_velo', label: 'Max EV', format: 'decimal', higherIsBetter: true, unit: 'mph' },
    { key: 'avg_launch_angle', label: 'Avg LA', format: 'decimal', higherIsBetter: true, unit: '°' },
    { key: 'hard_hit_rate', label: 'Hard-Hit%', format: 'rate', higherIsBetter: true, unit: 'pts' },
    { key: 'sweet_spot_rate', label: 'Sweet Spot%', format: 'rate', higherIsBetter: true, unit: 'pts' },
    { key: 'barrel_rate', label: 'Barrel%', format: 'rate', higherIsBetter: true, unit: 'pts' },
    { key: 'avg_bat_speed', label: 'Bat Speed', format: 'decimal', higherIsBetter: true, unit: 'pts' },
    { key: 'avg_attack_angle', label: 'Attack Angle', format: 'decimal', higherIsBetter: true, unit: '°' },
    { key: 'pull_rate', label: 'Pull%', format: 'rate', unit: 'pts', higherIsBetter: true },
    { key: 'center_rate', label: 'Center%', format: 'rate', unit: 'pts', higherIsBetter: true },
    { key: 'oppo_rate', label: 'Oppo%', format: 'rate', unit: 'pts', higherIsBetter: true },
  ],
}

export const COUNTING: MetricGroup = {
  label: 'Counting',
  metrics: [
    { key: 'pa', label: 'PA', format: 'count', higherIsBetter: true, unit: '' },
    { key: 'ab', label: 'AB', format: 'count', higherIsBetter: true, unit: '' },
    { key: 'hits', label: 'H', format: 'count', higherIsBetter: true, unit: '' },
    { key: 'doubles', label: '2B', format: 'count', higherIsBetter: true, unit: '' },
    { key: 'triples', label: '3B', format: 'count', higherIsBetter: true, unit: '' },
    { key: 'home_runs', label: 'HR', format: 'count', higherIsBetter: true, unit: '' },
    { key: 'total_walks', label: 'BB', format: 'count', higherIsBetter: true, unit: '' },
    { key: 'strikeouts', label: 'K', format: 'count', higherIsBetter: false, unit: '' },
  ],
}

export const METRIC_GROUPS: MetricGroup[] = [BATTING_LINE, SWING_DECISIONS, CONTACT_QUALITY, COUNTING,]

export const SPLIT_METRICS = [...SWING_DECISIONS.metrics, ...CONTACT_QUALITY.metrics].filter(
  (metric) => metric.key !== 'max_exit_velo',
)

export const formatValue = (value: number | null, format: Format) =>
  value === null ? '-' : FORMATTERS[format](value)

export const METRIC_SPECS = new Map<string, MetricSpec>(
  METRIC_GROUPS.flatMap((group) => group.metrics).map((metric) => [metric.key, metric]),
)
