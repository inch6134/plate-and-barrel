<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { headshotUrl } from '../api'
import { formatValue } from '../metrics'
import type { Player, StatLine } from '../types'

const props = defineProps<{ player: Player; stats: StatLine }>()

const SIDES: Record<string, string> = { L: 'Bats left', R: 'Bats right', S: 'Switch hitter' }

const headshotFailed = ref(false)

watch(() => props.player.batter_bam_id, () => (headshotFailed.value = false))

const initials = computed(() => props.player.name_first[0] + props.player.name_last[0])

const slash = computed(() => [
  { label: 'AVG', value: props.stats.avg },
  { label: 'OBP', value: props.stats.obp },
  { label: 'SLG', value: props.stats.slg },
  { label: 'OPS', value: props.stats.ops },
])
</script>

<template>
  <section class="bar">
    <img v-if="!headshotFailed" class="shot" :src="headshotUrl(player.batter_bam_id)" alt=""
      @error="headshotFailed = true" />
    <div v-else class="shot fallback numeric" aria-hidden="true">{{ initials }}</div>

    <div class="identity">
      <p class="eyebrow">{{ player.position }} &middot; No. {{ player.number }}</p>
      <h2 class="name">{{ player.name_first }} {{ player.name_last }}</h2>
      <p class="bio">
        {{ SIDES[player.side] }}, throws {{ player.throws }} &middot;
        {{ player.height }}, {{ player.weight }} lbs &middot; Age {{ player.age }}
      </p>
    </div>

    <dl class="slash">
      <div v-for="cell in slash" :key="cell.label" class="cell">
        <dd class="value numeric">{{ formatValue(cell.value, 'slash') }}</dd>
        <dt class="eyebrow">{{ cell.label }}</dt>
      </div>
    </dl>
  </section>
</template>

<style scoped>
.bar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1.5rem;
  align-items: center;
  padding: 1.5rem 0 1.75rem;
  border-bottom: 1px solid var(--rule);
}

.shot {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: var(--tint);
  border: 1px solid var(--line);
  object-fit: cover;
}

.fallback {
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--muted);
}

.identity .eyebrow {
  margin: 0;
}

.name {
  margin: 0.2rem 0 0.3rem;
  font-size: 2rem;
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.bio {
  margin: 0;
  font-size: 0.88rem;
  color: var(--muted);
}

.slash {
  display: flex;
  gap: 1.75rem;
  margin: 0;
  padding-top: 0.7rem;
  border-top: 3px solid var(--gold);
}

.cell {
  text-align: right;
}

.value {
  margin: 0;
  font-size: 1.9rem;
  font-weight: 600;
  line-height: 1.05;
  letter-spacing: -0.035em;
}

.cell .eyebrow {
  display: block;
  margin-top: 0.15rem;
}

@media (max-width: 860px) {
  .bar {
    grid-template-columns: auto 1fr;
    row-gap: 1.1rem;
  }

  .slash {
    grid-column: 1 / -1;
    justify-content: space-between;
    gap: 1rem;
  }

  .name {
    font-size: 1.6rem;
  }

  .value {
    font-size: 1.55rem;
  }
}

@media (max-width: 520px) {
  .shot {
    width: 56px;
    height: 56px;
  }

  .name {
    font-size: 1.35rem;
  }

  .bio {
    font-size: 0.82rem;
  }

  .value {
    font-size: 1.3rem;
  }
}
</style>
