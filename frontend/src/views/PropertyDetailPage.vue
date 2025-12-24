<template>
  <div class="property-detail">
    <button class="eyebrow logo-link back-link" type="button" @click="goBack">HomePick</button>
    <header class="hero">
      <div>
        <h1>{{ displayName || '이름 정보 없음' }}</h1>
      </div>
      <div class="badge">{{ filteredHistory.length }}건</div>
    </header>

    <section class="filters">
      <button
        v-for="option in periodOptions"
        :key="option.value"
        type="button"
        class="filter-chip"
        :class="{ active: periodFilter === option.value }"
        @click="periodFilter = option.value"
      >
        {{ option.label }}
      </button>
      <div class="divider"></div>
      <button
        v-for="option in typeOptions"
        :key="option.value"
        type="button"
        class="filter-chip"
        :class="{ active: typeFilter === option.value }"
        @click="typeFilter = option.value"
      >
        {{ option.label }}
      </button>
    </section>

    <section class="chart">
      <div class="section-title">
        <h2>가격 추이</h2>
        <span class="section-meta">필터 적용</span>
      </div>
      <div class="chart-tabs">
        <button
          type="button"
          class="chart-tab"
          :class="{ active: chartType === 'TRADE' }"
          @click="chartType = 'TRADE'"
        >
          매매
        </button>
        <button
          type="button"
          class="chart-tab"
          :class="{ active: chartType === 'RENT' }"
          @click="chartType = 'RENT'"
        >
          전세/월세
        </button>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <p class="chart-title">{{ chartHeaderTitle }}</p>
            <strong class="chart-value">{{ chartHeaderValue }}</strong>
          </div>
          <span class="chart-tag" :class="{ rent: chartType === 'RENT' }">{{ chartType }}</span>
        </div>
        <div class="chart-body">
          <svg class="chart-svg" viewBox="0 0 100 40" preserveAspectRatio="none">
            <defs>
              <linearGradient id="primaryFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="chartPrimaryColor" stop-opacity="0.35" />
                <stop offset="100%" :stop-color="chartPrimaryColor" stop-opacity="0" />
              </linearGradient>
              <linearGradient id="secondaryFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="chartSecondaryColor" stop-opacity="0.28" />
                <stop offset="100%" :stop-color="chartSecondaryColor" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path :d="chartPrimaryPath || fallbackPath" class="chart-line primary" :stroke="chartPrimaryColor" />
            <path :d="chartPrimaryAreaPath || fallbackAreaPath" class="chart-area primary" fill="url(#primaryFill)" />
            <path v-if="chartType === 'RENT'" :d="chartSecondaryPath || fallbackPath" class="chart-line secondary" :stroke="chartSecondaryColor" />
            <path v-if="chartType === 'RENT'" :d="chartSecondaryAreaPath || fallbackAreaPath" class="chart-area secondary" fill="url(#secondaryFill)" />
          </svg>
          <p v-if="chartEmpty" class="chart-empty">데이터 없음</p>
        </div>
        <div v-if="chartType === 'RENT'" class="chart-legend">
          <span><i class="legend-dot primary"></i>보증금</span>
          <span><i class="legend-dot secondary"></i>월세</span>
        </div>
      </div>
    </section>
    <section class="history">
      <div class="section-title">
        <h2>거래 이력</h2>
        <span class="section-meta">최근순</span>
      </div>
      <div v-if="loading" class="status">불러오는 중...</div>
      <div v-else-if="error" class="status error">{{ error }}</div>
      <div v-else-if="filteredHistory.length === 0" class="status">거래 이력이 없습니다.</div>
      <ul v-else class="history-list">
        <li v-for="(item, index) in filteredHistory" :key="index" class="history-item">
          <div class="history-main">
            <div class="history-title">
              <span class="chip">{{ formatTransactionType(item.transaction_type) }}</span>
              <span class="chip subtle">{{ formatAssetType(item.asset_type) }}</span>
            </div>
            <div class="history-amount">{{ formatDealAmount(item) }}</div>
            <div class="history-meta">
              <span>{{ formatDate(item.deal_date) }}</span>
              <span>·</span>
              <span>{{ formatArea(item.detail && item.detail.area) }}</span>
              <span v-if="item.detail && item.detail.floor != null">· {{ item.detail.floor }}층</span>
            </div>
          </div>
        </li>
      </ul>
    </section>
    <details class="raw-panel">
      <summary>Raw data</summary>
      <pre>{{ rawHistory }}</pre>
    </details>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PropertyDetailPage',
  data() {
    return {
      history: [],
      displayName: '',
      loading: false,
      error: '',
      periodFilter: '3m',
      typeFilter: 'all',
      periodOptions: [
        { value: '3m', label: '최근 3개월' },
        { value: '6m', label: '최근 6개월' },
        { value: '1y', label: '최근 1년' },
        { value: 'all', label: '전체' }
      ],
      typeOptions: [
        { value: 'all', label: '전체' },
        { value: 'TRADE', label: '매매' },
        { value: 'RENT', label: '전세/월세' }
      ],
      chartType: 'TRADE',
    };
  },
  computed: {
    propertyId() {
      return decodeURIComponent(this.$route.params.id || '');
    },
    filteredHistory() {
      const base = Array.isArray(this.history) ? this.history : [];
      const byType = this.typeFilter === 'all'
        ? base
        : base.filter(item => item.transaction_type === this.typeFilter);
      const cutoff = this.getCutoffDate(this.periodFilter);
      const byPeriod = cutoff
        ? byType.filter(item => this.parseDealDate(item.deal_date) >= cutoff)
        : byType;
      return [...byPeriod].sort((a, b) => this.parseDealDate(b.deal_date) - this.parseDealDate(a.deal_date));
    },
    periodHistory() {
      const base = Array.isArray(this.history) ? this.history : [];
      const cutoff = this.getCutoffDate(this.periodFilter);
      if (!cutoff) return base;
      return base.filter(item => this.parseDealDate(item.deal_date) >= cutoff);
    },
    tradeSeries() {
      const items = this.periodHistory.filter(item => item.transaction_type === 'TRADE');
      return this.buildSeries(items, item => item.price || item.deal_amount || item.amount);
    },
    rentDepositSeries() {
      const items = this.periodHistory.filter(item => item.transaction_type === 'RENT');
      return this.buildSeries(items, item => item.deposit);
    },
    rentMonthlySeries() {
      const items = this.periodHistory.filter(item => item.transaction_type === 'RENT');
      return this.buildSeries(items, item => item.monthly_rent);
    },
    chartPrimarySeries() {
      return this.chartType === 'RENT' ? this.rentDepositSeries : this.tradeSeries;
    },
    chartSecondarySeries() {
      return this.rentMonthlySeries;
    },
    chartPrimaryPath() {
      return this.buildPath(this.chartPrimarySeries.points);
    },
    chartPrimaryAreaPath() {
      return this.buildAreaPath(this.chartPrimarySeries.points);
    },
    chartSecondaryPath() {
      return this.buildPath(this.chartSecondarySeries.points);
    },
    chartSecondaryAreaPath() {
      return this.buildAreaPath(this.chartSecondarySeries.points);
    },
    chartPrimaryColor() {
      return this.chartType === 'RENT' ? '#16a34a' : '#3b82f6';
    },
    chartSecondaryColor() {
      return '#f59e0b';
    },
    chartHeaderTitle() {
      return this.chartType === 'RENT' ? '보증금/월세' : '매매가';
    },
    chartHeaderValue() {
      if (this.chartType === 'RENT') {
        const deposit = this.formatPrice(this.rentDepositSeries.latestValue);
        const monthly = this.formatPrice(this.rentMonthlySeries.latestValue);
        return `보증금 ${deposit} / 월 ${monthly}`;
      }
      return this.formatPrice(this.tradeSeries.latestValue);
    },
    fallbackPath() {
      return 'M 0 22 L 100 22';
    },
    fallbackAreaPath() {
      return 'M 0 22 L 100 22 L 100 36 L 0 36 Z';
    },
    chartEmpty() {
      const primaryPoints = this.chartPrimarySeries.points.length > 1;
      const secondaryPoints = this.chartType === 'RENT' ? this.chartSecondarySeries.points.length > 1 : true;
      return !(primaryPoints || secondaryPoints);
    },
    rawHistory() {
      return JSON.stringify(this.history, null, 2);
    }
  },
  watch: {
    propertyId: {
      immediate: true,
      handler(newId) {
        if (newId) this.fetchHistory(newId);
      }
    },
    typeFilter(newType) {
      if (newType === 'TRADE' || newType === 'RENT') {
        this.chartType = newType;
      }
    }
  },
  methods: {
    async fetchHistory(propertyId) {
      this.loading = true;
      this.error = '';
      try {
        const response = await axios.get(`http://localhost:8000/api/map/history/${encodeURIComponent(propertyId)}/`);
        this.history = response.data.history || [];
        this.displayName = response.data.display_name || '';
      } catch (err) {
        this.error = '거래 이력을 불러오지 못했습니다.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    formatDate(value) {
      if (!value) return '-';
      const raw = String(value);
      if (/^\d{8}$/.test(raw)) return `${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}`;
      if (/^\d{6}$/.test(raw)) return `${raw.slice(0, 4)}-${raw.slice(4, 6)}`;
      return raw;
    },
    buildSeries(items, valueGetter) {
      const points = [];
      items.forEach(item => {
        const x = this.parseDealDate(item.deal_date);
        const value = valueGetter(item);
        const y = Number(value);
        if (x && Number.isFinite(y)) {
          points.push({ x, y });
        }
      });
      const sorted = points.sort((a, b) => a.x - b.x);
      const latestValue = sorted.length ? sorted[sorted.length - 1].y : null;
      return { points: sorted, latestValue };
    },
    buildPath(points) {
      if (!points || points.length < 2) return '';
      const { minX, maxX, minY, maxY } = this.getBounds(points);
      const toX = value => this.scale(value, minX, maxX, 0, 100);
      const toY = value => this.scale(value, minY, maxY, 36, 4);
      return points
        .map((point, index) => `${index === 0 ? 'M' : 'L'} ${toX(point.x)} ${toY(point.y)}`)
        .join(' ');
    },
    buildAreaPath(points) {
      if (!points || points.length < 2) return '';
      const { minX, maxX, minY, maxY } = this.getBounds(points);
      const toX = value => this.scale(value, minX, maxX, 0, 100);
      const toY = value => this.scale(value, minY, maxY, 36, 4);
      const line = points
        .map((point, index) => `${index === 0 ? 'M' : 'L'} ${toX(point.x)} ${toY(point.y)}`)
        .join(' ');
      const last = points[points.length - 1];
      const first = points[0];
      return `${line} L ${toX(last.x)} 36 L ${toX(first.x)} 36 Z`;
    },
    getBounds(points) {
      const xs = points.map(point => point.x);
      const ys = points.map(point => point.y);
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);
      if (minY === maxY) {
        return { minX, maxX, minY: minY - 1, maxY: maxY + 1 };
      }
      return { minX, maxX, minY, maxY };
    },
    scale(value, min, max, outMin, outMax) {
      if (max === min) return outMin;
      return outMin + ((value - min) / (max - min)) * (outMax - outMin);
    },
    parseDealDate(value) {
      const raw = String(value || '').trim();
      if (/^\d{8}$/.test(raw)) return Number(raw);
      return 0;
    },
    getCutoffDate(period) {
      if (period === 'all') return null;
      const now = new Date();
      const months = period === '3m' ? 3 : period === '6m' ? 6 : 12;
      now.setMonth(now.getMonth() - months);
      const yyyy = now.getFullYear();
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      const dd = String(now.getDate()).padStart(2, '0');
      return Number(`${yyyy}${mm}${dd}`);
    },
    formatAssetType(value) {
      if (!value) return '-';
      const map = {
        APARTMENT: '아파트',
        HOUSE: '주택',
        COMMERCIAL: '상가',
        OFFICETEL: '오피스텔',
      };
      return map[value] || value;
    },
    formatTransactionType(value) {
      if (!value) return '-';
      const map = {
        TRADE: '매매',
        RENT: '전세/월세',
        LEASE: '전세',
      };
      return map[value] || value;
    },
    formatPrice(value) {
      if (value == null) return '가격미정';
      const num = Number(String(value).replace(/,/g, ''));
      if (Number.isNaN(num)) return String(value);
      const eok = Math.floor(num / 10000);
      const man = Math.floor(num % 10000);
      let res = "";
      if (eok > 0) res += `${eok}억 `;
      if (man > 0) return `${res}${man.toLocaleString()}만`.trim();
      return res.trim();
    },
    formatDealAmount(item) {
      if (!item) return '-';
      if (item.transaction_type === 'RENT') {
        const deposit = this.formatPrice(item.deposit);
        const monthly = item.monthly_rent ? this.formatPrice(item.monthly_rent) : '0';
        return `보증금 ${deposit} / 월 ${monthly}`;
      }
      return this.formatPrice(item.price || item.deal_amount || item.amount);
    },
    formatArea(value) {
      if (!value) return '-';
      const num = Number(value);
      if (Number.isNaN(num)) return String(value);
      return `${num.toFixed(1)}㎡`;
    },
    goBack() {
      this.$router.back();
    }
  }
};
</script>

