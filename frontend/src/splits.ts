export const DIMENSIONS = [
  { code: 'count', label: 'Count' },
  { code: 'outs', label: 'Outs' },
  { code: 'bases', label: 'Runners' },
  { code: 'inning', label: 'Inning' },
  { code: 'hand', label: 'Pitcher hand' },
  { code: 'role', label: 'Pitcher role' },
]

export const BUCKET_LABELS: Record<string, string> = {
  ahead: 'Ahead in count',
  even: 'Even count',
  behind: 'Behind in count',
  '0': 'No outs',
  '1': 'One out',
  '2': 'Two outs',
  early: 'Innings 1 to 3',
  middle: 'Innings 4 to 6',
  late: 'Innings 7 and later',
  empty: 'Bases empty',
  on_base: 'Runner on',
  scoring: 'Scoring position',
  L: 'vs left-handers',
  R: 'vs right-handers',
  starter: 'vs starters',
  reliever: 'vs relievers',
}
