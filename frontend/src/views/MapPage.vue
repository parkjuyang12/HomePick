<template>
  <div class="map-container">
    <h2>HomePick 매물 지도</h2>
    <div id="map" ref="mapElement"></div>
  </div>
</template>

<script>
export default {
  name: 'MapPage',
  mounted() {
    // 구글 맵 API 스크립트가 로드되었는지 확인 후 실행합니다.
    if (window.google && window.google.maps) {
      this.initMap();
    } else {
      // 혹시 로드가 늦어질 경우를 대비해 1초 뒤 다시 시도합니다.
      setTimeout(this.initMap, 1000);
    }
  },
  methods: {
    initMap() {
      const map = new window.google.maps.Map(this.$refs.mapElement, {
        center: { lat: 37.5665, lng: 126.9780 },
        zoom: 12,
      });

      // 테스트용 가짜 데이터 (나중에 백엔드에서 받아올 데이터 구조)
      const locations = [
        { title: "매물 1", lat: 37.5665, lng: 126.9780 },
        { title: "매물 2", lat: 37.5700, lng: 126.9800 },
        { title: "매물 3", lat: 37.5600, lng: 126.9700 },
      ];

      // 반복문을 돌며 마커 생성
      locations.forEach(loc => {
        new window.google.maps.Marker({
          position: { lat: loc.lat, lng: loc.lng },
          map: map,
          title: loc.title
        });
      });
    }
  }
}
</script>

<style scoped>
.map-container {
  width: 100%;
  padding: 20px;
}

#map {
  width: 100%;
  height: 600px; /* 지도의 높이를 충분히 줍니다. */
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
</style>