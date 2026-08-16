<script setup lang="ts">
import { computed, ref } from 'vue'
import { fetchLeaderboard } from '../api'
import { useResource } from '../composables/useResource'
import { METRIC_GROUPS, formatValue, type MetricSpec } from '../metrics'

defineProps<{ batterId: number }>()
const emit = defineEmits<{ select: [batterId: number] }>()

const metric = ref<MetricSpec>(METRIC_GROUPS[0].metrics[3])
const order = computed(() => (metric.value.higherIsBetter ? 'desc' : 'asc'))

const { data, error } = useResource(() => fetchLeaderboard(metric.value.key, order.value))
</script>

<template>
  <aside class="panel board">
    <h2 class="eyebrow">Team leaders</h2>

    <select v-model="metric" aria-label="Rank by">
      <optgroup v-for="group in METRIC_GROUPS" :key="group.label" :label="group.label">
        <option v-for="option in group.metrics" :key="option.key" :value="option">
          {{ option.label }}
        </option>
      </optgroup>
    </select>

    <p v-if="error" class="notice">{{ error }}</p>
    <ol v-else-if="data">
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
    <p v-if="data && data.length < 15" class="footnote">
      {{ 15 - data.length }} batters fall below the sample floor and are not ranked.
    </p>
  </aside>
</template>

<style scoped>
.board {
  padding: 1.25rem;
  align-self: start;
}

select {
  width: 100%;
  margin: 0.5rem 0 0.9rem;
  padding: 0.4rem 0.5rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 3px;
}

ol {
  margin: 0;
  padding: 0;
  list-style: none;
}

button {
  display: grid;
  grid-template-columns: 1.4rem 1fr auto auto;
  gap: 0.5rem;
  align-items: baseline;
  width: 100%;
  padding: 0.36rem 0.4rem;
  background: none;
  border: 0;
  border-radius: 3px;
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
  font-size: 0.72rem;
  color: var(--muted);
}

.who {
  font-size: 0.86rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sample {
  font-size: 0.72rem;
  color: var(--muted);
}

.value {
  font-size: 0.86rem;
  font-weight: 600;
  min-width: 3.2rem;
  text-align: right;
}

.footnote,
.notice {
  margin: 0.9rem 0 0;
  font-size: 0.72rem;
  color: var(--muted);
}
</style>
