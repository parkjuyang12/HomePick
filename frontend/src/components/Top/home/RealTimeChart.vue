<template>
  <div class="real-time-chart">
    <div class="chart-header">
      <div class="title">실거래가 실시간 추이</div>
      <div class="latest">최근: <strong>{{ latestValueLabel }}</strong></div>
    </div>

    <div class="chart-wrap">
      <svg class="chart" viewBox="0 0 300 120" preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id="grad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="#334DFF" stop-opacity="0.18" />
          <stop offset="100%" stop-color="#334DFF" stop-opacity="0.02" />
        </linearGradient>
      </defs>

      <path :d="areaPath" fill="url(#grad)" />
      <path :d="linePath" stroke="#334DFF" stroke-width="2" fill="none" stroke-linejoin="round" stroke-linecap="round" />
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RealTimeChart',
  props: {
    points: { type: Number, default: 30 },
    base: { type: Number, default: 10000 }
  },
  data() {
    return {
      values: [],
      timer: null
    }
  },
  computed: {
    latestValue() {
      return this.values.length ? this.values[this.values.length - 1] : this.base
    },
    latestValueLabel() {
      return this.formatK(this.latestValue)
    },
    scaledPoints() {
      const padding = 12
      const w = 300
      const h = 120
      const count = Math.max(2, this.points)
      const min = Math.min(...this.values)
      const max = Math.max(...this.values)
      const range = (max - min) || 1

      return this.values.map((v, i) => {
        const x = (i / (count - 1)) * (w - padding * 2) + padding
        const y = h - padding - ((v - min) / range) * (h - padding * 2)
        return { x, y }
      })
    },
    linePath() {
      if (!this.scaledPoints.length) return ''
      return this.scaledPoints.map((p, i) => (i === 0 ? `M ${p.x.toFixed(2)} ${p.y.toFixed(2)}` : `L ${p.x.toFixed(2)} ${p.y.toFixed(2)}`)).join(' ')
    },
    areaPath() {
      if (!this.scaledPoints.length) return ''
      const pts = this.scaledPoints
      const first = pts[0]
      const last = pts[pts.length - 1]
      const bottomY = 120 - 12
      const line = pts.map((p, i) => (i === 0 ? `M ${p.x.toFixed(2)} ${p.y.toFixed(2)}` : `L ${p.x.toFixed(2)} ${p.y.toFixed(2)}`)).join(' ')
      return `${line} L ${last.x.toFixed(2)} ${bottomY} L ${first.x.toFixed(2)} ${bottomY} Z`
    }
  },
  methods: {
    formatK(v) {
      if (v >= 1000000) return `${Math.round(v / 10000)}만`
      if (v >= 10000) return `${Math.round(v / 10000)}만`
      return `${Math.round(v)}`
    },
    pushValue(val) {
      this.values.push(val)
      if (this.values.length > this.points) this.values.shift()
    },
    simulateNext() {
      const last = this.values.length ? this.values[this.values.length - 1] : this.base
      // 랜덤 워크(작은 변동) + 추세(가벼운 노이즈)
      const noise = (Math.random() - 0.5) * (this.base * 0.01)
      const drift = (Math.random() - 0.5) * (this.base * 0.002)
      const next = Math.max(0, last + noise + drift)
      this.pushValue(next)
    }
  },
  mounted() {
    // 초기 값들 생성
    for (let i = 0; i < this.points; i++) {
      const jitter = (Math.random() - 0.5) * (this.base * 0.02)
      this.values.push(this.base + jitter)
    }

    // 실시간 시뮬레이션
    this.timer = setInterval(() => {
      this.simulateNext()
    }, 1500)
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  }
}
</script>

<style scoped>
.real-time-chart {
  width: calc(100% - 48px);
  max-width: 640px;
  margin: 14px auto 22px;
  padding: 14px 16px;
  border-radius: 14px;
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  box-shadow: 0 10px 30px rgba(16,24,40,0.06), 0 2px 6px rgba(16,24,40,0.04);
  border: 1px solid rgba(15,23,36,0.04);
  position: relative;
  overflow: hidden;
}

.chart-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.chart-header .title { font-size:15px; font-weight:700; color:#0f1724 }
.chart-header .latest { font-size:13px; color:#6b7280 }
.chart-wrap { padding: 6px 6px 2px 6px; }
.chart { width:100%; height:110px; display:block }

/* path transition for smoothness */
path[stroke] { transition: d 0.6s linear; }

@media (max-width: 420px) {
  .real-time-chart { padding:10px; margin:10px 12px 10px; width: calc(100% - 32px); }
  .chart { height:90px }
  .chart-wrap { padding-left:14px }
}
</style>
