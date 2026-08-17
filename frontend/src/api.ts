import type { LeaderboardEntry, Player, PlayerDetail, SwingProfile, SprayChart, Splits, Insight } from './types'

const request = async <T>(path: string, params: Record<string, string> = {}): Promise<T> => {
  const query = new URLSearchParams(params).toString()
  const response = await fetch(`/api${path}${query ? `?${query}` : ''}`)
  if (!response.ok) throw new Error(`Request to ${path} failed with ${response.status}`)
  return response.json() as Promise<T>
}

export const fetchPlayers = () => request<Player[]>('/players')

export const fetchPlayer = (batterId: number) => request<PlayerDetail>(`/players/${batterId}`)

export const fetchLeaderboard = (metric: string, order: string) =>
  request<LeaderboardEntry[]>('/leaderboard', { metric, order })

export const fetchSwingProfile = (batterId: number, pitchType: string, family: string) =>
  request<SwingProfile>(`/players/${batterId}/swing-profile`, {
    ...(pitchType ? { pitch_type: pitchType } : {}),
    ...(family ? { family } : {}),
  })

export const fetchSprayChart = (batterId: number, trajectory: string, outcome: string) =>
  request<SprayChart>(`/players/${batterId}/spray-chart`, {
    ...(trajectory ? { trajectory } : {}),
    ...(outcome ? { outcome } : {}),
  })

export const fetchSplits = (batterId: number, dimension: string) =>
  request<Splits>(`/players/${batterId}/splits`, { dimension })

export const fetchInsights = (batterId: number, view: string) =>
  request<Insight[]>('/insights', { batter_id: String(batterId), view })

export const headshotUrl = (batterId: number) =>
  `https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${batterId}/headshot/67/current`

