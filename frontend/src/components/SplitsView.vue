<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { fetchSplits } from '../api'
import { useResource } from '../composables/useResource'
import { SPLIT_METRICS, formatValue } from '../metrics'
import { BUCKET_LABELS, DIMENSIONS } from '../splits'
import type { MetricSpec } from '../metrics'
import type { Split } from '../types'

const props = defineProps<{ batterId: number }>()

const PLOT_LEFT = 170
const PLOT_RIGHT = 630
const ROW_HEIGHT = 46
const TOP = 14

const dimension = ref(DIMENSIONS[0].code)
const metric = ref<MetricSpec>(SPLIT_METRICS[2])
const selected = ref<Split>()

watch([() => props.batterId, dimension], () => (selected.value = undefined))

const { data, error } = useResource(() => fetchSplits(props.batterId, dimension.value))

const valueOf = (split: Split, side: 'player' | 'team') => {
  const value = split[side][metric.value.key]
  return typeof value === 'number' ? value : null
}

const rows = computed(() => data.value?.splits ?? [])

const domain = computed(() => {
  const values = rows.value
    .flatMap((split) => [valueOf(split, 'player'), valueOf(split, 'team')])
    .filter((value): value is number => value !== null)
  const low = Math.min(...values)
  const high = Math.max(...values)
  const pad = (high - low || Math.abs(high) || 1) * 0.18
  return [low - pad, high + pad]
})

const scale = (value: number) =>
  PLOT_LEFT + ((value - domain.value[0]) / (domain.value[1] - domain.value[0])) * (PLOT_RIGHT - PLOT_LEFT)

const height = computed(() => TOP + rows.value.length * ROW_HEIGHT + 34)
const axisY = computed(() => TOP + rows.value.length * ROW_HEIGHT + 6)
const plotted = computed(() => rows.value.filter((split) => valueOf(split, 'player') !== null))
</script>

<template>
  <div v-if="error" class="panel pad">{{ error }}</div>
  <div v-else-if="data" class="splits">
    <nav class="filters">
      <button v-for="option in DIMENSIONS" :key="option.code" type="button" :class="{ on: dimension === option.code }"
        @click="dimension = option.code">
        {{ option.label }}
      </button>
    </nav>

    <section class="panel pad">
      <header class="head">
        <h3 class="eyebrow">Player against team baseline</h3>
        <select v-model="metric" aria-label="Metric">
          <option v-for="option in SPLIT_METRICS" :key="option.key" :value="option">
            {{ option.label }}
          </option>
        </select>
      </header>

      <p v-if="plotted.length === 0" class="empty">
        Every bucket falls below the sample floor for {{ metric.label }}.
      </p>

      <svg v-else :viewBox="`0 0 660 ${height}`" role="img" :aria-label="`${metric.label} by split`">
        <g v-for="(split, index) in rows" :key="split.bucket" :transform="`translate(0, ${TOP + index * ROW_HEIGHT})`"
          :class="{ row: true, chosen: selected?.bucket === split.bucket }" @click="selected = split">
          <rect class="hit-area" x="0" y="0" width="660" :height="ROW_HEIGHT" />
          <text class="bucket" x="158" y="26" text-anchor="end">
            {{ BUCKET_LABELS[split.bucket] }}
          </text>
          <template v-if="valueOf(split, 'player') !== null && valueOf(split, 'team') !== null">
            <line class="gap" :x1="scale(valueOf(split, 'team')!)" :x2="scale(valueOf(split, 'player')!)" y1="21"
              y2="21" />
            <circle class="team" :cx="scale(valueOf(split, 'team')!)" cy="21" r="5" />
            <circle class="player" :cx="scale(valueOf(split, 'player')!)" cy="21" r="6" />
            <text class="reading numeric" :x="scale(valueOf(split, 'player')!)" y="40" text-anchor="middle">
              {{ formatValue(valueOf(split, 'player'), metric.format) }}
            </text>
          </template>
          <text v-else class="reading numeric" :x="PLOT_LEFT" y="26">Below sample floor</text>
        </g>

        <line class="axis" :x1="PLOT_LEFT" :x2="PLOT_RIGHT" :y1="axisY" :y2="axisY" />
        <text class="tick numeric" :x="PLOT_LEFT" :y="axisY + 16">
          {{ formatValue(domain[0], metric.format) }}
        </text>
        <text class="tick numeric" :x="PLOT_RIGHT" :y="axisY + 16" text-anchor="end">
          {{ formatValue(domain[1], metric.format) }}
        </text>
      </svg>

      <figcaption>
        <span class="key player">This batter</span>
        <span class="key team">Team</span>
      </figcaption>

      <p v-if="selected" class="readout numeric">
        {{ BUCKET_LABELS[selected.bucket] }} &middot;
        {{ selected.player.pitches }} pitches &middot;
        {{ selected.player.swings }} swings &middot;
        {{ selected.player.whiffs }} whiffs &middot;
        {{ selected.player.batted_balls }} batted balls &middot;
        {{ selected.player.hits }} hits in {{ selected.player.ab }} AB
      </p>
      <p v-else class="readout muted">Select a split for its underlying counts.</p>
    </section>
  </div>
</template>

<style scoped>
.splits {
  display: grid;
  gap: 0.7rem;
}

.pad {
  padding: 1.1rem 1.25rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.filters button {
  padding: 0.3rem 0.6rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: 0.78rem;
  cursor: pointer;
}

.filters button.on {
  background: var(--brown);
  border-color: var(--brown);
  color: var(--paper);
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.6rem;
}

.head select {
  padding: 0.3rem 0.45rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 3px;
  font-size: 0.8rem;
}

svg {
  width: 100%;
  height: auto;
}

.row {
  cursor: pointer;
}

.hit-area {
  fill: transparent;
}

.row:hover .hit-area,
.row.chosen .hit-area {
  fill: var(--tint);
}

.bucket {
  fill: var(--brown);
  font-size: 12px;
}

.gap {
  stroke: var(--line);
  stroke-width: 3;
}

.team {
  fill: var(--surface);
  stroke: var(--muted);
  stroke-width: 2;
}

.player {
  fill: var(--brown);
}

.reading {
  fill: var(--muted);
  font-size: 11px;
}

.axis {
  stroke: var(--line);
}

.tick {
  fill: var(--muted);
  font-size: 11px;
}

figcaption {
  display: flex;
  gap: 0.9rem;
  margin-top: 0.4rem;
  font-size: 0.72rem;
  color: var(--muted);
}

.key::before {
  content: '';
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 0.3rem;
  border-radius: 50%;
}

.key.player::before {
  background: var(--brown);
}

.key.team::before {
  border: 2px solid var(--muted);
}

.empty,
.readout {
  margin: 0.6rem 0 0;
  font-size: 0.78rem;
  min-height: 1.2em;
}

.empty,
.readout.muted {
  color: var(--muted);
}
</style>
