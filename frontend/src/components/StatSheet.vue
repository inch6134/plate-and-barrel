<script setup lang="ts">
import { METRIC_GROUPS, formatValue } from '../metrics'
import type { StatLine } from '../types'

defineProps<{ stats: StatLine }>()
</script>

<template>
  <section class="panel sheet">
    <h2 class="eyebrow section-head">Full stat line</h2>

    <div class="groups">
      <section v-for="group in METRIC_GROUPS" :key="group.label">
        <h3 class="eyebrow">{{ group.label }}</h3>
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

.groups > section {
  break-inside: avoid;
  margin-bottom: 1.4rem;
}

h3 {
  margin-bottom: 0.5rem;
}

dl {
  margin: 0;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.34rem 0;
  border-bottom: 1px solid var(--line);
  font-size: 0.9rem;
}

.row:last-child {
  border-bottom: 0;
}

dt {
  color: var(--muted);
}

dd {
  margin: 0;
  font-weight: 600;
}
</style>
