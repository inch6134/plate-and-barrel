<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { fetchSwingProfile } from '../api'
import { useResource } from '../composables/useResource'
import { PITCH_TYPE_LABELS } from '../pitches'
import DecisionBars from './DecisionBars.vue'
import FilterPills from './FilterPills.vue'
import SwingScatter from './SwingScatter.vue'

const props = defineProps<{ batterId: number }>()

const pitchType = ref('')

watch(
  () => props.batterId,
  () => (pitchType.value = ''),
)

const { data, error } = useResource(() => fetchSwingProfile(props.batterId, pitchType.value))

const pitchOptions = computed(() => [
  { code: '', label: 'All pitches' },
  ...(data.value?.pitch_types ?? []).map((option) => ({
    code: option.code,
    label: PITCH_TYPE_LABELS[option.code],
    count: option.count,
  })),
])
</script>

<template>
  <div v-if="error" class="panel pad">{{ error }}</div>
  <div v-else-if="data" class="profile">
    <FilterPills v-model="pitchType" :options="pitchOptions" />

    <section class="panel pad decisions">
      <h3 class="eyebrow">Swing decisions vs team</h3>
      <DecisionBars :player="data.player" :team="data.team" />
    </section>

    <section class="panel pad chart">
      <h3 class="eyebrow">Bat speed and contact quality</h3>
      <SwingScatter :swings="data.swings" :player-bat-speed="data.player.avg_bat_speed"
        :team-bat-speed="data.team.avg_bat_speed" />
    </section>
  </div>
</template>

<style scoped>
.profile {
  display: grid;
  gap: 0.9rem;
}

.pad {
  padding: 1.1rem 1.25rem;
}

.decisions h3,
.chart h3 {
  margin-bottom: 0.8rem;
}
</style>
