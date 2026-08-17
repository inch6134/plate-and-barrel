<script setup lang="ts">
import { axisBottom, axisLeft, scaleLinear, select } from 'd3'
import { onMounted, shallowRef, useTemplateRef, watchEffect } from 'vue'
import { PITCH_TYPE_LABELS } from '../pitches'
import type { Swing } from '../types'

const props = defineProps<{
  swings: Swing[]
  playerBatSpeed: number | null
  teamBatSpeed: number | null
}>()

const WIDTH = 660
const HEIGHT = 440
const MARGIN = { top: 18, right: 18, bottom: 64, left: 52 }
const HARD_HIT = 95
const BAT_SPEED_DOMAIN = [20, 82]
const EXIT_VELO_DOMAIN = [20, 120]

const canvas = useTemplateRef<SVGSVGElement>('canvas')
const hovered = shallowRef<Swing>()

const x = scaleLinear()
  .domain(BAT_SPEED_DOMAIN)
  .range([MARGIN.left, WIDTH - MARGIN.right])
  .clamp(true)

const y = scaleLinear()
  .domain(EXIT_VELO_DOMAIN)
  .range([HEIGHT - MARGIN.bottom, MARGIN.top])
  .clamp(true)

const whiffRow = HEIGHT - MARGIN.bottom + 22

const draw = (element: SVGSVGElement) => {
  const root = select(element)
  root.selectAll('*').remove()

  root
    .append('g')
    .attr('transform', `translate(0,${HEIGHT - MARGIN.bottom})`)
    .call(axisBottom(x).ticks(7).tickSizeOuter(0))
  root
    .append('g')
    .attr('transform', `translate(${MARGIN.left},0)`)
    .call(axisLeft(y).ticks(6).tickSizeOuter(0))

  root
    .append('text')
    .attr('class', 'axis-title')
    .attr('x', WIDTH - MARGIN.right)
    .attr('y', HEIGHT - 6)
    .attr('text-anchor', 'end')
    .text('Bat speed (mph)')
  root
    .append('text')
    .attr('class', 'axis-title')
    .attr('transform', 'rotate(-90)')
    .attr('x', -MARGIN.top)
    .attr('y', 14)
    .attr('text-anchor', 'end')
    .text('Exit velocity (mph)')

  root
    .append('line')
    .attr('class', 'threshold')
    .attr('x1', MARGIN.left)
    .attr('x2', WIDTH - MARGIN.right)
    .attr('y1', y(HARD_HIT))
    .attr('y2', y(HARD_HIT))
  root
    .append('text')
    .attr('class', 'threshold-label')
    .attr('x', WIDTH - MARGIN.right)
    .attr('y', y(HARD_HIT) - 5)
    .attr('text-anchor', 'end')
    .text('Hard-hit 95')

  const means: [number | null, string][] = [
    [props.teamBatSpeed, 'team'],
    [props.playerBatSpeed, 'player'],
  ]
  means
    .filter(([value]) => value !== null)
    .forEach(([value, role]) => {
      root
        .append('line')
        .attr('class', `mean ${role}`)
        .attr('x1', x(value as number))
        .attr('x2', x(value as number))
        .attr('y1', MARGIN.top)
        .attr('y2', HEIGHT - MARGIN.bottom)
    })

  root
    .append('g')
    .selectAll<SVGLineElement, Swing>('line')
    .data(props.swings.filter((swing) => swing.result === 'whiff'))
    .join('line')
    .attr('class', 'whiff')
    .attr('x1', (swing) => x(swing.bat_speed))
    .attr('x2', (swing) => x(swing.bat_speed))
    .attr('y1', whiffRow - 5)
    .attr('y2', whiffRow + 5)

  root
    .append('text')
    .attr('class', 'axis-title')
    .attr('x', MARGIN.left)
    .attr('y', whiffRow + 3)
    .attr('text-anchor', 'end')
    .attr('dx', -6)
    .text('Whiffs')

  root
    .append('g')
    .selectAll<SVGCircleElement, Swing>('circle')
    .data(props.swings.filter((swing) => swing.exit_velo !== null))
    .join('circle')
    .attr('class', (swing) => (swing.barrel ? 'barrel' : swing.hard_hit ? 'hard' : 'contact'))
    .attr('cx', (swing) => x(swing.bat_speed))
    .attr('cy', (swing) => y(swing.exit_velo as number))
    .attr('r', 4)
    .on('pointerenter', (_event, swing) => (hovered.value = swing))
    .on('pointerleave', () => (hovered.value = undefined))
}

