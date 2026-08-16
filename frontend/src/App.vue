<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchPlayers } from './api'
import { useResource } from './composables/useResource'
import LeaderboardPanel from './components/LeaderboardPanel.vue'
import PlayerPanel from './components/PlayerPanel.vue'
import SwingProfileView from './components/SwingProfileView.vue'
import SprayChartView from './components/SprayChartView.vue'
import SplitsView from './components/SplitsView.vue'
import InsightsPanel from './components/InsightsPanel.vue'

const TABS = [
  { code: 'swing', label: 'Swing Profile' },
  { code: 'spray', label: 'Spray Chart' },
  { code: 'splits', label: 'Situational Splits' },
]

const { data: players, error } = useResource(fetchPlayers)
const batterId = ref(0)
const activeTab = ref(TABS[0].code)

watch(players, (roster) => {
  if (roster) {
    batterId.value = roster[0].batter_bam_id
  }
})
</script>

<template>
  <header>
    <div class="brand">
      <h1>Plate&amp;Barrel</h1>
      <p class="eyebrow">San Diego Padres &middot; July 2024</p>
    </div>
    <label class="picker">
      <span class="eyebrow">Batter</span>
      <select v-model="batterId">
        <option v-for="player in players" :key="player.batter_bam_id" :value="player.batter_bam_id">
          {{ player.name_first }} {{ player.name_last }}
        </option>
      </select>
    </label>
  </header>

  <p v-if="error" class="failure panel">
    {{ error }} Start the API with <code>fastapi dev app/main.py</code> and reload.
  </p>

  <main v-else-if="batterId" class="layout">
    <PlayerPanel :batter-id="batterId" />

    <section class="view">
      <nav class="tabs">
        <button v-for="tab in TABS" :key="tab.code" type="button" :class="{ active: tab.code === activeTab }"
          :aria-pressed="tab.code === activeTab" @click="activeTab = tab.code">{{ tab.label }}</button>
      </nav>
      <InsightsPanel :batter-id="batterId" :view="activeTab" />

      <SwingProfileView v-if="activeTab === 'swing'" :batter-id="batterId" />
      <SprayChartView v-else-if="activeTab === 'spray'" :batter-id="batterId" />
      <SplitsView v-else :batter-id="batterId" />
    </section>

    <LeaderboardPanel :batter-id="batterId" @select="batterId = $event" />
  </main>
</template>

<style scoped>
.view {
  display: grid;
  gap: 0.9rem;
  align-content: start;
}
</style>
