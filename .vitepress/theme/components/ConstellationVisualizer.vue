<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { withBase } from 'vitepress'

interface SatelliteNode {
  id: string
  name: string
  ring: 'MKO' | 'LEO'
  mission: string
  missionLink: string
  status: 'ACTIVE' | 'QUEUED'
  initialAngleDeg: number
  periodSec: number
  altKm: number
  apKm: number
  peKm: number
  ecc: string
  inc: string
  antenna: string
  maxRangeKm: number
  slotLabel: string
}

const KERBIN_RADIUS_KM = 600.0
const ATMO_RADIUS_KM = 670.0
const KERBIN_SIDEREAL_PERIOD = 21549.425

// Scale: 1 px = 6.0 km => Kerbin R = 100 px, LEO (900km) = 150 px, MKO (1200km) = 200 px
const KM_TO_PX = 1 / 6.0
const CX = 240
const CY = 230

const SATELLITES: SatelliteNode[] = [
  // CoroltNet-MKO (600 km)
  {
    id: '1F',
    name: 'CoroltSat-1F',
    ring: 'MKO',
    mission: 'CSA-16',
    missionLink: '/missions/csa-16',
    status: 'ACTIVE',
    initialAngleDeg: 0.0,
    periodSec: 4395.164,
    altKm: 600.02,
    apKm: 601.15,
    peKm: 598.88,
    ecc: '0.000947',
    inc: '0.082°',
    antenna: '3x Codac-A23 (1,327 km)',
    maxRangeKm: 1327.4,
    slotLabel: 'Node 0 (Anchor 0.0°)',
  },
  {
    id: '1G',
    name: 'CoroltSat-1G',
    ring: 'MKO',
    mission: 'CSA-17',
    missionLink: '/missions/csa-17',
    status: 'ACTIVE',
    initialAngleDeg: 59.163,
    periodSec: 4395.282,
    altKm: 600.04,
    apKm: 601.15,
    peKm: 598.93,
    ecc: '0.000926',
    inc: '0.134°',
    antenna: '3x Codac-A23 (1,327 km)',
    maxRangeKm: 1327.4,
    slotLabel: 'Node 1 (+59.16°)',
  },
  {
    id: '1H',
    name: 'CoroltSat-1H',
    ring: 'MKO',
    mission: 'CSA-18',
    missionLink: '/missions/csa-18',
    status: 'ACTIVE',
    initialAngleDeg: 120.075,
    periodSec: 4395.165,
    altKm: 600.02,
    apKm: 601.14,
    peKm: 598.89,
    ecc: '0.000935',
    inc: '0.132°',
    antenna: '3x Codac-A23 (1,327 km)',
    maxRangeKm: 1327.4,
    slotLabel: 'Node 2 (+120.08°)',
  },
  {
    id: '1I',
    name: 'CoroltSat-1I',
    ring: 'MKO',
    mission: 'CSA-19',
    missionLink: '/missions/csa-19',
    status: 'ACTIVE',
    initialAngleDeg: 179.46,
    periodSec: 4395.178,
    altKm: 600.02,
    apKm: 601.16,
    peKm: 598.88,
    ecc: '0.000951',
    inc: '0.082°',
    antenna: '3x Codac-A23 (1,327 km)',
    maxRangeKm: 1327.4,
    slotLabel: 'Node 3 (+179.46° Antipode)',
  },
  {
    id: '1J',
    name: 'CoroltSat-1J',
    ring: 'MKO',
    mission: 'CSA-20',
    missionLink: '/missions/csa-20',
    status: 'ACTIVE',
    initialAngleDeg: 239.918,
    periodSec: 4395.204,
    altKm: 600.02,
    apKm: 601.15,
    peKm: 598.9,
    ecc: '0.000938',
    inc: '0.082°',
    antenna: '3x Codac-A23 (1,327 km)',
    maxRangeKm: 1327.4,
    slotLabel: 'Node 4 (+239.92° Record)',
  },
  {
    id: '1K',
    name: 'CoroltSat-1K',
    ring: 'MKO',
    mission: 'CSA-21 (Queued)',
    missionLink: '/missions/csa-20',
    status: 'QUEUED',
    initialAngleDeg: 300.0,
    periodSec: 4395.164,
    altKm: 600.0,
    apKm: 600.0,
    peKm: 600.0,
    ecc: '< 0.0010',
    inc: '0.000°',
    antenna: '3x Codac-A23 (1,327 km)',
    maxRangeKm: 1327.4,
    slotLabel: 'Node 5 (+300.0° Planned)',
  },
  // CoroltNet-LEO (300 km) - relative starting offsets
  {
    id: '1B',
    name: 'CoroltSat-1B',
    ring: 'LEO',
    mission: 'CSA-12',
    missionLink: '/missions/csa-12',
    status: 'ACTIVE',
    initialAngleDeg: 56.1,
    periodSec: 2882.093,
    altKm: 305.75,
    apKm: 311.49,
    peKm: 300.02,
    ecc: '0.006331',
    inc: '0.131°',
    antenna: 'Codac-A23 (650 km)',
    maxRangeKm: 650.0,
    slotLabel: 'LEO Slot 0 Anchor',
  },
  {
    id: '1D',
    name: 'CoroltSat-1D',
    ring: 'LEO',
    mission: 'CSA-14',
    missionLink: '/missions/csa-14',
    status: 'ACTIVE',
    initialAngleDeg: 90.7,
    periodSec: 2882.251,
    altKm: 305.78,
    apKm: 308.33,
    peKm: 303.24,
    ecc: '0.002813',
    inc: '0.173°',
    antenna: 'Codac-A23 (650 km)',
    maxRangeKm: 650.0,
    slotLabel: 'LEO Slot 1 (+34.6°)',
  },
  {
    id: '1E',
    name: 'CoroltSat-1E',
    ring: 'LEO',
    mission: 'CSA-15',
    missionLink: '/missions/csa-15',
    status: 'ACTIVE',
    initialAngleDeg: 46.4,
    periodSec: 2859.949,
    altKm: 301.1,
    apKm: 302.62,
    peKm: 299.59,
    ecc: '0.001678',
    inc: '0.095°',
    antenna: 'Codac-A23 (650 km)',
    maxRangeKm: 650.0,
    slotLabel: 'LEO Slot 2 (-9.7°)',
  },
  {
    id: '1C',
    name: 'CoroltSat-1C',
    ring: 'LEO',
    mission: 'CSA-13',
    missionLink: '/missions/csa-13',
    status: 'ACTIVE',
    initialAngleDeg: 185.1,
    periodSec: 2881.922,
    altKm: 305.72,
    apKm: 308.79,
    peKm: 302.65,
    ecc: '0.003390',
    inc: '0.190°',
    antenna: 'Codac-A23 (650 km)',
    maxRangeKm: 650.0,
    slotLabel: 'LEO Slot 3 (+129.0°)',
  },
]

