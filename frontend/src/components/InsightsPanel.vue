<script setup lang="ts">
import { computed } from 'vue'
import { fetchInsights } from '../api'
import { useResource } from '../composables/useResource'
import { METRIC_SPECS, formatGap, formatValue, valueUnit } from '../metrics'
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
  const unit = valueUnit(metric)
  return {
    key: `${insight.metric}-${insight.scope}`,
    label: metric.label,
    value: formatValue(insight.value, metric.format) + unit,
    baseline: formatValue(insight.baseline, metric.format) + unit,
    gap: formatGap(gap, metric),
    scope: insight.dimension ? BUCKET_LABELS[insight.scope] : '',
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
    <h3 class="eyebrow section-head">What stands out</h3>
    <ul>
      <li v-for="insight in insights" :key="insight.key">
        <span class="gap numeric" :class="{ better: insight.better }">{{ insight.gap }}</span>
        <span class="text">
          <strong>{{ insight.label }}:</strong>
          <span class="reading numeric">{{ insight.value }}</span>
          <span class="against">vs.&nbsp;team</span>
          <span class="reading numeric">{{ insight.baseline }}</span>
          <span v-if="insight.scope" class="context">{{ insight.scope }}</span>
          <span class="context numeric">{{ insight.sample }}</span>
        </span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.55rem;
}

li {
  display: flex;
  align-items: baseline;
  gap: 0.8rem;
  font-size: 0.9rem;
  line-height: 1.45;
}

.gap {
  flex: none;
  min-width: 5rem;
  padding: 0.12rem 0.45rem;
  border-radius: var(--radius);
  background: var(--tint);
  color: var(--ink-2);
  font-size: 0.8rem;
  font-weight: 700;
  text-align: right;
}

.gap.better {
  background: var(--gold);
  color: var(--brown);
}

.text {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.1rem 0.45rem;
  color: var(--muted);
}

strong {
  color: var(--brown);
  font-weight: 700;
}

/* The player's own number is the payload of the line, so it outsizes the prose
   around it and the baseline it is measured against. */
.reading {
  color: var(--brown);
  font-weight: 700;
  font-size: 1.02rem;
}

.reading + .against + .reading {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--ink-2);
}

.against {
  font-size: 0.82rem;
}

/* Scope and sample are the caveat, so they sit behind a separator and lighter. */
.context {
  font-size: 0.82rem;
}

.context::before {
  content: '·';
  margin-right: 0.45rem;
}
</style>
