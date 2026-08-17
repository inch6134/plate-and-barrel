export const PITCH_TYPE_LABELS: Record<string, string> = {
  '4S': 'Four-seam',
  '2S': 'Sinker',
  'CT': 'Cutter',
  'SL': 'Slider',
  'SW': 'Sweeper',
  'CB': 'Curveball',
  'CH': 'Changeup',
  'SP': 'Splitter',
}

/* Eight categorical hues, warm for fastballs, cool for breaking, green for
   offspeed, so the pitch families stay readable even though every type has its
   own colour. Taken from the validated house palette rather than invented: on a
   scatter any two types can land side by side, and no set of eight clears
   colourblind separation on all 28 pairs. Type is therefore never carried by
   colour alone - the legend names every type, the filter pills isolate one at a
   time, and the readout spells out the pitch you are pointing at. */
export const PITCH_COLORS: Record<string, string> = {
  '4S': '#e34948',
  '2S': '#eb6834',
  'CT': '#eda100',
  'SL': '#4a3aa7',
  'SW': '#e87ba4',
  'CB': '#2a78d6',
  'CH': '#1baf7a',
  'SP': '#008300',
}

export const PITCH_ORDER = ['4S', '2S', 'CT', 'SL', 'SW', 'CB', 'CH', 'SP']

export const FAMILIES = [
  { code: 'fastball', label: 'Fastballs', types: ['4S', '2S', 'CT'] },
  { code: 'breaking', label: 'Breaking', types: ['SL', 'SW', 'CB'] },
  { code: 'offspeed', label: 'Offspeed', types: ['CH', 'SP'] },
]
