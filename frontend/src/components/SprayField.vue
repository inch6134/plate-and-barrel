<script setup lang="ts">
import { line, scaleSqrt, select } from 'd3'
import { onMounted, shallowRef, useTemplateRef, watchEffect } from 'vue'
import { PITCH_TYPE_LABELS } from '../pitches'
import { TRAJECTORY_LABELS } from '../trajectories'
import type { BattedBall } from '../types'

const props = defineProps<{ battedBalls: BattedBall[] }>()

const HOME = { x: 360, y: 420 }

/* The drawing is laid out around HOME in a 720x500 space, but the fair wedge and
   the batted balls together only occupy the middle of it. Bearing runs past the
   foul lines in this data (-118.7 to 162.1 degrees), so balls caught in foul
   territory sit outside the wedge and two land behind home plate. The frame is
   cropped to hold every point with room for its radius, not to the field. */
const FRAME = { x: 100, y: 0, width: 550, height: 458 }
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

const size = scaleSqrt().domain([40, 120]).range([3.5, 8]).clamp(true)
const path = line()

/* Wall distance at the two poles, the two gaps and dead centre, so a reader can
   judge how deep a ball travelled without counting pixels. */
const markers = [-45, -22.5, 0, 22.5, 45].map((bearing) => {
  const radius = wallRadius(bearing)
  const [px, py] = project(bearing, radius + 20)
  return { bearing, feet: Math.round(radius), x: px, y: py }
})

/* Colour is how well it was struck, shape is what it produced. Keeping them on
   separate channels matters because they disagree often: hard-hit balls go for
   hits 48.7% of the time against 23.7% for everything else. */
const quality = (ball: BattedBall) =>
  ball.barrel ? 'barrel' : ball.hard_hit ? 'hard' : 'plain'

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
    .append('g')
    .selectAll('text')
    .data(markers)
    .join('text')
    .attr('class', 'marker')
    .attr('x', (marker) => marker.x)
    .attr('y', (marker) => marker.y)
    .attr('text-anchor', 'middle')
    .text((marker) => `${marker.feet} ft`)

  root
    .append('circle')
    .attr('class', 'mound')
    .attr('cx', project(0, MOUND_FT)[0])
    .attr('cy', project(0, MOUND_FT)[1])
    .attr('r', 9 * SCALE)

  root
    .append('g')
    .selectAll<SVGGElement, BattedBall>('g')
    .data(props.battedBalls)
    .join('g')
    .attr('class', (ball) =>
      ['ball', quality(ball), ball.is_hit ? 'hit' : 'out'].join(' '),
    )
    .attr('transform', (ball) => `translate(${project(ball.bearing, ball.distance)})`)
    .each(function (ball) {
      const radius = size(ball.exit_velo)
      const mark = select(this)
      if (ball.is_hit) {
        mark.append('circle').attr('class', 'mark').attr('r', radius)
      } else {
        /* An X spans its diagonal, so its arms stop short of the radius to keep
           it the same visual weight as a disc of the same exit velocity. */
        const arm = radius * 0.78
        mark
          .append('path')
          .attr('class', 'mark')
          .attr('d', `M${-arm},${-arm}L${arm},${arm}M${-arm},${arm}L${arm},${-arm}`)
        mark.append('circle').attr('class', 'target').attr('r', radius)
      }
    })
    .on('click', (_event, ball) => (selected.value = ball))
}

onMounted(() => {
  const element = canvas.value as SVGSVGElement
  watchEffect(() => draw(element))
})
</script>

<template>
  <figure>
    <svg ref="canvas" :viewBox="`${FRAME.x} ${FRAME.y} ${FRAME.width} ${FRAME.height}`" role="img"
      aria-label="Batted ball locations" />
    <figcaption>
      <span class="shape out">Out</span>
      <span class="swatch barrel">Barrel</span>
      <span class="swatch hard">Hard-hit</span>
      <span class="swatch plain">Hit</span>
      <span>Size is exit velocity</span>
    </figcaption>

    <div v-if="selected" class="readout">
      <span class="lede">{{ selected.event_type.replace(/_/g, ' ') }}</span>
      <span class="fact">
        <span class="term">Exit velo</span>
        <span class="fact-value">{{ selected.exit_velo.toFixed(1) }} mph</span>
      </span>
      <span class="fact">
        <span class="term">Launch</span>
        <span class="fact-value">{{ selected.launch_angle.toFixed(0) }}&deg;</span>
      </span>
      <span class="fact">
        <span class="term">Distance</span>
        <span class="fact-value">{{ selected.distance.toFixed(0) }} ft</span>
      </span>
      <span class="fact">
        <span class="term">{{ TRAJECTORY_LABELS[selected.trajectory] }}</span>
        <span class="fact-value">off a {{ PITCH_TYPE_LABELS[selected.pitch_type] }}</span>
      </span>
      <span class="fact">
        <span class="term">Date</span>
        <span class="fact-value">{{ selected.game_date }}</span>
      </span>
    </div>
    <p v-else class="readout empty">Select a batted ball for its detail.</p>
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

svg :deep(.marker) {
  fill: var(--muted);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

svg :deep(.base),
svg :deep(.mound) {
  fill: none;
  stroke: var(--line);
}

svg :deep(.ball) {
  cursor: pointer;
}

/* Shape is the outcome, colour is how well it was struck. Hits are discs, outs
   are crosses, and both scale with exit velocity. */
svg :deep(.ball circle.mark) {
  stroke: var(--brown);
  stroke-width: 1;
}

svg :deep(.ball path.mark) {
  fill: none;
  stroke-width: 2.4;
  stroke-linecap: round;
}

/* An invisible disc over each cross, so the hover target is the whole mark
   rather than two hairlines. */
svg :deep(.ball .target) {
  fill: transparent;
  stroke: none;
}

svg :deep(.ball.plain circle.mark) {
  fill: var(--surface);
}

svg :deep(.ball.plain path.mark) {
  stroke: var(--faint);
}

svg :deep(.ball.hard circle.mark) {
  fill: var(--brown);
}

svg :deep(.ball.hard path.mark) {
  stroke: var(--brown);
}

svg :deep(.ball.barrel circle.mark) {
  fill: var(--gold);
}

svg :deep(.ball.barrel path.mark) {
  stroke: var(--gold-ink);
}

svg :deep(.ball:hover circle.mark) {
  stroke-width: 3;
}

svg :deep(.ball:hover path.mark) {
  stroke: var(--brown);
  stroke-width: 4;
}

figcaption {
  display: flex;
  flex-wrap: wrap;
  gap: 1.1rem;
  margin-top: 0.6rem;
  font-size: 0.84rem;
  color: var(--muted);
}

.swatch::before {
  content: '';
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 0.35rem;
  border: 1px solid var(--brown);
  border-radius: 50%;
}

.swatch.barrel::before {
  background: var(--gold);
}

.swatch.hard::before {
  background: var(--brown);
}

.swatch.plain::before {
  background: var(--surface);
}

.shape::before {
  margin-right: 0.3rem;
  color: var(--brown);
  font-weight: 700;
}

.shape.hit::before {
  content: '●';
}

.shape.out::before {
  content: '✕';
}
</style>
