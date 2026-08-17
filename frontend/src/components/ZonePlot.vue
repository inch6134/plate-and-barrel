<script setup lang="ts">
import { scaleLinear } from 'd3'
import { computed, ref, shallowRef, watch } from 'vue'
import { PITCH_COLORS, PITCH_TYPE_LABELS } from '../pitches'
import type { Pitch, PitchResult, Zone } from '../types'

const props = defineProps<{ pitches: Pitch[]; zone: Zone }>()

const WIDTH = 560
const HEIGHT = 600
const MARGIN = { top: 14, right: 14, bottom: 34, left: 14 }
const X_FEET = [-2.35, 2.35]
const Z_FEET = [0, 5.1]

/* One ball width outside the zone edge. Almost every chase lives in this band,
   so it is drawn rather than left implicit. */
const SHADOW_FT = 0.24
const PLATE_HALF_FT = 0.708

const RESULTS: { code: PitchResult; label: string }[] = [
  { code: 'take', label: 'Take' },
  { code: 'whiff', label: 'Whiff' },
  { code: 'foul', label: 'Foul' },
  { code: 'in_play', label: 'In play' },
]

const hovered = shallowRef<Pitch>()
const shown = ref<PitchResult[]>(RESULTS.map((result) => result.code))

watch(
  () => props.pitches,
  () => (hovered.value = undefined),
)

const toggle = (code: PitchResult) => {
  shown.value = shown.value.includes(code)
    ? shown.value.filter((entry) => entry !== code)
    : [...shown.value, code]
}

const x = scaleLinear().domain(X_FEET).range([MARGIN.left, WIDTH - MARGIN.right])
const y = scaleLinear().domain(Z_FEET).range([HEIGHT - MARGIN.bottom, MARGIN.top])

const box = computed(() => ({
  left: x(-props.zone.half_width),
  right: x(props.zone.half_width),
  top: y(props.zone.top),
  bottom: y(props.zone.bottom),
}))

const shadow = computed(() => ({
  left: x(-props.zone.half_width - SHADOW_FT),
  right: x(props.zone.half_width + SHADOW_FT),
  top: y(props.zone.top + SHADOW_FT),
  bottom: y(props.zone.bottom - SHADOW_FT),
}))

/* Home plate seen edge on from behind, the way a broadcast centre-field camera
   frames it: a flat bar with a point, sitting under the zone. */
const plate = computed(() =>
  [
    [-PLATE_HALF_FT, 0.42],
    [PLATE_HALF_FT, 0.42],
    [PLATE_HALF_FT, 0.24],
    [0, 0.08],
    [-PLATE_HALF_FT, 0.24],
  ]
    .map(([feet, height]) => `${x(feet)},${y(height)}`)
    .join(' '),
)

/* Catcher's view: the right handed batter stands on the negative side, so the
   label alone marks which box he hit from. Switch hitters get both, with the
   pitch count each side saw. */
const stances = computed(() =>
  props.zone.boxes.map((batterBox) => ({
    ...batterBox,
    labelX: x(batterBox.side === 'R' ? -1.72 : 1.72),
    labelY: y(0.24),
  })),
)

const marks = computed(() =>
  props.pitches
    .filter((pitch) => shown.value.includes(pitch.result))
    .map((pitch) => ({
      pitch,
      cx: x(Math.max(X_FEET[0], Math.min(X_FEET[1], pitch.plate_x))),
      cy: y(Math.max(Z_FEET[0], Math.min(Z_FEET[1], pitch.plate_z))),
      color: PITCH_COLORS[pitch.pitch_type],
    })),
)

const inShadow = (pitch: Pitch) =>
  !pitch.in_zone &&
  Math.abs(pitch.plate_x) <= props.zone.half_width + SHADOW_FT &&
  pitch.plate_z <= props.zone.top + SHADOW_FT &&
  pitch.plate_z >= props.zone.bottom - SHADOW_FT

const bands = computed(() => {
  const groups = [
    { key: 'zone', label: 'In the zone', of: (pitch: Pitch) => pitch.in_zone },
    { key: 'shadow', label: 'Shadow', of: inShadow },
    {
      key: 'outside',
      label: 'Beyond',
      of: (pitch: Pitch) => !pitch.in_zone && !inShadow(pitch),
    },
  ]
  return groups.map((group) => {
    const within = props.pitches.filter(group.of)
    const swings = within.filter((pitch) => pitch.result !== 'take').length
    return {
      ...group,
      pitches: within.length,
      rate: within.length ? (100 * swings) / within.length : null,
    }
  })
})

const cross = (size: number) =>
  `M${-size},${-size}L${size},${size}M${-size},${size}L${size},${-size}`

const square = (size: number) => `M${-size},${-size}H${size}V${size}H${-size}Z`
</script>

