<script setup lang="ts">
import { SWING_DECISIONS, formatValue } from '../metrics'
import type { StatLine } from '../types'

const props = defineProps<{ player: StatLine; team: StatLine }>()

const percent = (value: number | null) => (value === null ? 0 : value * 100)

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
        <span class="value numeric">{{ formatValue(player[metric.key], metric.format) }}</span>
        <span v-if="gap(metric.key) !== null" class="gap numeric"
          :class="{ better: (gap(metric.key)! > 0) === metric.higherIsBetter }">
          {{ gap(metric.key)! > 0 ? '+' : '' }}{{ gap(metric.key)!.toFixed(1) }}
        </span>
      </div>
      <div class="track">
        <div class="fill" :style="{ width: `${percent(player[metric.key])}%` }" />
        <div class="baseline" :style="{ left: `${percent(team[metric.key])}%` }" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.bars {
  display: grid;
  gap: 1rem;
}

.head {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  margin-bottom: 0.35rem;
}

.label {
  flex: 1;
  font-size: 0.9rem;
  color: var(--ink-2);
}

.value {
  font-size: 0.95rem;
  font-weight: 600;
}

.gap {
  min-width: 3.2rem;
  padding: 0.08rem 0.4rem;
  border-radius: var(--radius);
  background: var(--tint);
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 700;
  text-align: right;
}

/* Brown, not gold. Gold is rationed to four jobs page-wide and five bars would
   spend the whole budget in one panel. */
.gap.better {
  background: var(--brown);
  color: var(--surface);
}

.track {
  position: relative;
  height: 9px;
  background: var(--tint);
  border-radius: 999px;
  overflow: hidden;
}

.fill {
  height: 100%;
  background: var(--brown);
  border-radius: 999px;
}

.baseline {
  position: absolute;
  top: -2px;
  bottom: -2px;
  width: 2px;
  background: var(--muted);
}
</style>
