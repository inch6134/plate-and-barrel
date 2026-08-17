<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { fetchSprayChart } from '../api'
import { useResource } from '../composables/useResource'
import { TRAJECTORY_LABELS } from '../trajectories'
import FilterPills from './FilterPills.vue'
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

const trajectoryOptions = computed(() => [
  { code: '', label: 'All trajectories' },
  ...(data.value?.trajectories ?? []).map((option) => ({
    code: option.code,
    label: TRAJECTORY_LABELS[option.code],
    count: option.count,
  })),
])
</script>

<template>
  <div v-if="error" class="panel pad">{{ error }}</div>
  <div v-else-if="data" class="spray">
    <FilterPills v-model="trajectory" :options="trajectoryOptions" />
    <FilterPills v-model="outcome" :options="OUTCOMES" />

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

section h3 {
  margin-bottom: 0.7rem;
}
</style>