const simTimeSec = ref(0)
const speedMultiplier = ref(200)
const ringFilter = ref<'ALL' | 'MKO' | 'LEO'>('ALL')
const showRfLinks = ref(true)
const showKscUplink = ref(true)
const selectedId = ref('1J')

let animFrame: number | null = null
let lastTimestamp = 0

function tick(ts: number) {
  if (!lastTimestamp) lastTimestamp = ts
  const dt = (ts - lastTimestamp) / 1000
  lastTimestamp = ts
  if (speedMultiplier.value > 0) {
    simTimeSec.value += dt * speedMultiplier.value
  }
  animFrame = requestAnimationFrame(tick)
}

onMounted(() => {
  animFrame = requestAnimationFrame(tick)
})

onUnmounted(() => {
  if (animFrame !== null) cancelAnimationFrame(animFrame)
})

function resetSim() {
  simTimeSec.value = 0
}

// Compute live positions
const visibleSatellites = computed(() => {
  return SATELLITES.filter((s) => ringFilter.value === 'ALL' || s.ring === ringFilter.value).map((s) => {
    const angularVelDegPerSec = 360.0 / s.periodSec
    // Counter-clockwise prograde orbital motion in SVG (negative angle step in screen Y-down coords)
    const angleDeg = (s.initialAngleDeg + angularVelDegPerSec * simTimeSec.value) % 360
    const rad = (-angleDeg * Math.PI) / 180
    const rKm = KERBIN_RADIUS_KM + s.altKm
    const rPx = rKm * KM_TO_PX
    return {
      ...s,
      angleDeg,
      xKm: rKm * Math.cos(rad),
      yKm: rKm * Math.sin(rad),
      x: CX + rPx * Math.cos(rad),
      y: CY + rPx * Math.sin(rad),
    }
  })
})

