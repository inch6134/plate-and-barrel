<script setup lang="ts">
import { computed, ref } from 'vue'
import { fetchLeaderboard } from '../api'
import { useResource } from '../composables/useResource'
import {
  METRIC_GROUPS,
  OPS,
  SAMPLE_LABELS,
  formatValue,
  sampleOf,
  type MetricSpec,
} from '../metrics'

defineProps<{ batterId: number }>()
const emit = defineEmits<{ select: [batterId: number] }>()

const metric = ref<MetricSpec>(OPS)
const order = computed(() => (metric.value.higherIsBetter ? 'desc' : 'asc'))

const { data, error } = useResource(() => fetchLeaderboard(metric.value.key, order.value))
</script>

<template>
  <aside class="panel board">
    <h2 class="eyebrow section-head">Team leaders</h2>

    <select v-model="metric" class="field" aria-label="Rank by">
      <optgroup v-for="group in METRIC_GROUPS" :key="group.label" :label="group.label">
        <option v-for="option in group.metrics" :key="option.key" :value="option">
          {{ option.label }}
        </option>
      </optgroup>
    </select>

    <p v-if="error" class="notice">{{ error }}</p>
    <template v-else-if="data">
      <p class="colhead eyebrow">
        <span class="who">Batter</span>
        <span>{{ SAMPLE_LABELS[sampleOf(metric)] }}</span>
        <span class="value">{{ metric.label }}</span>
      </p>
      <ol>
      <li v-for="(entry, index) in data" :key="entry.batter_bam_id">
        <button type="button" :class="{ current: entry.batter_bam_id === batterId }"
          @click="emit('select', entry.batter_bam_id)">
          <span class="rank numeric">{{ index + 1 }}</span>
          <span class="who">{{ entry.name_first[0] }}. {{ entry.name_last }}</span>
          <span class="sample numeric">{{ entry.sample }}</span>
          <span class="value numeric">{{ formatValue(entry.value, metric.format) }}</span>
        </button>
      </li>
      </ol>
    </template>
    <p v-if="data && data.length < 15" class="footnote">
      {{ 15 - data.length }} batters fall below the sample floor for {{ metric.label }} and are not ranked.
    </p>
  </aside>
</template>

<style scoped>
.board {
  align-self: start;
}

.field {
  width: 100%;
  margin-bottom: 0.7rem;
}

.colhead {
  display: grid;
  grid-template-columns: 1.5rem minmax(0, 1fr) auto 3.4rem;
  gap: 0.6rem;
  margin: 0 0 0.3rem;
  padding: 0 0.5rem 0.4rem;
  border-bottom: 1px solid var(--line);
}

.colhead .who {
  grid-column: 2;
}

ol {
  margin: 0;
  padding: 0;
  list-style: none;
}

button {
  display: grid;
  grid-template-columns: 1.5rem minmax(0, 1fr) auto 3.4rem;
  gap: 0.6rem;
  align-items: baseline;
  width: 100%;
  padding: 0.42rem 0.5rem;
  background: none;
  border: 0;
  border-radius: var(--radius);
  text-align: left;
  cursor: pointer;
}

button:hover {
  background: var(--tint);
}

button.current {
  background: var(--tint);
  box-shadow: inset 3px 0 0 var(--gold);
}

.rank {
  font-size: 0.75rem;
  color: var(--muted);
}

.who {
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

button.current .who {
  font-weight: 600;
}

.sample {
  font-size: 0.75rem;
  color: var(--muted);
}

.value {
  font-size: 0.9rem;
  font-weight: 600;
  text-align: right;
}

.colhead .value {
  font-size: 0.7rem;
  font-weight: 700;
}

.footnote,
.notice {
  margin: 0.9rem 0 0;
  font-size: 0.78rem;
  line-height: 1.4;
  color: var(--muted);
}
</style>
