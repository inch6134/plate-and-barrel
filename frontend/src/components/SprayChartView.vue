<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { fetchSprayChart } from '../api'
import { useResource } from '../composables/useResource'
import { BATTED_BALL_DIRECTION, formatValue, valueUnit } from '../metrics'
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
  <div v-if="error" class="panel">{{ error }}</div>
  <div v-else-if="data" class="spray">
    <FilterPills v-model="trajectory" :options="trajectoryOptions" />
    <FilterPills v-model="outcome" :options="OUTCOMES" />

    <section class="panel">
      <h3 class="eyebrow section-head">{{ data.batted_balls.length }} batted balls</h3>
      <div class="plot">
        <SprayField :batted-balls="data.batted_balls" />
      </div>

      <dl class="direction">
        <div v-for="metric in BATTED_BALL_DIRECTION.metrics" :key="metric.key" class="cell">
          <dt class="eyebrow">{{ metric.label.replace('%', '') }}</dt>
          <dd class="reading numeric">
            {{ formatValue(data.player[metric.key], metric.format) }}{{ valueUnit(metric) }}
          </dd>
          <dd class="against numeric">
            vs. team {{ formatValue(data.team[metric.key], metric.format) }}{{ valueUnit(metric) }}
          </dd>
        </div>
      </dl>
    </section>
  </div>
</template>

<style scoped>
.spray {
  display: grid;
  gap: 0.7rem;
}

/* The chart shows where the ball went; these three name it and give it the team
   baseline the rest of the page compares against. */
.direction {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  max-width: 840px;
  margin: 1.4rem auto 0;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
  text-align: center;
}

.direction dt {
  margin-bottom: 0.25rem;
}

.direction dd {
  margin: 0;
}

.reading {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.against {
  font-size: 0.82rem;
  color: var(--muted);
}
</style>
