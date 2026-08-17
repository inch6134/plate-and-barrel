<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { fetchSwingProfile } from '../api'
import { useResource } from '../composables/useResource'
import { FAMILIES, PITCH_COLORS, PITCH_TYPE_LABELS } from '../pitches'
import BatTracking from './BatTracking.vue'
import DecisionBars from './DecisionBars.vue'
import FilterPills from './FilterPills.vue'
import ZonePlot from './ZonePlot.vue'

const props = defineProps<{ batterId: number }>()

/* One control, two request shapes: a family code filters by family, anything else
   by type, so the pills stay a single row of mutually exclusive choices. */
const chosen = ref('')

const isFamily = (code: string) => FAMILIES.some((family) => family.code === code)

watch(
  () => props.batterId,
  () => (chosen.value = ''),
)

const { data, error } = useResource(() =>
  fetchSwingProfile(
    props.batterId,
    isFamily(chosen.value) ? '' : chosen.value,
    isFamily(chosen.value) ? chosen.value : '',
  ),
)

const counts = computed(
  () => new Map((data.value?.pitch_types ?? []).map((option) => [option.code, option.count])),
)

const familyOptions = computed(() =>
  FAMILIES.map((family) => ({
    code: family.code,
    label: family.label,
    count: family.types.reduce((total, code) => total + (counts.value.get(code) ?? 0), 0),
  })).filter((family) => family.count > 0),
)

const pitchOptions = computed(() => [
  { code: '', label: 'All pitches' },
  ...familyOptions.value,
  ...(data.value?.pitch_types ?? []).map((option) => ({
    code: option.code,
    label: PITCH_TYPE_LABELS[option.code],
    count: option.count,
  })),
])

const legend = computed(() =>
  (data.value?.pitch_types ?? []).map((option) => ({
    code: option.code,
    label: PITCH_TYPE_LABELS[option.code],
    color: PITCH_COLORS[option.code],
  })),
)
</script>

<template>
  <div v-if="error" class="panel">{{ error }}</div>
  <div v-else-if="data" class="profile">
    <FilterPills v-model="chosen" :options="pitchOptions" />

    <section class="panel">
      <h3 class="eyebrow section-head">Pitch locations</h3>
      <ZonePlot :pitches="data.pitches" :zone="data.zone" />

      <ul class="types">
        <li v-for="entry in legend" :key="entry.code">
          <span class="chip" :style="{ background: entry.color }" />{{ entry.label }}
        </li>
      </ul>
    </section>

    <div class="pair">
      <section class="panel">
        <h3 class="eyebrow section-head">Swing decisions vs team</h3>
        <DecisionBars :player="data.player" :team="data.team" :spread="data.spread" />
      </section>

      <BatTracking :contexts="data.contexts" />
    </div>
  </div>
</template>

<style scoped>
.profile {
  display: grid;
  gap: 1.1rem;
}

/* Type is never carried by colour alone: the legend names all eight, the pills
   above isolate one at a time, and the readout spells out the pitch. */
.types {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 1.1rem;
  margin: 1.1rem 0 0;
  padding: 0.9rem 0 0;
  border-top: 1px solid var(--line);
  list-style: none;
  font-size: 0.84rem;
  color: var(--muted);
}

.types li {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.chip {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.pair {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1.1rem;
  align-items: start;
}

@media (max-width: 900px) {
  .pair {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