const kscPos = computed(() => {
  const angleDeg = (285.0 + (360.0 / KERBIN_SIDEREAL_PERIOD) * simTimeSec.value) % 360
  const rad = (-angleDeg * Math.PI) / 180
  const rPx = KERBIN_RADIUS_KM * KM_TO_PX
  return {
    xKm: KERBIN_RADIUS_KM * Math.cos(rad),
    yKm: KERBIN_RADIUS_KM * Math.sin(rad),
    x: CX + rPx * Math.cos(rad),
    y: CY + rPx * Math.sin(rad),
    angleDeg,
  }
})

// Check line-of-sight occlusion against Kerbin sphere (R = 600 km)
function hasLineOfSight(x1: number, y1: number, x2: number, y2: number, minClearanceKm = 595): boolean {
  const dx = x2 - x1
  const dy = y2 - y1
  const lenSq = dx * dx + dy * dy
  if (lenSq === 0) return true
  let t = -(x1 * dx + y1 * dy) / lenSq
  t = Math.max(0, Math.min(1, t))
  const closestX = x1 + t * dx
  const closestY = y1 + t * dy
  const dist = Math.hypot(closestX, closestY)
  return dist >= minClearanceKm
}

const activeLinks = computed(() => {
  if (!showRfLinks.value) return []
  const sats = visibleSatellites.value.filter((s) => s.status === 'ACTIVE')
  const links: Array<{
    key: string
    x1: number
    y1: number
    x2: number
    y2: number
    distKm: number
    ring: 'MKO' | 'LEO'
  }> = []

  for (let i = 0; i < sats.length; i++) {
    for (let j = i + 1; j < sats.length; j++) {
      const a = sats[i]
      const b = sats[j]
      if (a.ring !== b.ring) continue
      const distKm = Math.hypot(a.xKm - b.xKm, a.yKm - b.yKm)
      if (distKm <= a.maxRangeKm && hasLineOfSight(a.xKm, a.yKm, b.xKm, b.yKm, KERBIN_RADIUS_KM)) {
        links.push({
          key: `${a.id}-${b.id}`,
          x1: a.x,
          y1: a.y,
          x2: b.x,
          y2: b.y,
          distKm,
          ring: a.ring,
        })
      }
    }
  }
  return links
})

const kscLinks = computed(() => {
  if (!showKscUplink.value) return []
  const k = kscPos.value
  return visibleSatellites.value
    .filter((s) => s.status === 'ACTIVE')
    .map((s) => {
      const distKm = Math.hypot(s.xKm - k.xKm, s.yKm - k.yKm)
      // Dot product > 0 means satellite is above KSC local horizon
      const aboveHorizon = (s.xKm - k.xKm) * k.xKm + (s.yKm - k.yKm) * k.yKm > 0
      return { sat: s, distKm, visible: aboveHorizon && distKm <= s.maxRangeKm }
    })
    .filter((l) => l.visible)
})

const selectedSat = computed(() => {
  return visibleSatellites.value.find((s) => s.id === selectedId.value) || visibleSatellites.value[0]
})

const selectedSatLinksCount = computed(() => {
  const s = selectedSat.value
  if (!s || s.status !== 'ACTIVE') return 0
  return activeLinks.value.filter((l) => l.key.includes(s.id)).length
})

const formattedSimClock = computed(() => {
  const t = Math.floor(simTimeSec.value)
  const h = Math.floor(t / 3600)
  const m = Math.floor((t % 3600) / 60)
  const s = t % 60
  return `T+${String(h).padStart(2, '0')}h ${String(m).padStart(2, '0')}m ${String(s).padStart(2, '0')}s`
})
</script>

