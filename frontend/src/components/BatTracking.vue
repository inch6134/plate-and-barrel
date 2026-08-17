<script setup lang="ts">
import { computed, ref } from 'vue'
import { BAT_TRACKING, formatGap, formatValue, valueUnit } from '../metrics'
import FilterPills from './FilterPills.vue'
import type { ContextSplit } from '../types'

const props = defineProps<{ contexts: ContextSplit[] }>()

const CONTEXT_LABELS: Record<string, string> = {
  location: 'By location',
  count: 'By count',
  family: 'By pitch type',
}

const BUCKET_LABELS: Record<string, string> = {
  zone: 'In the zone',
  outside: 'Outside',
  under_two: 'Under two strikes',
  two_strikes: 'Two strikes',
  fastball: 'Fastballs',
  breaking: 'Breaking',
  offspeed: 'Offspeed',
}

const options = BAT_TRACKING.metrics.map((option) => ({
  code: option.key,
  label: option.label,
}))

const chosen = ref(BAT_TRACKING.metrics[0].key)
const metric = computed(
  () => BAT_TRACKING.metrics.find((option) => option.key === chosen.value)!,
)

const readings = computed(() =>
  props.contexts.map((context) => ({
    key: context.context,
    label: CONTEXT_LABELS[context.context],
    rows: context.buckets.map((bucket) => {
      const player = bucket.player[metric.value.key]
      const team = bucket.team[metric.value.key]
      const comparable = typeof player === 'number' && typeof team === 'number'
      return {
        key: bucket.bucket,
        label: BUCKET_LABELS[bucket.bucket],
        swings: bucket.player.swings,
        player: formatValue(player as number | null, metric.value.format),
        team: formatValue(team as number | null, metric.value.format),
        gap: comparable ? formatGap(player - team, metric.value) : null,
        better: comparable && player > team === metric.value.higherIsBetter,
      }
    }),
  })),
)
</script>

<template>
  <section class="panel tracking">
    <header class="head">
      <h3 class="eyebrow">Bat tracking by context</h3>
      <FilterPills v-model="chosen" :options="options" />
    </header>

    <div v-for="context in readings" :key="context.key" class="context">
      <h4 class="eyebrow">{{ context.label }}</h4>
      <dl>
        <div v-for="row in context.rows" :key="row.key" class="row">
          <dt>
            {{ row.label }}
            <span class="sample numeric">{{ row.swings }} swings</span>
          </dt>
          <dd v-if="row.gap === null" class="gated numeric">below floor</dd>
          <template v-else>
            <dd class="value numeric">{{ row.player }}{{ valueUnit(metric) }}</dd>
            <dd class="gap numeric" :class="{ better: row.better }">{{ row.gap }}</dd>
            <dd class="team numeric">vs. team {{ row.team }}{{ valueUnit(metric) }}</dd>
          </template>
        </div>
      </dl>
    </div>

    <p class="footnote">
      Averages exclude bunt attempts and cover swings with a tracked bat speed. A
      bucket under the 20-swing floor reports no rate.
    </p>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.6rem 1rem;
  margin-bottom: 1.1rem;
}

.context {
  margin-bottom: 1.2rem;
}

h4 {
  margin-bottom: 0.35rem;
}

dl {
  margin: 0;
}

.row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: baseline;
  gap: 0.15rem 0.7rem;
  padding: 0.45rem 0;
  border-bottom: 1px solid var(--line);
  font-size: 0.9rem;
}

.row:last-child {
  border-bottom: 0;
}

dt {
  grid-row: span 2;
  color: var(--ink-2);
}

.sample {
  display: block;
  font-size: 0.76rem;
  color: var(--muted);
}

dd {
  margin: 0;
}

.value {
  font-size: 1rem;
  font-weight: 700;
  text-align: right;
}

.team {
  grid-column: 2 / -1;
  font-size: 0.78rem;
  color: var(--muted);
  text-align: right;
}

.gap {
  min-width: 4.2rem;
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

.gated {
  grid-column: 2 / -1;
  color: var(--muted);
  font-size: 0.85rem;
  text-align: right;
}

.footnote {
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.45;
  color: var(--muted);
}
</style>
