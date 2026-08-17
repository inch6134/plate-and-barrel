<script setup lang="ts">
import { computed } from 'vue'
import { fetchPlayer, headshotUrl } from '../api'
import { useResource } from '../composables/useResource'
import { METRIC_GROUPS, formatValue } from '../metrics'

const props = defineProps<{ batterId: number }>()

const { data, error } = useResource(() => fetchPlayer(props.batterId))

const slash = computed(() => {
  const stats = data.value?.stats
  return stats ? [stats.avg, stats.obp, stats.slg, stats.ops].map((value) => formatValue(value, 'slash')).join(' / ') : ''
})

const SIDES: Record<string, string> = { L: 'Bats left', R: 'Bats right', S: 'Switch hitter' }
</script>

<template>
  <aside class="panel player">
    <p v-if="error" class="notice">{{ error }}</p>
    <template v-else-if="data">
      <img class="headshot" :src="headshotUrl(data.player.batter_bam_id)" alt="" />
      <p class="eyebrow">{{ data.player.position }} &middot; No. {{ data.player.number }}</p>
      <h2 class="name">{{ data.player.name_first }} {{ data.player.name_last }}</h2>
      <p class="bio">
        {{ SIDES[data.player.side] }} &middot; {{ data.player.height }},
        {{ data.player.weight }} lbs &middot; Age {{ data.player.age }}
      </p>

      <p class="slash numeric">{{ slash }}</p>
      <p class="eyebrow">AVG / OBP / SLG / OPS</p>

      <section v-for="group in METRIC_GROUPS" :key="group.label" class="group">
        <h3 class="eyebrow">{{ group.label }}</h3>
        <dl>
          <div v-for="metric in group.metrics" :key="metric.key" class="row">
            <dt>{{ metric.label }}</dt>
            <dd class="numeric">{{ formatValue(data.stats[metric.key], metric.format) }}</dd>
          </div>
        </dl>
      </section>
    </template>
  </aside>
</template>

<style scoped>
.player {
  padding: 1.25rem;
}

.headshot {
  display: block;
  width: 92px;
  height: 92px;
  border-radius: 50%;
  background: var(--tint);
  object-fit: cover;
}

.name {
  font-size: 1.35rem;
  line-height: 1.15;
  margin: 0.15rem 0 0.35rem;
}

.eyebrow {
  margin: 0.7rem 0 0.2rem;
}

.bio {
  margin: 0;
  font-size: 0.82rem;
  color: var(--muted);
}

.slash {
  margin: 1.1rem 0 0;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  border-top: 3px solid var(--gold);
  padding-top: 0.6rem;
}

.group {
  margin-top: 1.1rem;
}

dl {
  margin: 0.35rem 0 0;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.28rem 0;
  border-bottom: 1px solid var(--line);
  font-size: 0.86rem;
}

dt {
  color: var(--muted);
}

dd {
  margin: 0;
  font-weight: 600;
}

.notice {
  margin: 0;
  color: var(--notice, var(--muted));
}
</style>