<template>
  <div class="csa-viz-container">
    <div class="csa-viz-header">
      <div class="csa-viz-title-block">
        <span class="csa-live-dot"></span>
        <span class="csa-viz-title">COROLTNET LIVE ORBITAL TRACKER</span>
        <span class="csa-viz-badge">5/6 MKO + 4/9 LEO</span>
      </div>
      <div class="csa-viz-clock">{{ formattedSimClock }}</div>
    </div>

    <div class="csa-viz-controls">
      <div class="csa-ctrl-group">
        <span class="csa-ctrl-label">WARP:</span>
        <button
          v-for="spd in [0, 1, 100, 200, 500, 1000]"
          :key="spd"
          :class="['csa-btn', { active: speedMultiplier === spd }]"
          @click="speedMultiplier = spd"
        >
          {{ spd === 0 ? 'PAUSE' : spd + 'x' }}
        </button>
        <button class="csa-btn" @click="resetSim" title="Reset to Epoch">↺</button>
      </div>

      <div class="csa-ctrl-group">
        <button
          v-for="f in (['ALL', 'MKO', 'LEO'] as const)"
          :key="f"
          :class="['csa-btn', { active: ringFilter === f }]"
          @click="ringFilter = f"
        >
          {{ f === 'ALL' ? 'ALL RINGS' : f === 'MKO' ? 'MKO 600km' : 'LEO 300km' }}
        </button>
        <button :class="['csa-btn', { active: showRfLinks }]" @click="showRfLinks = !showRfLinks">
          RF LINKS
        </button>
        <button :class="['csa-btn', { active: showKscUplink }]" @click="showKscUplink = !showKscUplink">
          KSC UPLINK
        </button>
      </div>
    </div>

    <div class="csa-viz-body">
      <!-- Orbital SVG Viewport -->
      <div class="csa-svg-wrap">
        <svg viewBox="0 0 480 460" class="csa-svg">
          <defs>
            <radialGradient id="kerbinGrad" cx="40%" cy="40%" r="60%">
              <stop offset="0%" stop-color="#1e6091" />
              <stop offset="65%" stop-color="#0f3460" />
              <stop offset="100%" stop-color="#071930" />
            </radialGradient>
            <radialGradient id="atmoGrad" cx="50%" cy="50%" r="50%">
              <stop offset="82%" stop-color="rgba(56, 189, 248, 0.0)" />
              <stop offset="95%" stop-color="rgba(56, 189, 248, 0.22)" />
              <stop offset="100%" stop-color="rgba(56, 189, 248, 0.0)" />
            </radialGradient>
            <filter id="glowNode" x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          <!-- Background Radar Grid -->
          <line :x1="CX" y1="15" :x2="CX" y2="445" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="3,4" />
          <line x1="20" :y1="CY" x2="460" :y2="CY" stroke="#1e293b" stroke-width="0.8" stroke-dasharray="3,4" />

          <!-- MKO Orbit Ring (600 km -> R=200px) -->
          <circle
            v-if="ringFilter !== 'LEO'"
            :cx="CX"
            :cy="CY"
            :r="1200 * KM_TO_PX"
            fill="none"
            stroke="#10b981"
            stroke-width="1.2"
            stroke-dasharray="5,5"
            opacity="0.4"
          />
          <!-- LEO Orbit Ring (300 km -> R=150px) -->
          <circle
            v-if="ringFilter !== 'MKO'"
            :cx="CX"
            :cy="CY"
            :r="900 * KM_TO_PX"
            fill="none"
            stroke="#38bdf8"
            stroke-width="1.1"
            stroke-dasharray="4,4"
            opacity="0.4"
          />

          <!-- Orbit Labels -->
          <text v-if="ringFilter !== 'LEO'" :x="CX + 4" :y="CY - 204" fill="#10b981" font-size="9" font-family="monospace">
            MKO-600 RING (T=4,395s)
          </text>
          <text v-if="ringFilter !== 'MKO'" :x="CX + 4" :y="CY - 154" fill="#38bdf8" font-size="9" font-family="monospace">
            LEO-300 RING (T=2,882s)
          </text>

          <!-- Inter-Satellite RF Links -->
          <line
            v-for="link in activeLinks"
            :key="link.key"
            :x1="link.x1"
            :y1="link.y1"
            :x2="link.x2"
            :y2="link.y2"
            :stroke="link.ring === 'MKO' ? '#10b981' : '#38bdf8'"
            stroke-width="1.6"
            opacity="0.65"
          />

          <!-- KSC Uplink Beams -->
          <line
            v-for="u in kscLinks"
            :key="'ksc-' + u.sat.id"
            :x1="kscPos.x"
            :y1="kscPos.y"
            :x2="u.sat.x"
            :y2="u.sat.y"
            stroke="#fbbf24"
            stroke-width="1.0"
            stroke-dasharray="3,3"
            opacity="0.55"
          />

          <!-- Kerbin Atmosphere & Planet Body -->
          <circle :cx="CX" :cy="CY" :r="ATMO_RADIUS_KM * KM_TO_PX" fill="url(#atmoGrad)" />
          <circle :cx="CX" :cy="CY" :r="KERBIN_RADIUS_KM * KM_TO_PX" fill="url(#kerbinGrad)" stroke="#38bdf8" stroke-width="1.2" />
          <text :x="CX" :y="CY + 3" fill="#93c5fd" font-size="10" font-weight="bold" text-anchor="middle" font-family="monospace">
            KERBIN
          </text>
          <text :x="CX" :y="CY + 15" fill="#64748b" font-size="8" text-anchor="middle" font-family="monospace">
            R = 600 km
          </text>

          <!-- KSC Ground Station -->
          <circle :cx="kscPos.x" :cy="kscPos.y" r="4" fill="#fbbf24" stroke="#060a14" stroke-width="1.2" />
          <text :x="kscPos.x + 7" :y="kscPos.y + 3" fill="#fbbf24" font-size="8.5" font-weight="bold" font-family="monospace">
            KSC
          </text>

          <!-- Satellite Nodes -->
          <g
            v-for="sat in visibleSatellites"
            :key="sat.id"
            class="csa-sat-node"
            @click="selectedId = sat.id"
          >
            <!-- Selection Halo -->
            <circle
              v-if="selectedId === sat.id"
              :cx="sat.x"
              :cy="sat.y"
              r="11"
              fill="none"
              stroke="#ffffff"
              stroke-width="1.2"
              stroke-dasharray="2,2"
            />
            <circle
              :cx="sat.x"
              :cy="sat.y"
              :r="sat.status === 'ACTIVE' ? 5.5 : 4.5"
              :fill="sat.status === 'QUEUED' ? '#1e293b' : sat.ring === 'MKO' ? '#10b981' : '#00e5ff'"
              :stroke="sat.status === 'QUEUED' ? '#94a3b8' : '#ffffff'"
              :stroke-dasharray="sat.status === 'QUEUED' ? '2,2' : 'none'"
              stroke-width="1.5"
              :filter="sat.status === 'ACTIVE' ? 'url(#glowNode)' : undefined"
            />
            <text
              :x="sat.x + 9"
              :y="sat.y + 3"
              :fill="sat.status === 'QUEUED' ? '#94a3b8' : sat.ring === 'MKO' ? '#6ee7b7' : '#7dd3fc'"
              font-size="9.5"
              font-weight="bold"
              font-family="monospace"
            >
              {{ sat.id }}
            </text>
          </g>
        </svg>
      </div>

      <!-- Telemetry Inspector Panel -->
      <div v-if="selectedSat" class="csa-inspector">
        <div class="csa-insp-header">
          <div>
            <div class="csa-insp-name">{{ selectedSat.name }}</div>
            <div class="csa-insp-slot">{{ selectedSat.slotLabel }}</div>
          </div>
          <span :class="['csa-status-pill', selectedSat.status === 'ACTIVE' ? 'active' : 'queued']">
            {{ selectedSat.status }}
          </span>
        </div>

        <div class="csa-insp-grid">
          <div class="csa-insp-item">
            <span class="lbl">MISSION</span>
            <span class="val">{{ selectedSat.mission }}</span>
          </div>
          <div class="csa-insp-item">
            <span class="lbl">RING</span>
            <span class="val">{{ selectedSat.ring }}-{{ selectedSat.ring === 'MKO' ? '600' : '300' }}</span>
          </div>
          <div class="csa-insp-item">
            <span class="lbl">ORBIT (Ap × Pe)</span>
            <span class="val">{{ selectedSat.apKm.toFixed(2) }} × {{ selectedSat.peKm.toFixed(2) }} km</span>
          </div>
          <div class="csa-insp-item">
            <span class="lbl">PERIOD (T)</span>
            <span class="val">{{ selectedSat.periodSec.toFixed(3) }} s</span>
          </div>
          <div class="csa-insp-item">
            <span class="lbl">ECCENTRICITY</span>
            <span class="val">{{ selectedSat.ecc }}</span>
          </div>
          <div class="csa-insp-item">
            <span class="lbl">INCLINATION</span>
            <span class="val">{{ selectedSat.inc }}</span>
          </div>
          <div class="csa-insp-item full">
            <span class="lbl">RELAY PAYLOAD</span>
            <span class="val">{{ selectedSat.antenna }}</span>
          </div>
          <div class="csa-insp-item full">
            <span class="lbl">LIVE CROSS-LINKS</span>
            <span class="val">{{ selectedSatLinksCount }} Active Inter-Satellite Hops</span>
          </div>
        </div>

        <div class="csa-insp-footer">
          <a :href="withBase(selectedSat.missionLink)" class="csa-insp-link">
            View {{ selectedSat.mission }} Telemetry Report →
          </a>
        </div>

        <div class="csa-node-pills">
          <button
            v-for="s in SATELLITES"
            :key="s.id"
            :class="['csa-pill-btn', { selected: selectedId === s.id, queued: s.status === 'QUEUED' }]"
            @click="selectedId = s.id"
          >
            {{ s.id }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.csa-viz-container {
  max-width: 1152px;
  margin: 2rem auto;
  background: linear-gradient(145deg, rgba(10, 16, 30, 0.95) 0%, rgba(5, 9, 18, 0.98) 100%);
  border: 1px solid rgba(0, 229, 255, 0.25);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
  color: #e2e8f0;
}

.csa-viz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.6);
  padding-bottom: 0.75rem;
  margin-bottom: 0.85rem;
}