<style scoped>
.property-detail {
  min-height: 100vh;
  padding: 24px 20px 32px;
  background: #f4f6fb;
  color: #0f1f3a;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 12px;
  color: #536380;
}

.logo-link {
  text-decoration: none;
  color: inherit;
  font-weight: 600;
  display: inline-block;
  margin-bottom: 8px;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.logo-link:hover {
  color: #1d4ed8;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.hero > div {
  min-width: 0;
  flex: 1 1 auto;
}

.hero h1 {
  margin: 2px 0 6px;
  font-size: clamp(18px, 3.2vw, 26px);
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge {
  min-width: 56px;
  padding: 6px 12px;
  border-radius: 999px;
  background: #e9f1ff;
  color: #1d4ed8;
  font-weight: 700;
  font-size: 12px;
  text-align: center;
  white-space: nowrap;
  flex-shrink: 0;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-title h2 {
  margin: 0;
  font-size: 18px;
}

.section-meta {
  font-size: 12px;
  color: #7b8aa5;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 10px 22px rgba(15, 31, 58, 0.08);
  margin-bottom: 20px;
}

.filter-chip {
  border: none;
  background: #eef2ff;
  color: #1f2937;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.filter-chip.active {
  background: #1d4ed8;
  color: #fff;
}

.divider {
  width: 1px;
  height: 20px;
  background: #e2e8f0;
  margin: 0 2px;
}

.status {
  margin-top: 12px;
  font-size: 14px;
  color: #52607a;
}

.status.error {
  color: #b91c1c;
}

.history {
  margin-top: 20px;
}

.chart {
  margin-top: 28px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.chart-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(237, 242, 255, 0.9));
  border-radius: 20px;
  padding: 18px;
  box-shadow: 0 18px 32px rgba(15, 31, 58, 0.08);
  display: grid;
  gap: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.chart-tabs {
  display: inline-flex;
  gap: 6px;
  padding: 4px;
  border-radius: 999px;
  background: #eef2ff;
  margin-bottom: 12px;
}

.chart-tab {
  border: none;
  background: transparent;
  color: #1f2937;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.chart-tab.active {
  background: #1d4ed8;
  color: #fff;
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.chart-title {
  margin: 0;
  font-size: 12px;
  color: #7b8aa5;
}

.chart-value {
  font-size: 18px;
  font-weight: 700;
  color: #0f1f3a;
}

.chart-tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  background: #e9f1ff;
  color: #1d4ed8;
}

.chart-tag.rent {
  background: #ecfdf3;
  color: #15803d;
}

.chart-svg {
  width: 100%;
  height: 128px;
}

.chart-body {
  position: relative;
}

.chart-empty {
  position: absolute;
  right: 12px;
  top: 10px;
  font-size: 12px;
  color: #94a3b8;
}

.chart-line {
  fill: none;
  stroke-width: 1.6;
}

.chart-line.primary {
  stroke-linecap: round;
  stroke-linejoin: round;
}

.chart-line.secondary {
  stroke-linecap: round;
  stroke-linejoin: round;
}

.chart-area {
  opacity: 0.9;
}

.chart-legend {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #7b8aa5;
}

.legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.legend-dot.primary {
  background: #22c0a6;
}

.legend-dot.secondary {
  background: #f59e0b;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 12px;
}

.history-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  padding: 16px 18px;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 14px 28px rgba(15, 31, 58, 0.08);
  font-size: 14px;
}

.history-main {
  display: grid;
  gap: 8px;
}

.history-title {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: #1d4ed8;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.chip.subtle {
  background: #e9f1ff;
  color: #1d4ed8;
}

.history-amount {
  font-size: 18px;
  font-weight: 700;
  color: #0f1f3a;
}

.history-meta {
  display: flex;
  gap: 6px;
  color: #7b8aa5;
  font-size: 12px;
}

.raw-panel {
  margin-top: 18px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 12px;
}

.raw-panel summary {
  cursor: pointer;
  font-weight: 600;
  margin-bottom: 8px;
  color: #e5edff;
}

.raw-panel pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}
</style>
