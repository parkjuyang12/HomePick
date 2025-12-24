backend/
├─ core/                       # 공통 설정, 예외, 공용 유틸
│  ├─ elasticsearch.py         # ES client
│  ├─ exceptions.py
│  └─ constants.py             # asset_type, transaction_type enum
│
├─ map/                        # 지도 UI 컨텍스트 (오케스트레이션)
│  ├─ views.py                 # map/search, bounds 기반 API
│  ├─ urls.py
│  └─ serializers.py           # 지도 전용 응답 형태
│
├─ properties/                 # "건물" 도메인 (실거래 기반)
│  ├─ services/
│  │  ├─ search.py             # 통합 검색 (bounds + filter + zoom)
│  │  ├─ history.py            # 거래 이력 조회
│  │  ├─ strategy.py           # zoom → 조회 전략
│  │  └─ filter.py             # FilterSpec 정의 ⭐
│  │
│  ├─ serializers.py           # 건물 요약 / 상세
│  └─ utils.py                 # property_id 파싱 등
|
├─ geo/                        # 좌표 / 위치 도메인 ⭐
│  ├─ services.py              # geocode, reverse geocode
│  └─ utils.py                 # bounds 계산, zoom 처리
│
├─ listings/                   # (확장) 매물 도메인
│  ├─ services/
│  │  ├─ search.py
│  │  └─ filter.py
│  ├─ serializers.py
│  └─ urls.py


[Frontend]
 └─ /api/map/search
     ├─ asset_type=APARTMENT
     ├─ transaction_type=TRADE
     ├─ bounds + zoom
          ↓
[map/views.py]
 └─ filter_spec 생성
          ↓
[properties/services/search.py]
 ├─ filter 적용
 ├─ zoom → strategy
 └─ ES 조회