<script setup lang="ts">
import { SWING_DECISIONS, formatGap, formatValue, valueUnit } from '../metrics'
import type { StatLine } from '../types'

const props = defineProps<{
  player: StatLine
  team: StatLine
  spread: Record<string, number | null>
}>()

const percent = (value: number | null) => (value === null ? 0 : value * 100)

/* One cross-player standard deviation either side of the team rate, so a gap can
   be read against how much the metric actually varies across the roster. */
const band = (key: keyof StatLine) => {
  const team = props.team[key]
  const deviation = props.spread[key]
  if (typeof team !== 'number' || !deviation) return null
  const low = Math.max(0, (team - deviation) * 100)
  const high = Math.min(100, (team + deviation) * 100)
  return { left: `${low}%`, width: `${high - low}%` }
}

const gap = (key: keyof StatLine) => {
  const player = props.player[key]
  const team = props.team[key]
  return typeof player === 'number' && typeof team === 'number' ? (player - team) * 100 : null
}
</script>

<template>
  <div class="bars">
    <div v-for="metric in SWING_DECISIONS.metrics" :key="metric.key" class="metric">
      <div class="head">
        <span class="label">{{ metric.label }}</span>
        <span class="value numeric">
          {{ formatValue(player[metric.key], metric.format) }}{{ valueUnit(metric) }}
        </span>
        <span v-if="gap(metric.key) !== null" class="gap numeric"
          :class="{ better: (gap(metric.key)! > 0) === metric.higherIsBetter }">
          {{ formatGap(gap(metric.key)!, metric) }}
        </span>
      </div>
      <div class="track">
        <div class="fill" :style="{ width: `${percent(player[metric.key])}%` }" />
        <div v-if="band(metric.key)" class="spread" :style="band(metric.key)!" />
        <div class="baseline" :style="{ left: `${percent(team[metric.key])}%` }">
          <span class="tick-label numeric">{{ formatValue(team[metric.key], metric.format) }}</span>
        </div>
      </div>
    </div>
  </div>

  <p class="key">
    <span class="swatch fill" />This batter
    <span class="swatch tick" />Team baseline
    <span class="swatch spread" />Spread across the roster
    <span class="note">A gold chip means better than the team.</span>
  </p>
</template>

<style scoped>
.bars {
  display: grid;
  gap: 1.35rem;
}

.head {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  margin-bottom: 0.4rem;
}

.label {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--brown);
}

.value {
  font-size: 0.95rem;
  font-weight: 600;
}

.gap {
  min-width: 4rem;
  padding: 0.1rem 0.45rem;
  border-radius: var(--radius);
  background: var(--tint);
  color: var(--muted);
  font-size: 0.8rem;
  font-weight: 700;
  text-align: right;
}

.gap.better {
  background: var(--gold);
  color: var(--brown);
}

.track {
  position: relative;
  height: 14px;
  margin-top: 12px;
  background: var(--tint);
  border: 1px solid var(--line);
  border-radius: 2px;
}

.fill {
  height: 100%;
  background: var(--brown);
  border-radius: 1px;
}

/* One standard deviation of roster spread either side of the team rate. It rides
   just above the bar rather than inside it, so the player's fill never hides
   half the range. Scoped to the track: unscoped it also caught the legend
   swatch and tore it out of the flow. */
.track .spread {
  position: absolute;
  top: -8px;
  height: 4px;
  background: repeating-linear-gradient(
    -45deg,
    var(--rule) 0 1.5px,
    var(--tint) 1.5px 4px
  );
  border-radius: 2px;
}

/* The team rate is the thing every bar is read against, so it is a full-height
   post with its own number rather than a tick lost inside the fill. */
.baseline {
  position: absolute;
  top: -9px;
  bottom: -4px;
  width: 2px;
  background: var(--brown);
  box-shadow: 0 0 0 1.5px var(--surface);
}

.tick-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding-top: 2px;
  font-size: 0.72rem;
  color: var(--muted);
}

.key {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin: 1.9rem 0 0;
  font-size: 0.8rem;
  color: var(--muted);
}

.swatch {
  width: 14px;
  height: 10px;
  border-radius: 1px;
}

.swatch.fill {
  background: var(--brown);
}

.swatch.tick {
  width: 2px;
  height: 14px;
  margin-left: 0.6rem;
  background: var(--brown);
}

.swatch.spread {
  height: 5px;
  margin-left: 0.6rem;
  background: repeating-linear-gradient(
    -45deg,
    var(--rule) 0 1.5px,
    var(--tint) 1.5px 4px
  );
  border-radius: 2px;
}

.note {
  margin-left: auto;
}
</style>
