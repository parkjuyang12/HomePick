<template>
  <div class="recommend-section">
    <div class="section-header">
      <h2 class="section-title">이런 곳은 어떠세요?</h2>
      <p class="section-subtitle">지금 가장 인기있는 매물들이에요</p>
    </div>

    <!-- 가로 스크롤 카드 -->
    <div class="cards-scroll">
      <div 
        class="card" 
        v-for="(item, index) in recommends" 
        :key="index"
      >
        <!-- 이미지 -->
        <div class="card-image-wrapper">
          <img :src="item.icon" class="card-image" alt="추천 매물" />
          <div class="card-overlay">
            <span class="badge">추천</span>
            <div class="image-label">#보험 상품</div>
          </div>
        </div>
        
        <!-- 내용 -->
        <div class="card-content">
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-location">{{ item.location }}</p>
          <div class="card-footer">
            <span class="card-price">{{ item.price }}</span>
            <button class="card-button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 더보기 버튼 -->
    <div class="button-wrapper">
      <button class="show-more-btn">
        <span>더 많은 추천 보기</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import 보험 from '@/assets/recommend/보험.png'
import 보험2 from '@/assets/recommend/보험2.png'
import 보험3 from '@/assets/recommend/보험3.png'

const recommends = [
  { 
    icon: 보험,
    title: '강남 신축 아파트',
    location: '역세권 도보 5분',
    price: '12억 5천'
  },
  { 
    icon: 보험2,
    title: '판교 타워형 아파트',
    location: '학군 우수지역',
    price: '9억 8천'
  },
  { 
    icon: 보험3,
    title: '송파 리모델링 완료',
    location: '남향 전망 좋음',
    price: '11억 2천'
  }
];
</script>

<style scoped>
.recommend-section {
  padding: 24px 0;
  background: #ffffff;
}

/* 섹션 헤더 */
.section-header {
  padding: 0 20px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 22px;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}

.section-subtitle {
  font-size: 14px;
  color: #8e8e93;
  margin: 0;
  font-weight: 500;
}

/* 가로 스크롤 컨테이너 */
.cards-scroll {
  display: flex;
  gap: 12px;
  padding: 0 20px;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  margin-bottom: 20px;
}

.cards-scroll::-webkit-scrollbar {
  display: none;
}

/* 카드 - 크기 조정 */
.card {
  flex: 0 0 calc(100% - 60px); /* ✅ 양옆 30px씩 보이게 */
  max-width: 210px; /* ✅ 320px → 210px (3분의2 크기) */
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  scroll-snap-align: center; /* ✅ 중앙 정렬 */
}

.card:active {
  transform: scale(0.98);
}

/* 이미지 영역 */
.card-image-wrapper {
  position: relative;
  width: 100%;
  height: 120px; /* 180px → 120px */
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, transparent 50%, rgba(0,0,0,0.6) 100%);
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.badge {
  align-self: flex-end;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  color: #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-label {
  color: white;
  font-size: 13px;
  font-weight: 700;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  align-self: flex-start;
}

/* 카드 콘텐츠 */
.card-content {
  padding: 12px;
}

.card-title {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px;
  letter-spacing: -0.3px;
  line-height: 1.2;
}

.card-location {
  font-size: 11px;
  color: #8e8e93;
  margin: 0 0 10px;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-price {
  font-size: 14px;
  font-weight: 800;
  color: #667eea;
  letter-spacing: -0.5px;
}

.card-button {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.card-button:active {
  transform: scale(0.9);
}

/* 더보기 버튼 */
.button-wrapper {
  padding: 0 20px;
}

.show-more-btn {
  width: 100%;
  padding: 16px;
  border: 2px solid #e5e5ea;
  border-radius: 16px;
  background: white;
  color: #1a1a1a;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.show-more-btn:active {
  transform: scale(0.98);
  background: #f8f9fa;
}

/* 모바일 최적화 */
@media (max-width: 375px) {
  .card {
    flex: 0 0 calc(100% - 50px);
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .card-image-wrapper {
    height: 160px;
  }
}

@media (min-width: 768px) {
  .card {
    flex: 0 0 340px;
  }
}
</style>