onMounted(() => {
  const element = canvas.value as SVGSVGElement
  watchEffect(() => draw(element))
})
</script>

<template>
  <figure>
    <svg ref="canvas" :viewBox="`0 0 ${WIDTH} ${HEIGHT}`" role="img" aria-label="Bat speed against exit velocity" />
    <figcaption>
      <span class="key barrel">Barrel</span>
      <span class="key hard">Hard-hit</span>
      <span class="key contact">In play</span>
      <span class="key player">Player avg bat speed</span>
      <span class="key team">Team avg</span>
    </figcaption>
    <p v-if="hovered" class="readout numeric">
      {{ PITCH_TYPE_LABELS[hovered.pitch_type] }} &middot;
      {{ hovered.bat_speed.toFixed(1) }} mph bat speed &middot;
      {{ hovered.exit_velo?.toFixed(1) }} mph off the bat &middot;
      {{ hovered.launch_angle?.toFixed(0) }}&deg; &middot;
      {{ hovered.distance?.toFixed(0) }} ft &middot;
      {{ hovered.event_type?.replace(/_/g, ' ') }}
    </p>
    <p v-else class="readout muted">Point at a batted ball for its detail.</p>
  </figure>
</template>

<style scoped>
figure {
  margin: 0;
}

svg {
  width: 100%;
  height: auto;
}

svg :deep(.domain),
svg :deep(.tick line) {
  stroke: var(--rule);
}

svg :deep(.tick text) {
  fill: var(--muted);
  font-size: 12px;
}

svg :deep(.axis-title),
svg :deep(.threshold-label) {
  fill: var(--muted);
  font-size: 12.5px;
}

svg :deep(.threshold) {
  stroke: var(--line);
  stroke-dasharray: 4 4;
}

svg :deep(.mean) {
  stroke-width: 2;
}

svg :deep(.mean.player) {
  stroke: var(--gold);
}

svg :deep(.mean.team) {
  stroke: var(--muted);
  stroke-dasharray: 3 5;
  stroke-width: 1;
}

svg :deep(.whiff) {
  stroke: var(--muted);
  opacity: 0.45;
}

svg :deep(circle) {
  cursor: crosshair;
}

svg :deep(.contact) {
  fill: none;
  stroke: var(--muted);
  opacity: 0.7;
}

svg :deep(.hard) {
  fill: var(--brown);
  opacity: 0.75;
}

svg :deep(.barrel) {
  fill: var(--gold);
  stroke: var(--brown);
}

figcaption {
  display: flex;
  flex-wrap: wrap;
  gap: 1.1rem;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--muted);
}

.key::before {
  content: '';
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 0.3rem;
  border-radius: 50%;
  vertical-align: baseline;
}

.key.barrel::before {
  background: var(--gold);
  border: 1px solid var(--brown);
}

.key.hard::before {
  background: var(--brown);
}

.key.contact::before {
  border: 1px solid var(--muted);
}

.key.player::before,
.key.team::before {
  width: 12px;
  height: 2px;
  border-radius: 0;
  margin-bottom: 3px;
}

.key.player::before {
  background: var(--gold);
}

.key.team::before {
  background: var(--muted);
}

.readout {
  margin: 0.7rem 0 0;
  font-size: 0.85rem;
  min-height: 1.3em;
}

.readout.muted {
  color: var(--muted);
}
</style>
