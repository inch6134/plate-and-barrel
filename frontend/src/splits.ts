export const DIMENSIONS = [
  { code: 'count', label: 'Count' },
  { code: 'bases', label: 'Runners' },
  { code: 'inning', label: 'Inning' },
  { code: 'hand', label: 'Pitcher hand' },
]

export const BUCKET_LABELS: Record<string, string> = {
  ahead: 'Ahead in count',
  even: 'Even count',
  behind: 'Behind in count',
  early: 'Innings 1 to 3',
  middle: 'Innings 4 to 6',
  late: 'Innings 7 and later',
  empty: 'Bases empty',
  on_base: 'Runner on',
  scoring: 'Scoring position',
  L: 'vs left-handers',
  R: 'vs right-handers',
}
