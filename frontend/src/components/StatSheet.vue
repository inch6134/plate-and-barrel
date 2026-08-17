<script setup lang="ts">
import { METRIC_GROUPS, SAMPLE_LABELS, formatValue } from '../metrics'
import type { StatLine } from '../types'

defineProps<{ stats: StatLine }>()
</script>

<template>
  <section class="panel sheet">
    <h2 class="eyebrow section-head">Full stat line</h2>

    <div class="groups">
      <section v-for="group in METRIC_GROUPS" :key="group.label">
        <h3 class="eyebrow">
          {{ group.label }}
          <span class="sample">{{ SAMPLE_LABELS[group.sample] }} {{ stats[group.sample] }}</span>
        </h3>
        <dl>
          <div v-for="metric in group.metrics" :key="metric.key" class="row">
            <dt>{{ metric.label }}</dt>
            <dd class="numeric">{{ formatValue(stats[metric.key], metric.format) }}</dd>
          </div>
        </dl>
      </section>
    </div>
  </section>
</template>

<style scoped>
/* Multi-column rather than grid: the groups are different lengths, and a grid
   wraps the last one onto a new row and leaves a hole where the short columns
   ended. Columns pack them continuously instead. */
.groups {
  column-width: 200px;
  column-gap: 2rem;
}

/* Each group is a card of its own so the eye can tell where one ends and the
   next begins, which a run of identical rows could not do. */
.groups > section {
  break-inside: avoid;
  margin-bottom: 1.1rem;
  padding: 0.75rem 0.9rem 0.5rem;
  background: var(--tint);
  border-radius: var(--radius);
}

h3 {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.45rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--rule);
  color: var(--brown);
  white-space: nowrap;
}

/* Naming the denominator here is what tells a reader why Bat Speed sits apart
   from Avg EV: one is measured over swings, the other over batted balls. */
.sample {
  font-weight: 400;
  letter-spacing: 0.04em;
  color: var(--muted);
}

dl {
  margin: 0;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.3rem 0;
  font-size: 0.92rem;
}

dt {
  color: var(--muted);
}

dd {
  margin: 0;
  font-weight: 600;
}
</style>
