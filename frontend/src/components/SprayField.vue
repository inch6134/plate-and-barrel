<script setup lang="ts">
import { line, scaleSqrt, select } from 'd3'
import { onMounted, shallowRef, useTemplateRef, watchEffect } from 'vue'
import { PITCH_TYPE_LABELS } from '../pitches'
import { TRAJECTORY_LABELS } from '../trajectories'
import type { BattedBall } from '../types'

const props = defineProps<{ battedBalls: BattedBall[] }>()

const WIDTH = 720
const HEIGHT = 500
const HOME = { x: 360, y: 420 }
const SCALE = 0.95
const FOUL_LINE_FT = 330
const CENTER_FIELD_FT = 400
const BASE_PATH_FT = 90
const SECOND_BASE_FT = 127.28
const MOUND_FT = 60.5
const INFIELD_ARC_FT = 95

const canvas = useTemplateRef<SVGSVGElement>('canvas')
const selected = shallowRef<BattedBall>()

const radians = (degrees: number) => (degrees * Math.PI) / 180

const project = (bearing: number, distance: number): [number, number] => [
  HOME.x + distance * Math.sin(radians(bearing)) * SCALE,
  HOME.y - distance * Math.cos(radians(bearing)) * SCALE,
]

const wallRadius = (bearing: number) =>
  CENTER_FIELD_FT - (CENTER_FIELD_FT - FOUL_LINE_FT) * (Math.abs(bearing) / 45) ** 2

const bearings = Array.from({ length: 91 }, (_, step) => step - 45)

const fairTerritory = [
  [HOME.x, HOME.y] as [number, number],
  ...bearings.map((bearing) => project(bearing, wallRadius(bearing))),
]

const infieldArc = Array.from({ length: 361 }, (_, step) => radians(step - 180))
  .map((angle): [number, number] => [
    HOME.x + INFIELD_ARC_FT * Math.sin(angle) * SCALE,
    HOME.y - (MOUND_FT + INFIELD_ARC_FT * Math.cos(angle)) * SCALE,
  ])
  .filter(([px, py]) => Math.abs(Math.atan2(px - HOME.x, HOME.y - py)) <= radians(45))

const diamond = [
  project(0, 0),
  project(45, BASE_PATH_FT),
  project(0, SECOND_BASE_FT),
  project(-45, BASE_PATH_FT),
]

const size = scaleSqrt().domain([40, 120]).range([3, 7.5]).clamp(true)
const path = line()

const draw = (element: SVGSVGElement) => {
  const root = select(element)
  root.selectAll('*').remove()

  root.append('path').attr('class', 'grass').attr('d', `${path(fairTerritory)}Z`)
  root.append('path').attr('class', 'arc').attr('d', path(infieldArc))
  root.append('path').attr('class', 'diamond').attr('d', `${path(diamond)}Z`)

  root
    .append('g')
    .selectAll('line')
    .data([-45, 45])
    .join('line')
    .attr('class', 'foul-line')
    .attr('x1', HOME.x)
    .attr('y1', HOME.y)
    .attr('x2', (bearing) => project(bearing, FOUL_LINE_FT)[0])
    .attr('y2', (bearing) => project(bearing, FOUL_LINE_FT)[1])

  root
    .append('g')
    .selectAll('rect')
    .data([project(45, BASE_PATH_FT), project(0, SECOND_BASE_FT), project(-45, BASE_PATH_FT)])
    .join('rect')
    .attr('class', 'base')
    .attr('x', ([px]) => px - 3)
    .attr('y', ([, py]) => py - 3)
    .attr('width', 6)
    .attr('height', 6)

  root
    .append('circle')
    .attr('class', 'mound')
    .attr('cx', project(0, MOUND_FT)[0])
    .attr('cy', project(0, MOUND_FT)[1])
    .attr('r', 9 * SCALE)

  root
    .append('g')
    .selectAll<SVGCircleElement, BattedBall>('circle')
    .data(props.battedBalls)
    .join('circle')
    .attr('class', (ball) => (ball.is_hit ? 'ball hit' : 'ball out'))
    .attr('cx', (ball) => project(ball.bearing, ball.distance)[0])
    .attr('cy', (ball) => project(ball.bearing, ball.distance)[1])
    .attr('r', (ball) => size(ball.exit_velo))
    .on('click', (_event, ball) => (selected.value = ball))
}

onMounted(() => {
  const element = canvas.value as SVGSVGElement
  watchEffect(() => draw(element))
})
</script>

<template>
  <figure>
    <svg ref="canvas" :viewBox="`0 0 ${WIDTH} ${HEIGHT}`" role="img" aria-label="Batted ball locations" />
    <figcaption>
      <span class="key hit">Hit</span>
      <span class="key out">Out</span>
      <span>Point size is exit velocity</span>
    </figcaption>
    <p v-if="selected" class="readout numeric">
      {{ selected.event_type.replace(/_/g, ' ') }} &middot;
      {{ TRAJECTORY_LABELS[selected.trajectory] }} &middot;
      {{ selected.exit_velo.toFixed(1) }} mph &middot;
      {{ selected.launch_angle.toFixed(0) }}&deg; &middot;
      {{ selected.distance.toFixed(0) }} ft &middot;
      {{ PITCH_TYPE_LABELS[selected.pitch_type] }} &middot;
      {{ selected.game_date }}
    </p>
    <p v-else class="readout muted">Select a batted ball for its detail.</p>
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

svg :deep(.grass) {
  fill: var(--tint);
  stroke: var(--line);
}

svg :deep(.arc),
svg :deep(.diamond) {
  fill: none;
  stroke: var(--line);
}

svg :deep(.foul-line) {
  stroke: var(--line);
}

svg :deep(.base),
svg :deep(.mound) {
  fill: none;
  stroke: var(--line);
}

svg :deep(.ball) {
  cursor: pointer;
}

svg :deep(.ball.hit) {
  fill: var(--gold);
  stroke: var(--brown);
}

svg :deep(.ball.out) {
  fill: none;
  stroke: var(--muted);
  opacity: 0.75;
}

figcaption {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem;
  font-size: 0.72rem;
  color: var(--muted);
}

.key::before {
  content: '';
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 0.3rem;
  border-radius: 50%;
}

.key.hit::before {
  background: var(--gold);
  border: 1px solid var(--brown);
}

.key.out::before {
  border: 1px solid var(--muted);
}

.readout {
  margin: 0.6rem 0 0;
  font-size: 0.78rem;
  min-height: 1.2em;
}

.readout.muted {
  color: var(--muted);
}
</style>