.csa-viz-title-block {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.csa-live-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
  animation: pulseDot 2s infinite;
}

@keyframes pulseDot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.csa-viz-title {
  font-family: 'Orbitron', monospace, sans-serif;
  font-weight: 800;
  font-size: 0.95rem;
  letter-spacing: 0.08em;
  color: #f8fafc;
}

.csa-viz-badge {
  font-family: monospace;
  font-size: 0.75rem;
  background: rgba(16, 185, 129, 0.15);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.csa-viz-clock {
  font-family: monospace;
  font-size: 0.88rem;
  color: #00e5ff;
  background: rgba(0, 229, 255, 0.08);
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  border: 1px solid rgba(0, 229, 255, 0.2);
}

.csa-viz-controls {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.csa-ctrl-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.csa-ctrl-label {
  font-family: monospace;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-right: 0.2rem;
}

.csa-btn {
  font-family: monospace;
  font-size: 0.75rem;
  padding: 0.28rem 0.6rem;
  border-radius: 5px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.csa-btn:hover {
  border-color: #38bdf8;
  color: #ffffff;
}

.csa-btn.active {
  background: rgba(0, 229, 255, 0.18);
  border-color: #00e5ff;
  color: #00e5ff;
  font-weight: 700;
}

.csa-viz-body {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 1.25rem;
  align-items: center;
}

@media (max-width: 860px) {
  .csa-viz-body {
    grid-template-columns: 1fr;
  }
}

.csa-svg-wrap {
  background: radial-gradient(circle at center, #0b1325 0%, #050811 100%);
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 0.5rem;
}

.csa-svg {
  width: 100%;
  height: auto;
  display: block;
}

.csa-sat-node {
  cursor: pointer;
}

.csa-inspector {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.csa-insp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #1e293b;
  padding-bottom: 0.65rem;
}

.csa-insp-name {
  font-family: 'Orbitron', monospace, sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  color: #f8fafc;
}

.csa-insp-slot {
  font-family: monospace;
  font-size: 0.8rem;
  color: #38bdf8;
  margin-top: 0.15rem;
}

.csa-status-pill {
  font-family: monospace;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
}

.csa-status-pill.active {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.csa-status-pill.queued {
  background: rgba(148, 163, 184, 0.15);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.35);
}

.csa-insp-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
}

.csa-insp-item {
  background: rgba(6, 10, 20, 0.6);
  border: 1px solid #1e293b;
  border-radius: 6px;
  padding: 0.45rem 0.65rem;
  display: flex;
  flex-direction: column;
}

.csa-insp-item.full {
  grid-column: span 2;
}

.csa-insp-item .lbl {
  font-family: monospace;
  font-size: 0.68rem;
  color: #64748b;
  letter-spacing: 0.05em;
}

.csa-insp-item .val {
  font-family: monospace;
  font-size: 0.85rem;
  color: #f1f5f9;
  font-weight: 600;
  margin-top: 0.15rem;
}

.csa-insp-footer {
  padding-top: 0.25rem;
}

.csa-insp-link {
  display: inline-block;
  font-family: monospace;
  font-size: 0.82rem;
  color: #00e5ff;
  text-decoration: none;
  font-weight: 700;
}

.csa-insp-link:hover {
  text-decoration: underline;
}

.csa-node-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  border-top: 1px solid #1e293b;
  padding-top: 0.75rem;
}

.csa-pill-btn {
  font-family: monospace;
  font-size: 0.72rem;
  padding: 0.22rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #334155;
  background: #0b1120;
  color: #94a3b8;
  cursor: pointer;
}

.csa-pill-btn.selected {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  font-weight: 700;
}

.csa-pill-btn.queued {
  border-style: dashed;
}
</style>
