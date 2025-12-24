<template>
  <div class="map-page">
    <header class="map-hero">
      <div class="title-block">
        <router-link class="eyebrow logo-link" to="/">HomePick</router-link>
        <h1>매물 지도를 한눈에</h1>
        <p class="subtitle">부동산 실거래 흐름을 한 화면에서 확인하세요.</p>
      </div>
      <div class="hero-actions">
        <div class="chips">
          <button class="chip active" type="button">실거래</button>
          <button class="chip" type="button">전세</button>
          <button class="chip" type="button">월세</button>
        </div>
        <div class="stats">
          <div class="stat">
            <strong>1,284</strong>
            <span>활성 매물</span>
          </div>
          <div class="stat">
            <strong>{{ currentAddress || '종로구 청운효자동' }}</strong>
            <span>현재 위치</span>
          </div>
        </div>
      </div>
    </header>
    <section class="map-shell">
      <div class="map-toolbar">
        <label class="search">
          <span class="search-icon">⌕</span>
          <input 
            type="text" 
            v-model="localSearchQuery" 
            placeholder="지역이나 지하철역을 검색해보세요" 
            @keyup.enter="handleLocalSearch"
          />
        </label>
        <button class="ghost" type="button">필터</button>
        <button class="ghost" type="button">반경 2km</button>
      </div>
      <div id="map" ref="mapElement"></div>
      <div class="map-legend">
        <span class="legend-item"><i class="dot sale"></i>실거래</span>
        <span class="legend-item"><i class="dot rent"></i>전세</span>
        <span class="legend-item"><i class="dot lease"></i>월세</span>
      </div>
    </section>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'MapPage',
  data() {
    return {
      map: null,
      markers: [],
      currentAddress: '',
      localSearchQuery: '',
    };
  },
  mounted() {
    // 구글 맵 API 스크립트가 로드되었는지 확인 후 실행합니다.
    if (window.google && window.google.maps) {
      this.initMap();
    } else {
      // 혹시 로드가 늦어질 경우를 대비해 1초 뒤 다시 시도합니다.
      setTimeout(() => this.initMap(), 1000);
    }
  },
  // [추가] URL의 검색어가 변경될 때마다 지도를 업데이트합니다.
  watch: {
    '$route.query.address': {
      handler(newAddress) {
        if (newAddress && this.map) {
          this.fetchNearbyProperties(newAddress);
        }
      },
      immediate: false
    }
  },
  methods: {
    initMap() {
      this.map = new window.google.maps.Map(this.$refs.mapElement, {
        center: { lat: 37.5665, lng: 126.9780 },
        zoom: 12,
        mapTypeControl: false,
        fullscreenControl: false,
        streetViewControl: false,
        clickableIcons: false,
        gestureHandling: "greedy",
      });

      // [수정] 초기 로드 시 URL에 검색어가 있다면 해당 위치로 이동합니다.
      const initialAddress = this.$route.query.address;
      if (initialAddress) {
        this.fetchNearbyProperties(initialAddress);
      }
    },

    // [추가] 백엔드 API와 통신하여 좌표를 받고 지도를 이동시키는 핵심 로직
    async fetchNearbyProperties(address) {
      try {
        this.currentAddress = address;
        const response = await axios.get('http://localhost:8000/api/map/search/', {
          params: { address: address }
        });

        const { center, results } = response.data;

        if (center) {
          // 1. 지도의 중심을 검색된 위치로 이동
          const newCenter = new window.google.maps.LatLng(center.lat, center.lng);
          this.map.setCenter(newCenter);
          this.map.setZoom(15);

          // 2. 마커 표시
          this.renderMarkers(results);
        }
      } catch (error) {
        console.error("데이터를 불러오는 중 오류 발생:", error);
      }
    },

    // [추가] 받아온 매물 데이터를 지도에 마커로 렌더링
    renderMarkers(properties) {
      // 기존 마커 제거
      this.markers.forEach(marker => marker.setMap(null));
      this.markers = [];

      properties.forEach(prop => {
        // [업무 2 반영] 자산 유형에 따른 마커 커스텀 (이미지 경로 설정 필요)
        let iconPath = null;
        if (prop.asset_type === 'APARTMENT') {
          // 커스텀 아이콘 사용 시 예시: iconPath = '/img/marker_apt.png';
        }

        const marker = new window.google.maps.Marker({
          position: { lat: prop.lat, lng: prop.lng },
          map: this.map,
          title: prop.title,
          // 커스텀 아이콘이 없으면 기본 원형 심볼 유지
          icon: iconPath || {
            path: window.google.maps.SymbolPath.CIRCLE,
            fillColor: prop.asset_type === 'COMMERCIAL' ? "#22c0a6" : "#1d4ed8",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 2,
            scale: 8
          }
        });
        this.markers.push(marker);
      });
    },

    // 지도 페이지 내 검색창 엔터 처리
    handleLocalSearch() {
      if (this.localSearchQuery) {
        this.$router.push({ query: { address: this.localSearchQuery } });
      }
    }
  }
}
</script>

