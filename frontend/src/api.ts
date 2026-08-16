import type { LeaderboardEntry, Player, PlayerDetail, StatLine } from './types'

const request = async <T>(path: string, params: Record<string, string> = {}): Promise<T> => {
  const query = new URLSearchParams(params).toString()
  const response = await fetch(`/api${path}${query ? `?${query}` : ''}`)
  if (!response.ok) throw new Error(`Request to ${path} failed with ${response.status}`)
  return response.json() as Promise<T>
}

export const fetchPlayers = () => request<Player[]>('/players')

export const fetchPlayer = (batterId: number) => request<PlayerDetail>(`/players/${batterId}`)

export const fetchTeam = () => request<StatLine>('/team')

export const fetchLeaderboard = (metric: string, order: string) =>
  request<LeaderboardEntry[]>('/leaderboard', { metric, order })

export const headshotUrl = (batterId: number) =>
  `https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${batterId}/headshot/67/current`
