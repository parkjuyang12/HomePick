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
            <strong>{{ currentDisplayAddress || '지역을 검색하세요' }}</strong>
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
        <button v-if="!$route.query.category" class="ghost" type="button">필터</button>
        <button class="ghost" type="button">반경 2km</button>
      </div>
      
      <div id="map" ref="mapElement"></div>

      <div v-if="!$route.query.category" class="map-legend">
        <span class="legend-item"><i class="dot sale"></i>아파트</span>
        <span class="legend-item"><i class="dot rent"></i>주택</span>
        <span class="legend-item"><i class="dot lease"></i>상가건물</span>
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
      currentDisplayAddress: '',
      localSearchQuery: '',
      lastResults: [],
    };
  },
  mounted() {
    if (window.google && window.google.maps) {
      this.initMap();
    } else {
      setTimeout(() => this.initMap(), 1000);
    }
  },
  watch: {
    '$route.query': {
      handler(newQuery) {
        if (this.map) {
          this.handleInitialLoad(newQuery.address, newQuery.category);
        }
      },
      deep: true
    }
  },
  methods: {
    initMap() {
      const mapOptions = {
        center: { lat: 37.5665, lng: 126.9780 },
        zoom: 14,
        mapTypeControl: false,
        fullscreenControl: false,
        streetViewControl: false,
        clickableIcons: false,
        gestureHandling: "greedy",
      };
      this.map = new window.google.maps.Map(this.$refs.mapElement, mapOptions);
      this.updateMarkerScale(this.map.getZoom());
      const restored = this.restoreMapState();
      this.map.addListener('zoom_changed', () => {
        this.updateMarkerScale(this.map.getZoom());
        if (this.lastResults.length) {
          this.renderBubbleMarkers(this.lastResults);
        }
      });
      this.map.addListener('dragend', () => {
        this.persistMapState();
      });
      if (!restored) {
        this.handleInitialLoad(this.$route.query.address, this.$route.query.category);
      }
    },

    // [수정] 진입 시 검색어 유무에 따른 로직 분기 (실제 사용자 위치 반영)
    async handleInitialLoad(address, category) {
      console.log('📍 handleInitialLoad 호출:', { address, category });
      
      // 유효한 검색어가 있는 경우에만 검색
      const hasValidAddress = address && typeof address === 'string' && address.trim().length > 0;
      
      if (hasValidAddress) {
        console.log('🔍 검색어 있음 - 검색 실행:', address);
        this.fetchNearbyProperties(address, category);
      } else if (category) {
        console.log('📱 카테고리만 있음 - 현재 위치 요청');
        this.getCurrentLocationAndSearch(category);
      } else {
        console.log('⚠️ address와 category 모두 없음');
      }
    },

    // [추가] 브라우저 Geolocation을 사용하여 사용자 위치 기반 검색
    getCurrentLocationAndSearch(category) {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            // 좌표를 문자열로 전달하여 백엔드에서 주소 변환 및 검색 수행
            this.fetchNearbyProperties(`${lat},${lng}`, category);
          },
          () => {
            // 위치 권한 거부 시 기본값 사용
            this.fetchNearbyProperties('판교역', category);
          }
        );
      } else {
        this.fetchNearbyProperties('판교역', category);
      }
    },

    async fetchNearbyProperties(address, category) {
      try {
        // 좌표가 들어온 경우(lat,lng) currentDisplayAddress를 '현재 위치'로 표시
        this.currentDisplayAddress = address.includes(',') ? '현재 위치 주변' : address;
        
        const response = await axios.get('http://localhost:8000/api/map/search/', {
          params: { 
            address: address,
            category: category 
          }
        });

        const { center, results } = response.data;
        if (center) {
          const newPos = new window.google.maps.LatLng(center.lat, center.lng);
          this.map.setCenter(newPos);
          this.map.setZoom(15);
          this.lastResults = results;
          this.renderBubbleMarkers(results);
          this.persistMapState();
        }
      } catch (error) {
        console.error("Fetch Error:", error);
      }
    },

    renderBubbleMarkers(properties) {
      this.markers.forEach(m => m.setMap(null));
      this.markers = [];

      const zoom = this.map ? this.map.getZoom() : 14;
      const clustered = zoom <= 15 ? this.clusterProperties(properties, zoom) : null;
      const items = clustered || properties;

      items.forEach(item => {
        const isCluster = !!item.isCluster;
        const prop = item.sample || item;
        const priceLabel = this.formatPrice(prop.price);
        const typeClass = prop.asset_type ? prop.asset_type.toLowerCase() : 'default';

        const sizeForCluster = isCluster ? this.getClusterSize(item.count, zoom) : null;

        const div = document.createElement('div');
        if (isCluster) {
          div.className = 'cluster-marker';
          div.style.setProperty('--cluster-size', `${sizeForCluster}px`);
          div.setAttribute('data-count', item.count);
          div.innerHTML = `
            <div class="cluster-count">${item.count}</div>
          `;
        } else {
          div.className = `custom-bubble-marker ${typeClass}`;
          div.innerHTML = `
            <div class="marker-title">${prop.title}</div>
            <div class="marker-price">${priceLabel}</div>
            <div class="marker-tail"></div>
          `;
        }
        div.addEventListener('click', (event) => {
          event.stopPropagation();
          if (isCluster) {
            this.handleClusterClick(item);
          } else {
            this.handleMarkerClick(prop);
          }
        });

        const Overlay = function(pos, element, map) {
          this.pos = pos; this.element = element; this.setMap(map);
        };
        Overlay.prototype = new window.google.maps.OverlayView();
        Overlay.prototype.onAdd = function() { this.getPanes().overlayMouseTarget.appendChild(this.element); };
        Overlay.prototype.draw = function() {
          const position = this.getProjection().fromLatLngToDivPixel(this.pos);
          if (position) {
            this.element.style.left = (position.x - (this.element.offsetWidth / 2)) + 'px';
            this.element.style.top = (position.y - this.element.offsetHeight - 10) + 'px';
          }
        };
        Overlay.prototype.onRemove = function() { if (this.element.parentNode) this.element.parentNode.removeChild(this.element); };

        const position = new window.google.maps.LatLng(item.lat, item.lng);
        const overlayInstance = new Overlay(position, div, this.map);
        this.markers.push(overlayInstance);
      });
    },
    clusterProperties(properties, zoom) {
      const bucketSize = this.getClusterBucketSize(zoom);
      const buckets = new Map();

      properties.forEach(prop => {
        const keyLat = Math.floor(prop.lat / bucketSize);
        const keyLng = Math.floor(prop.lng / bucketSize);
        const key = `${keyLat},${keyLng}`;
        const existing = buckets.get(key);
        if (!existing) {
          buckets.set(key, {
            latSum: prop.lat,
            lngSum: prop.lng,
            count: 1,
            sample: prop,
          });
        } else {
          existing.latSum += prop.lat;
          existing.lngSum += prop.lng;
          existing.count += 1;
        }
      });

      return Array.from(buckets.values()).map(bucket => ({
        isCluster: true,
        lat: bucket.latSum / bucket.count,
        lng: bucket.lngSum / bucket.count,
        count: bucket.count,
        sample: bucket.sample,
      }));
    },
    getClusterBucketSize(zoom) {
      if (zoom <= 10) return 0.15; // ~15km
      if (zoom <= 12) return 0.08; // ~8km
      if (zoom <= 14) return 0.04; // ~4km
      return 0.02; // ~2km up to zoom 15
    },
    getClusterSize(count, zoom) {
      const base = 46;
      const countBoost = Math.min(32, Math.log(count + 1) * 12);
      const zoomBoost = Math.max(0, (zoom - 11) * 3);
      return Math.min(110, base + countBoost + zoomBoost);
    },
    handleClusterClick(cluster) {
      if (!this.map) return;
      const nextZoom = Math.min((this.map.getZoom() || 14) + 2, 17);
      this.map.setCenter(new window.google.maps.LatLng(cluster.lat, cluster.lng));
      this.map.setZoom(nextZoom);
    },
    handleMarkerClick(prop) {
      if (!prop || !prop.id) return;
      this.$router.push({ path: `/property/${prop.id}` });
    },
    updateMarkerScale(zoom) {
      if (!this.$refs.mapElement) return;
      const minZoom = 11;
      const maxZoom = 17;
      const clamped = Math.min(Math.max(zoom, minZoom), maxZoom);
      const scale = 0.78 + ((clamped - minZoom) / (maxZoom - minZoom)) * 0.5;
      this.$refs.mapElement.style.setProperty('--marker-scale', scale.toFixed(2));
    },
    persistMapState() {
      if (!this.map) return;
      const center = this.map.getCenter();
      const state = {
        center: center ? { lat: center.lat(), lng: center.lng() } : null,
        zoom: this.map.getZoom(),
        address: this.$route.query.address || '',
        category: this.$route.query.category || '',
        results: this.lastResults || [],
      };
      sessionStorage.setItem('map_state', JSON.stringify(state));
    },
    restoreMapState() {
      const raw = sessionStorage.getItem('map_state');
      if (!raw) return false;
      try {
        const state = JSON.parse(raw);
        if (state.center && typeof state.center.lat === 'number' && typeof state.center.lng === 'number') {
          this.map.setCenter(state.center);
        }
        if (typeof state.zoom === 'number') {
          this.map.setZoom(state.zoom);
        }
        if (Array.isArray(state.results)) {
          this.lastResults = state.results;
          this.renderBubbleMarkers(state.results);
        }
        return true;
      } catch (error) {
        console.warn('Failed to restore map state', error);
        return false;
      }
    },

    formatPrice(price) {
      if (!price) return "가격미정";
      const eok = Math.floor(price / 100000000);
      const man = Math.floor((price % 100000000) / 10000);
      let res = "";
      if (eok > 0) res += `${eok}억 `;
      if (man > 0) res += `${man.toLocaleString()}`;
      return res + "만";
    },

    handleLocalSearch() {
      if (this.localSearchQuery.trim()) {
        this.$router.push({ 
          query: { 
            address: this.localSearchQuery 
            // 검색어로 검색 시에는 카테고리 필터를 제거하여 범례/필터 버튼이 다시 나오게 함
          } 
        });
      }
    }
  }
}
</script>