<style scoped>
:global(:root) {
  --ink: #0f1f3a;
  --muted: #536380;
  --accent: #1d4ed8;
  --accent-soft: #3b82f6;
  --mint: #22c0a6;
  --sun: #fbbf24;
  --card: rgba(255, 255, 255, 0.86);
  --shadow: 0 26px 70px rgba(15, 31, 58, 0.2);
}

@import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Nanum+Gothic:wght@400;700&display=swap");

.map-page {
  min-height: 100vh;
  padding: 24px 20px 24px;
  background: radial-gradient(circle at top left, #e6efff 0%, #f4f7fd 40%, #eef3fb 100%);
  font-family: "Space Grotesk", "Nanum Gothic", sans-serif;
  color: var(--ink);
  position: relative;
  overflow: hidden;
}

.map-page::before,
.map-page::after {
  content: "";
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.45;
  z-index: 0;
}

.map-page::before {
  top: -80px;
  right: -40px;
  background: radial-gradient(circle, #b7d0ff, transparent 70%);
}

.map-page::after {
  bottom: -120px;
  left: -60px;
  background: radial-gradient(circle, #c9ddff, transparent 70%);
}

.map-hero {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  z-index: 1;
  animation: rise 0.8s ease-out;
}

.title-block h1 {
  margin: 8px 0 10px;
  font-size: clamp(28px, 3.4vw, 38px);
  font-weight: 700;
}

.eyebrow {
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 12px;
  color: var(--muted);
}

.logo-link {
  text-decoration: none;
  color: inherit;
  font-weight: 600;
}

.logo-link:hover {
  color: var(--accent);
}

.subtitle {
  margin: 0;
  font-size: 15px;
  color: var(--muted);
}

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.chips {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.chip {
  border: 1px solid rgba(19, 33, 60, 0.15);
  background: rgba(255, 255, 255, 0.7);
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chip.active {
  background: var(--accent);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 12px 22px rgba(29, 78, 216, 0.35);
}

.chip:hover {
  transform: translateY(-1px);
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 14px;
}

.stat {
  background: var(--card);
  padding: 12px 16px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
}

.stat strong {
  display: block;
  font-size: 14px;
}

.stat span {
  font-size: 12px;
  color: var(--muted);
}

.map-shell {
  margin-top: 24px;
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: var(--shadow);
  background: var(--card);
  backdrop-filter: blur(12px);
  z-index: 1;
  animation: rise 0.9s ease-out;
}

.map-toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 34px rgba(29, 78, 216, 0.18);
  z-index: 2;
}

.search {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  background: #eef4ff;
  border-radius: 10px;
  padding: 8px 12px;
  color: var(--muted);
}

.search input {
  border: none;
  background: transparent;
  width: 100%;
  font-size: 10px;
  outline: none;
  color: var(--ink);
  font-family: inherit;
}

.ghost {
  border: none;
  background: #e9f1ff;
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 12px;
  cursor: pointer;
  color: var(--ink);
}

#map {
  width: 100%;
  height: clamp(320px, 62vh, 560px);
}

.map-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  gap: 14px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(15, 31, 58, 0.86);
  color: #fff;
  font-size: 12px;
  z-index: 2;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot.sale {
  background: var(--accent-soft);
}

.dot.rent {
  background: var(--mint);
}

.dot.lease {
  background: var(--sun);
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .map-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .map-legend {
    flex-wrap: wrap;
  }

  #map {
    height: clamp(320px, 58vh, 460px);
  }
}
</style>