<template>
  <figure>
    <nav class="results">
      <button v-for="result in RESULTS" :key="result.code" type="button" role="switch"
        :aria-checked="shown.includes(result.code)" :class="{ off: !shown.includes(result.code) }"
        @click="toggle(result.code)">
        <svg class="glyph" viewBox="-8 -8 16 16" aria-hidden="true">
          <path v-if="result.code === 'take'" class="take" :d="square(3.8)" />
          <path v-else-if="result.code === 'whiff'" class="whiff" :d="cross(4.4)" />
          <circle v-else-if="result.code === 'foul'" class="foul" r="4.2" />
          <circle v-else class="in-play" r="5.4" />
        </svg>
        {{ result.label }}
      </button>
    </nav>

    <svg :viewBox="`0 0 ${WIDTH} ${HEIGHT}`" role="img" aria-label="Pitch locations against the strike zone">
      <text v-for="stance in stances" :key="stance.side" class="stance-label" :x="stance.labelX" :y="stance.labelY"
        text-anchor="middle">
        {{ stance.side }}HB<tspan v-if="stances.length > 1"> · {{ stance.pitches }}</tspan>
      </text>

      <polygon class="plate" :points="plate" />

      <rect class="shadow" :x="shadow.left" :y="shadow.top" :width="shadow.right - shadow.left"
        :height="shadow.bottom - shadow.top" />
      <rect class="zone" :x="box.left" :y="box.top" :width="box.right - box.left" :height="box.bottom - box.top" />

      <g v-for="(mark, index) in marks" :key="index" :class="['mark', mark.pitch.result]"
        :transform="`translate(${mark.cx}, ${mark.cy})`" @pointerenter="hovered = mark.pitch"
        @pointerleave="hovered = undefined">
        <path v-if="mark.pitch.result === 'take'" class="take" :d="square(3.8)" :stroke="mark.color" />
        <path v-else-if="mark.pitch.result === 'whiff'" class="whiff" :d="cross(4.4)" :stroke="mark.color" />
        <circle v-else-if="mark.pitch.result === 'foul'" class="foul" r="4.2" :stroke="mark.color" />
        <circle v-else class="in-play" r="5.4" :fill="mark.color" />
        <circle class="target" r="7" />
      </g>
    </svg>

    <dl class="bands">
      <div v-for="band in bands" :key="band.key" class="band">
        <dt class="eyebrow">{{ band.label }}</dt>
        <dd class="rate numeric">{{ band.rate === null ? '—' : `${band.rate.toFixed(0)}%` }}</dd>
        <dd class="count numeric">swung at, of {{ band.pitches }}</dd>
      </div>
    </dl>

    <div v-if="hovered" class="readout">
      <span class="lede">{{ RESULTS.find((result) => result.code === hovered!.result)!.label }}</span>
      <span class="fact">
        <span class="term">Pitch</span>
        <span class="fact-value">{{ PITCH_TYPE_LABELS[hovered.pitch_type] }}</span>
      </span>
      <span class="fact">
        <span class="term">Zone</span>
        <span class="fact-value">{{ hovered.in_zone ? 'In' : 'Out' }}</span>
      </span>
      <span class="fact">
        <span class="term">Height</span>
        <span class="fact-value">{{ hovered.plate_z.toFixed(1) }} ft</span>
      </span>
      <span v-if="hovered.bat_speed !== null" class="fact">
        <span class="term">Bat speed</span>
        <span class="fact-value">{{ hovered.bat_speed.toFixed(1) }} mph</span>
      </span>
      <span v-if="hovered.exit_velo !== null" class="fact">
        <span class="term">Exit velo</span>
        <span class="fact-value">{{ hovered.exit_velo.toFixed(1) }} mph</span>
      </span>
    </div>
    <p v-else class="readout empty">Point at a pitch for its detail. Colour is pitch type.</p>
  </figure>
</template>

<style scoped>
figure {
  margin: 0;
}

.results {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.9rem;
}

.results button {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.32rem 0.75rem;
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: 999px;
  font-size: 0.84rem;
  color: var(--ink-2);
  cursor: pointer;
}

.results button.off {
  border-style: dashed;
  color: var(--muted);
  opacity: 0.55;
}

.glyph {
  width: 15px;
  height: 15px;
  overflow: visible;
}

.glyph .take,
.glyph .whiff,
.glyph .foul {
  stroke: var(--ink-2);
}

.glyph .in-play {
  fill: var(--ink-2);
  stroke: none;
}

svg {
  display: block;
  width: 100%;
  max-width: 660px;
  height: auto;
  margin: 0 auto;
}

.stance-label {
  fill: var(--muted);
  stroke: none;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.plate {
  fill: var(--tint);
  stroke: var(--rule);
}

.zone {
  fill: none;
  stroke: var(--brown);
  stroke-width: 1.5;
}

.shadow {
  fill: none;
  stroke: var(--rule);
  stroke-dasharray: 4 4;
}

.take {
  fill: none;
  stroke-width: 1.5;
  stroke-linejoin: round;
}

.whiff {
  fill: none;
  stroke-width: 2.4;
  stroke-linecap: round;
}

.foul {
  fill: var(--surface);
  stroke-width: 2;
}

/* Balls in play carry a dark ring and a slightly larger disc, so they read as
   the foreground against the outlined marks rather than only as a filled one. */
.in-play {
  stroke: var(--brown);
  stroke-width: 1.2;
}

/* Balls in play are the outcome the view is about, so everything short of one
   sits well back. */
.mark.take {
  opacity: 0.35;
}

.mark.whiff,
.mark.foul {
  opacity: 0.6;
}

.target {
  fill: transparent;
}

.mark:hover {
  opacity: 1;
}

.mark:hover .take,
.mark:hover .foul,
.mark:hover .in-play {
  stroke: var(--brown);
  stroke-width: 2.5;
}

.mark:hover .whiff {
  stroke-width: 4;
}

.bands {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 1.1rem 0 0;
  padding-top: 0.9rem;
  border-top: 1px solid var(--line);
  text-align: center;
}

.band dd {
  margin: 0;
}

.rate {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.count {
  font-size: 0.8rem;
  color: var(--muted);
}
</style>