<style scoped>
/* --- 기존 스타일 유지 --- */
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

.map-page::before, .map-page::after {
  content: ""; position: absolute; width: 320px; height: 320px; border-radius: 50%; filter: blur(40px); opacity: 0.45; z-index: 0;
}
.map-page::before { top: -80px; right: -40px; background: radial-gradient(circle, #b7d0ff, transparent 70%); }
.map-page::after { bottom: -120px; left: -60px; background: radial-gradient(circle, #c9ddff, transparent 70%); }

.map-hero { display: flex; flex-direction: column; gap: 20px; position: relative; z-index: 1; animation: rise 0.8s ease-out; }
.title-block h1 { margin: 8px 0 10px; font-size: clamp(28px, 3.4vw, 38px); font-weight: 700; }
.eyebrow { letter-spacing: 0.18em; text-transform: uppercase; font-size: 12px; color: var(--muted); }
.logo-link { text-decoration: none; color: inherit; font-weight: 600; }
.logo-link:hover { color: var(--accent); }
.subtitle { margin: 0; font-size: 15px; color: var(--muted); }

.hero-actions { display: flex; flex-direction: column; gap: 18px; }
.chips { display: flex; gap: 10px; flex-wrap: wrap; }
.chip { border: 1px solid rgba(19, 33, 60, 0.15); background: rgba(255, 255, 255, 0.7); padding: 8px 14px; border-radius: 999px; font-size: 13px; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease; }
.chip.active { background: var(--accent); color: #fff; border-color: transparent; box-shadow: 0 12px 22px rgba(29, 78, 216, 0.35); }
.chip:hover { transform: translateY(-1px); }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; }
.stat { background: var(--card); padding: 12px 16px; border-radius: 14px; box-shadow: var(--shadow); backdrop-filter: blur(12px); }
.stat strong { display: block; font-size: 14px; }
.stat span { font-size: 12px; color: var(--muted); }

.map-shell { margin-top: 24px; position: relative; border-radius: 24px; overflow: hidden; box-shadow: var(--shadow); background: var(--card); backdrop-filter: blur(12px); z-index: 1; animation: rise 0.9s ease-out; }
.map-toolbar { position: absolute; top: 16px; left: 16px; right: 16px; display: flex; gap: 12px; align-items: center; padding: 8px; border-radius: 16px; background: rgba(255, 255, 255, 0.94); box-shadow: 0 12px 34px rgba(29, 78, 216, 0.18); z-index: 2; }

.search { display: flex; align-items: center; gap: 8px; flex: 1; background: #eef4ff; border-radius: 10px; padding: 8px 12px; color: var(--muted); }
.search input { border: none; background: transparent; width: 100%; font-size: 12px; outline: none; color: var(--ink); font-family: inherit; }
.ghost { border: none; background: #e9f1ff; padding: 8px 10px; border-radius: 10px; font-size: 12px; cursor: pointer; color: var(--ink); }

#map { width: 100%; height: clamp(320px, 62vh, 560px); }

:global(.custom-bubble-marker) {
  position: absolute;
  padding: 10px 14px;
  background: linear-gradient(135deg, #63b3ff, #3b6bff 55%, #1d4ed8 100%);
  color: #f7fbff;
  border-radius: 18px;
  box-shadow: 0 12px 26px rgba(17, 24, 39, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.24);
  border: none;
  text-align: center;
  z-index: 10;
  cursor: pointer;
  transform: scale(var(--marker-scale, 1));
  transform-origin: 50% 100%;
  transition: transform 0.12s ease-out, box-shadow 0.12s ease-out;
}

:global(.custom-bubble-marker:hover) {
  box-shadow: 0 16px 30px rgba(17, 24, 39, 0.42), 0 0 0 1px rgba(255, 255, 255, 0.3);
  transform: translateY(-1px) scale(var(--marker-scale, 1));
}

:global(.cluster-marker) {
  position: absolute;
  width: var(--cluster-size, 64px);
  height: var(--cluster-size, 64px);
  border-radius: 50%;
  background: #1f4fd6;
  opacity: 0.96;
  color: #0f172a;
  border: 1.2px solid rgba(255, 255, 255, 0.34);
  box-shadow: 0 calc(var(--cluster-size, 64px) * 0.16) calc(var(--cluster-size, 64px) * 0.32) rgba(24, 39, 75, 0.18);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transform: scale(var(--marker-scale, 1));
  transform-origin: 50% 100%;
  transition: transform 0.14s ease-out, box-shadow 0.18s ease-out;
}

:global(.cluster-marker)::before {
  content: "";
  position: absolute;
  inset: -6%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(31, 79, 214, 0.26) 0%, rgba(31, 79, 214, 0.12) 38%, rgba(31, 79, 214, 0) 70%);
  z-index: 0;
}

:global(.cluster-marker)::after {
  content: "";
  position: absolute;
  inset: 12%;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.32), transparent 60%);
  z-index: 0;
}

:global(.cluster-count) {
  position: relative;
  z-index: 1;
  font-weight: 700;
  font-size: calc(var(--cluster-size, 64px) * 0.34);
  letter-spacing: 0.01em;
  color: #0f172a;
}

:global(.cluster-marker:hover) {
  box-shadow: 0 calc(var(--cluster-size, 64px) * 0.32) calc(var(--cluster-size, 64px) * 0.58) rgba(29, 78, 216, 0.4),
    0 0 0 calc(var(--cluster-size, 64px) * 0.15) rgba(59, 130, 246, 0.22);
  transform: translateY(-2px) scale(var(--marker-scale, 1));
}

:global(.marker-title) {
  font-weight: 700;
  font-size: 13px;
  margin-bottom: 2px;
  white-space: nowrap;
}

:global(.marker-price) {
  font-size: 11px;
  opacity: 0.95;
}

:global(.marker-tail) {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 7px solid transparent;
  border-top-color: inherit;
}

:global(.custom-bubble-marker .marker-tail),
:global(.cluster-marker .marker-tail) {
  display: none;
}

:global(.custom-bubble-marker.apartment) { background: linear-gradient(135deg, #63b3ff, #3b6bff 55%, #1d4ed8 100%); }
:global(.custom-bubble-marker.commercial) { background: linear-gradient(135deg, #4adeb5, #2bb48f 55%, #128569 100%); }
:global(.custom-bubble-marker.house) { background: linear-gradient(135deg, #ffe082, #f6c84e 55%, #f59e0b 100%); }

.map-legend { position: absolute; bottom: 16px; left: 16px; display: flex; gap: 14px; padding: 10px 14px; border-radius: 12px; background: rgba(15, 31, 58, 0.86); color: #fff; font-size: 12px; z-index: 2; }
.legend-item { display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot.sale { background: var(--accent-soft); }
.dot.rent { background: var(--mint); }
.dot.lease { background: var(--sun); }

@keyframes rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .map-toolbar { flex-direction: column; align-items: stretch; }
  .map-legend { flex-wrap: wrap; }
  #map { height: clamp(320px, 58vh, 460px); }
}
</style>
