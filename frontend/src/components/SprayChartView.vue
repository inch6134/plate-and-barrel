<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchSprayChart } from '../api'
import { useResource } from '../composables/useResource'
import { TRAJECTORY_LABELS } from '../trajectories'
import SprayField from './SprayField.vue'

const props = defineProps<{ batterId: number }>()

const OUTCOMES = [
  { code: '', label: 'All outcomes' },
  { code: 'hit', label: 'Hits' },
  { code: 'out', label: 'Outs' },
]

const trajectory = ref('')
const outcome = ref('')

watch(
  () => props.batterId,
  () => {
    trajectory.value = ''
    outcome.value = ''
  },
)

const { data, error } = useResource(() =>
  fetchSprayChart(props.batterId, trajectory.value, outcome.value),
)
</script>

<template>
  <div v-if="error" class="panel pad">{{ error }}</div>
  <div v-else-if="data" class="spray">
    <nav class="filters">
      <button type="button" :class="{ on: trajectory === '' }" @click="trajectory = ''">
        All trajectories
      </button>
      <button v-for="option in data.trajectories" :key="option.code" type="button"
        :class="{ on: trajectory === option.code }" @click="trajectory = option.code">
        {{ TRAJECTORY_LABELS[option.code] }}
        <span class="count numeric">{{ option.count }}</span>
      </button>
    </nav>

    <nav class="filters">
      <button v-for="option in OUTCOMES" :key="option.label" type="button" :class="{ on: outcome === option.code }"
        @click="outcome = option.code">
        {{ option.label }}
      </button>
    </nav>

    <section class="panel pad">
      <h3 class="eyebrow">{{ data.batted_balls.length }} batted balls</h3>
      <SprayField :batted-balls="data.batted_balls" />
    </section>
  </div>
</template>

<style scoped>
.spray {
  display: grid;
  gap: 0.7rem;
}

.pad {
  padding: 1.1rem 1.25rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.filters button {
  padding: 0.3rem 0.6rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: 0.78rem;
  cursor: pointer;
}

.filters button.on {
  background: var(--brown);
  border-color: var(--brown);
  color: var(--paper);
}

.count {
  margin-left: 0.3rem;
  font-size: 0.7rem;
  opacity: 0.6;
}

section h3 {
  margin-bottom: 0.7rem;
}
</style>
