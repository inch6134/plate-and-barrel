<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchPlayer, fetchPlayers } from './api'
import { useResource } from './composables/useResource'
import LeaderboardPanel from './components/LeaderboardPanel.vue'
import PlayerBar from './components/PlayerBar.vue'
import StatSheet from './components/StatSheet.vue'
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

const { data: detail, pending: loadingPlayer } = useResource(() => fetchPlayer(batterId.value))
</script>

<template>
  <div class="app">
    <header class="masthead">
      <div>
        <h1>Plate<span class="amp">&amp;</span>Barrel</h1>
        <p class="eyebrow">San Diego Padres batting &middot; July 2024</p>
      </div>
      <label class="picker">
        <span class="eyebrow">Batter</span>
        <select v-model="batterId" class="field">
          <option v-for="player in players" :key="player.batter_bam_id" :value="player.batter_bam_id">
            {{ player.name_last }}, {{ player.name_first }}
          </option>
        </select>
      </label>
    </header>

    <p v-if="error" class="panel failure">
      {{ error }} Start the API with <code>uv run fastapi run app/main.py</code> and reload.
    </p>

    <template v-else-if="detail">
      <PlayerBar :player="detail.player" :stats="detail.stats" :class="{ refreshing: loadingPlayer }" />

      <main class="stage">
        <nav class="tabs">
          <button v-for="tab in TABS" :key="tab.code" type="button" :class="{ active: tab.code === activeTab }"
            :aria-pressed="tab.code === activeTab" @click="activeTab = tab.code">{{ tab.label }}</button>
        </nav>

        <InsightsPanel :batter-id="batterId" :view="activeTab" />

        <SwingProfileView v-if="activeTab === 'swing'" :batter-id="batterId" />
        <SprayChartView v-else-if="activeTab === 'spray'" :batter-id="batterId" />
        <SplitsView v-else :batter-id="batterId" />
      </main>

      <div class="shelf">
        <StatSheet :stats="detail.stats" :class="{ refreshing: loadingPlayer }" />
        <LeaderboardPanel :batter-id="batterId" @select="batterId = $event" />
      </div>
    </template>

    <div v-else class="panel awaiting" />
  </div>
</template>

<style scoped>
.masthead {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
  padding: 2.25rem 0 1.1rem;
  border-bottom: 1px solid var(--rule);
}

h1 {
  font-size: 1.6rem;
  letter-spacing: -0.035em;
}

/* The ampersand is the one place the retail pun is allowed to show. */
.amp {
  padding: 0 0.06em;
  font-weight: 400;
  color: var(--muted);
}

.masthead .eyebrow {
  margin: 0.3rem 0 0;
}

.picker {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.stage {
  margin-top: 2.25rem;
  display: grid;
  gap: 1.1rem;
  align-content: start;
}

/* Wraps rather than scrolls. A horizontal scroller hides tabs behind a gesture,
   and three tabs always fit in at most two rows. */
.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem;
  border-bottom: 1px solid var(--line);
}

.tabs button {
  margin-bottom: -1px;
  padding: 0.65rem 1.05rem;
  background: none;
  border: 0;
  border-bottom: 2px solid transparent;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  white-space: nowrap;
  cursor: pointer;
}

.tabs button:hover {
  color: var(--brown);
}

.tabs button.active {
  color: var(--brown);
  border-bottom-color: var(--gold);
}

.shelf {
  margin-top: 2.75rem;
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: 1.1rem;
  align-items: start;
}

.failure {
  margin-top: 2rem;
}

@media (max-width: 960px) {
  .shelf {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 520px) {
  .masthead {
    padding-top: 1.5rem;
  }

  .tabs button {
    padding: 0.6rem 0.75rem;
    letter-spacing: 0.06em;
  }
}
</style>
