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
