<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchSwingProfile } from '../api'
import { useResource } from '../composables/useResource'
import { PITCH_TYPE_LABELS } from '../pitches'
import DecisionBars from './DecisionBars.vue'
import SwingScatter from './SwingScatter.vue'

const props = defineProps<{ batterId: number }>()

const pitchType = ref('')

watch(
  () => props.batterId,
  () => (pitchType.value = ''),
)

const { data, error } = useResource(() => fetchSwingProfile(props.batterId, pitchType.value))
</script>

<template>
  <div v-if="error" class="panel pad">{{ error }}</div>
  <div v-else-if="data" class="profile">
    <nav class="filters">
      <button type="button" :class="{ on: pitchType === '' }" @click="pitchType = ''">
        All pitches
      </button>
      <button v-for="option in data.pitch_types" :key="option.code" type="button"
        :class="{ on: pitchType === option.code }" @click="pitchType = option.code">
        {{ PITCH_TYPE_LABELS[option.code] }}
        <span class="count numeric">{{ option.count }}</span>
      </button>
    </nav>

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

.decisions h3,
.chart h3 {
  margin-bottom: 0.8rem;
}
</style>
