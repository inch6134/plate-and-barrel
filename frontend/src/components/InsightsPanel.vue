<script setup lang="ts">
import { computed } from 'vue'
import { fetchInsights } from '../api'
import { useResource } from '../composables/useResource'
import { METRIC_SPECS, formatValue } from '../metrics'
import { BUCKET_LABELS } from '../splits'
import type { Insight } from '../types'
import type { MetricSpec } from '../metrics'

const props = defineProps<{ batterId: number; view: string }>()

const SAMPLE_NOUNS: Record<string, string> = {
  swings: 'swings',
  batted_balls: 'batted balls',
  pa: 'plate appearances',
}

const { data } = useResource(() => fetchInsights(props.batterId, props.view))

const describe = (insight: Insight, metric: MetricSpec) => {
  const gap =
    metric.format === 'rate'
      ? (insight.value - insight.baseline) * 100
      : insight.value - insight.baseline
  return {
    key: `${insight.metric}-${insight.scope}`,
    label: metric.label,
    value: formatValue(insight.value, metric.format),
    baseline: formatValue(insight.baseline, metric.format),
    gap: `${gap > 0 ? '+' : ''}${gap.toFixed(1)}${metric.unit ? ` ${metric.unit}` : ''}`,
    scope: insight.dimension ? BUCKET_LABELS[insight.scope] : 'overall',
    sample: `${insight.sample} ${SAMPLE_NOUNS[insight.sample_column]}`,
    better: gap > 0 === metric.higherIsBetter,
  }
}

const insights = computed(() =>
  (data.value ?? []).flatMap((insight) => {
    const metric = METRIC_SPECS.get(insight.metric)
    return metric ? [describe(insight, metric)] : []
  }),
)
</script>

<template>
  <section v-if="insights.length" class="panel insights">
    <h3 class="eyebrow">What stands out</h3>
    <ul>
      <li v-for="insight in insights" :key="insight.key">
        <span class="gap numeric" :class="{ better: insight.better }">{{ insight.gap }}</span>
        <span class="text">
          <strong>{{ insight.label }}</strong>
          <span class="numeric">{{ insight.value }}</span>
          against the team's
          <span class="numeric">{{ insight.baseline }}</span>
          {{ insight.scope }}, on {{ insight.sample }}.
        </span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.insights {
  padding: 0.9rem 1.25rem;
}

ul {
  margin: 0.5rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.4rem;
}

li {
  display: flex;
  align-items: baseline;
  gap: 0.7rem;
  font-size: 0.82rem;
}

.gap {
  flex: none;
  min-width: 4.6rem;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  background: var(--tint);
  color: var(--muted);
  font-size: 0.76rem;
  font-weight: 600;
  text-align: right;
}

.gap.better {
  background: var(--gold);
  color: var(--brown);
}

.text {
  color: var(--muted);
}

strong {
  color: var(--brown);
  font-weight: 600;
  margin-right: 0.2rem;
}

.text .numeric {
  color: var(--brown);
  font-weight: 600;
}
</style>
