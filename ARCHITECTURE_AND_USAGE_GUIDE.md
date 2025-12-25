# HomePick - 아키텍처 및 사용 가이드

> **실시간 부동산 데이터 파이프라인 및 웹 서비스**  
> 공공데이터를 이벤트 스트림으로 수집하고, Apache Flink로 실시간 처리하여  
> Elasticsearch 기반의 검색 최적화된 부동산 정보 서비스를 제공합니다.

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [전체 아키텍처](#2-전체-아키텍처)
3. [주요 컴포넌트 상세](#3-주요-컴포넌트-상세)
4. [데이터 파이프라인 흐름](#4-데이터-파이프라인-흐름)
5. [프로젝트 구조](#5-프로젝트-구조)
6. [환경 구성 및 실행 방법](#6-환경-구성-및-실행-방법)
7. [웹 서비스 사용 방법](#7-웹-서비스-사용-방법)
8. [API 엔드포인트](#8-api-엔드포인트)
9. [개발 가이드](#9-개발-가이드)
10. [트러블슈팅](#10-트러블슈팅)

---

## 1. 프로젝트 개요

### 1.1 프로젝트 목적

HomePick은 **실시간 부동산 거래 정보를 수집, 처리, 제공하는 종합 플랫폼**입니다.

**핵심 기능:**
- 🏢 **실시간 거래 데이터 수집**: 공공데이터 포털 API를 통한 주기적 데이터 수집
- 🔄 **스트림 처리**: Apache Flink 기반 실시간 중복 제거 및 상태 관리
- 🔍 **고속 검색**: Elasticsearch 기반 매물 검색 및 필터링
- 💬 **AI 챗봇**: LLM 기반 부동산 상담 서비스
- 📍 **지도 통합**: 구글 맵 기반 지역 정보 및 매물 위치 표시
- ⭐ **관심 매물 관리**: 사용자별 찜 기능 및 알림

### 1.2 기술 스택

**Backend:**
- Django 4.x (REST API)
- PostgreSQL 14 (사용자 데이터, 메타데이터)
- Elasticsearch 7.17 (매물 검색 엔진)

**Data Pipeline:**
- Apache Kafka (이벤트 스트림)
- Apache Flink 1.18+ (실시간 스트림 처리)
- Zookeeper (Kafka 코디네이션)

**Frontend:**
- Vue.js 3
- Google Maps API

**Infrastructure:**
- Docker

---

## 2. 전체 아키텍처

### 2.1 시스템 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                      공공데이터 포털 API                           │
│              (아파트/다세대/오피스텔/상업용 거래정보)                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (10분 주기 Polling)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Transaction Kafka Producer                      │
|              거래 데이터 수집 및 fingerprint 기반 이벤트 처리             |
│             (거래 데이터 수집 및 Kafka 전송)                        │
└──────────────────────┬───────────────────────────────────────────┘
                       │ Raw Events
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Apache Kafka                               │
│  Topics:                                                          │
│  - apartment.trade, apartment.rent                                │
│  - house.multi.trade, house.multi.rent                            │
│  - officetel.trade, officetel.rent                                │
│  - commercial.trade                                               │
└──────────────────────┬───────────────────────────────────────────┘
                       │ Stream Processing
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Apache Flink Job                             │
│  기능:                                                             │
│  - 중복 제거 (Keyed State 기반)                                    │
│  - 최신 상태 판단 및 관리                                          │
│  - 거래 이력 생성 (PRICE_CHANGE, SOLD 등)                         │
│  - property_id 생성 (주소 기반 해싱)                               │
└──────────────┬───────────────────────┬──────────────────────────┘
               │                       │
               │ (Upsert)             │ (Append-only)
               ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  Elasticsearch (Current) │  │ Elasticsearch (History)  │
│  - realestate_current_*  │  │  - realestate_history_*  │
│  - 최신 매물 상태           │  │  - 거래/변경 이력            │
│  - 검색/필터/정렬 최적화      │  │  - 타임라인 분석용           │
└──────────────┬───────────┘  └──────────────┬───────────┘
               │                              │
               └──────────────┬───────────────┘
                              │ REST API 조회
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Django Backend                             │
│  Apps:                                                            │
│  - users: 사용자 관리, 카카오 소셜 로그인                               │
│  - properties: 매물 검색, 거래 정보 조회                               │ 
│  - chatbot: LLM 기반 부동산 상담                                   │
│  - map: 구글 맵 연동, 지역 정보                                    │
│  - favorites: 관심 매물 관리                                       │
└──────────────────────┬───────────────────────────────────────────┘
                       │ REST API (JSON)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Vue.js Frontend                            │
│  - 매물 검색 및 상세 정보                                          │
│  - 지도 기반 매물 탐색                                             │
│  - AI 챗봇 상담                                                    │
│  - 사용자 관심 매물 관리                                           │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 데이터 흐름 개념

```
[공공 API 응답] 
    → (있는 그대로)
→ [Kafka: 단일 진실 원천]
    → (판단 + 상태 관리)
→ [Flink: 두뇌 역할]
    ├─→ [ES Current: 최신 상태 조회]
    └─→ [ES History: 변경 이력]
→ [Django: 비즈니스 로직 + API]
→ [Vue: 사용자 인터페이스]
```

**핵심 설계 철학:**
1. **Kafka**: 수집한 데이터를 "사실 그대로" 보관 
2. **Flink**: 중복 제거, 최신 상태 판단, 히스토리 생성의 **유일한 책임자**
3. **Elasticsearch**: 조회 최적화된 결과만 저장 (처리는 하지 않음)
4. **Django**: 비즈니스 로직, 인증, 사용자 데이터 관리

---

## 3. 주요 컴포넌트 상세

### 3.1 Transaction Kafka Producer

**위치:** `transaction-kafka-producer/`

**역할:**
- 공공데이터 포털 API를 10분마다 호출
- 거래 데이터를 Kafka 토픽에 전송
- 체크포인트 기반 증분 수집 (마지막 조회 시점 저장)

**주요 파일:**
- `main.py`: Producer 메인 로직
- `fetchers/`: 자산 유형별 API 호출 로직
  - `apartment_trade.py`, `apartment_rent.py`
  - `house_multi_trade.py`, `house_multi_rent.py`
  - `officetel_trade.py`, `officetel_rent.py`
  - `commercial_trade.py`
- `messaging/producer.py`: Kafka 메시지 전송
- `state/postgres.py`: 체크포인트 저장 (마지막 API 호출 시점)

**수집 프로세스:**
```python
# 1. 마지막 체크포인트 조회
last_fetch = db.get_checkpoint()

# 2. API 호출
data = api.fetch(from_date=last_fetch, to_date=now)

# 3. Postgres fingerprint(거래별 식별자) 기반 변경 감지
if fingerprint is None: producer.send_event(event_type="CREATE",...)
elif prev_hash != data_hash: producer.send_event(event_type="UPDATE",...)

# 4. Kafka 전송
for item in data:
    producer.send(topic="apartment.trade", value=item)

# 5. 체크포인트 업데이트
db.update_checkpoint(now)
```

### 3.2 Apache Kafka

**역할:**
- 이벤트 로그의 **단일 진실 원천 (Single Source of Truth)**
- 재처리 및 장애 복구 지원
- 중복 포함, 원본 데이터 보존

**토픽 구조:**
```
apartment.trade        # 아파트 매매
apartment.rent         # 아파트 전월세
house.multi.trade      # 다세대/연립 매매
house.multi.rent       # 다세대/연립 전월세
officetel.trade        # 오피스텔 매매
officetel.rent         # 오피스텔 전월세
commercial.trade       # 상업용 건물 매매
```

**특징:**
- Retention: 7일 (설정 가능)
- Replication Factor: 1 (개발 환경)
- Auto Topic Creation: Enabled

### 3.3 Apache Flink Job

**위치:** `flink/job/transaction-job.py`

**핵심 역할:**
1. **중복 제거**: property_id 기준 Keyed State 관리
2. **최신 상태 판단**: 거래일, 가격, 상태 업데이트
3. **이력 생성**: 변경 발생 시 이벤트 생성 (PRICE_CHANGE, SOLD 등)

**처리 흐름:**
```python
# 1. Kafka 소스 설정
kafka_source = KafkaSource.builder() \
    .set_topics("apartment.trade", "house.multi.trade", ...) \
    .set_group_id("flink-transaction-consumer") \
    .build()

# 2. 스트림 생성
stream = env.from_source(kafka_source, ...)

# 3. 파싱 및 변환
parsed = stream.map(parse_transaction)

# 4. property_id 기준 키잉
keyed = parsed.key_by(lambda x: x['property_id'])

# 5. 상태 관리 및 처리
processed = keyed.process(TransactionProcessor())

# 6. 싱크 분기
processed.add_sink(create_current_sink())  # Current Index
processed.add_sink(create_history_sink())  # History Index
```

**Keyed State 구조:**
```python
class TransactionProcessor(KeyedProcessFunction):
    def __init__(self):
        self.state = None  # ValueState[dict]
    
    def process_element(self, value, ctx):
        # 1. 이전 상태 조회
        previous = self.state.value()
        
        # 2. 변경 판단
        if is_new_or_changed(previous, value):
            # 3. 이력 생성
            yield create_history_event(previous, value)
            
            # 4. 상태 업데이트
            self.state.update(value)
        
        # 5. Current 상태 출력 (항상)
        yield create_current_document(value)
```

**property_id 생성 로직:**
```python
def generate_property_id(address: dict, asset_type: str) -> str:
    """
    주소 정보를 기반으로 매물 고유 ID 생성
    - 법정동 코드
    - 읍면동
    - 지번/도로명
    - 건물명 (아파트/오피스텔)
    """
    components = [
        address['lawd_cd'],
        address['umd'],
        address.get('jibun', ''),
        address.get('apt_name', ''),
        asset_type
    ]
    return hashlib.sha256('|'.join(components).encode()).hexdigest()
```

### 3.4 Elasticsearch

**인덱스 구조:**

**A. Current Index (최신 상태)**
```
realestate_current_apartment
realestate_current_house
realestate_current_officetel
realestate_current_commercial
```

**매핑 예시:**
```json
{
  "mappings": {
    "properties": {
      "property_id": {"type": "keyword"},
      "transaction_type": {"type": "keyword"},
      "deal_date": {"type": "date"},
      "price": {"type": "long"},
      "deposit": {"type": "long"},
      "monthly_rent": {"type": "long"},
      "area_sqm": {"type": "float"},
      "floor": {"type": "integer"},
      "address": {
        "properties": {
          "sido": {"type": "keyword"},
          "sigungu": {"type": "keyword"},
          "umd": {"type": "keyword"},
          "jibun": {"type": "text"},
          "road": {"type": "text"},
          "display": {"type": "text"}
        }
      },
      "location": {"type": "geo_point"},
      "updated_at": {"type": "date"}
    }
  }
}
```

**B. History Index (거래 이력)**
```
realestate_history_apartment
realestate_history_house
realestate_history_officetel
realestate_history_commercial
```

**이력 이벤트 타입:**
- `NEW`: 신규 매물 등록
- `PRICE_CHANGE`: 가격 변동
- `SOLD`: 거래 완료
- `STATUS_CHANGE`: 상태 변경

### 3.5 Django Backend

**위치:** `backend/`

**앱 구조:**

**A. core/** - 프로젝트 설정
- `settings.py`: Django 설정, 환경변수, 데이터베이스
- `urls.py`: 전체 URL 라우팅
- `asgi.py`, `wsgi.py`: ASGI/WSGI 엔트리포인트

**B. users/** - 사용자 관리
- 카스텀 User 모델 (이메일, 생년월일, 프로필)
- 카카오 소셜 로그인 연동
- JWT 기반 인증

**C. properties/** - 매물 정보
- Elasticsearch 연동 검색
- 거래 정보 조회 (Current + History)
- 필터링 (지역, 가격, 면적, 거래 유형)

**D. chatbot/** - AI 챗봇
- LLM 기반 부동산 상담 (OpenAI/Anthropic)
- 매물 추천
- 부동산 용어 설명

**E. map/** - 지도 서비스
- 구글 맵 API 연동
- 지역 좌표 변환
- 주변 편의시설 정보

**F. favorites/** - 관심 매물
- 찜 기능
- 사용자별 매물 저장

### 3.6 Vue.js Frontend

**위치:** `frontend/`

**주요 페이지:**
- `HomePage.vue`: 메인 화면, 매물 검색
- `ChatbotPage.vue`: AI 챗봇 대화
- `FavoritePage.vue`: 관심 매물 목록
- `PropertyDetailPage.vue`: 매물 상세 정보
- `MapPage.vue`: 지도 기반 매물 탐색

**컴포넌트:**
- `Top/`: 헤더, 네비게이션
- `Bottom/`: 하단 탭 바
- `Login/`: 로그인 모달

---

## 4. 데이터 파이프라인 흐름

### 4.1 전체 파이프라인

```
1. API 수집 (10분 주기)
   → Transaction Producer가 공공 API 호출
   → 거래 데이터 JSON 획득

2. Kafka 전송
   → 자산 유형별 토픽에 메시지 발행
   → 원본 데이터 보존 (중복 포함)

3. Flink 스트림 처리
   → Kafka Consumer로 메시지 읽기
   → property_id 생성 및 키잉
   → Keyed State로 중복 판단
   → 변경 감지 시 이력 생성

4. Elasticsearch 저장
   → Current Index: Upsert (최신 상태)
   → History Index: Append (변경 이력)

5. Django API 제공
   → Elasticsearch 쿼리
   → 필터링, 정렬, 페이지네이션
   → REST API 응답

6. Frontend 렌더링
   → Vue Router로 페이지 라우팅
   → 매물 목록/상세 표시
   → 지도에 매물 마커 표시
```

### 4.2 중복 제거 메커니즘

**문제 상황:**
- 공공 API는 10분마다 호출됨
- 동일 거래가 여러 번 조회될 수 있음
- 변경되지 않은 데이터도 계속 들어옴

**Flink의 해결책:**
```python
# Keyed State 기반 중복 제거
class DeduplicationProcessor(KeyedProcessFunction):
    def open(self, runtime_context):
        # property_id별 마지막 데이터 저장
        self.last_state = runtime_context.get_state(
            ValueStateDescriptor("last_data", Types.PICKLED_BYTE_ARRAY())
        )
    
    def process_element(self, value, ctx):
        current = value
        previous = self.last_state.value()
        
        # 1. 신규 매물
        if previous is None:
            self.last_state.update(current)
            yield ("NEW", current)
            return
        
        # 2. 변경 감지
        if has_changed(previous, current):
            yield ("CHANGED", previous, current)
            self.last_state.update(current)
        else:
            # 중복 - 아무것도 하지 않음
            pass
```

### 4.3 거래 이력 생성

**시나리오 1: 가격 변동**
```python
# 이전 상태
previous = {
    "property_id": "abc123",
    "price": 900000000,
    "deal_date": "2025-12-01"
}

# 새로운 상태
current = {
    "property_id": "abc123",
    "price": 850000000,
    "deal_date": "2025-12-15"
}

# 생성되는 이력
history_event = {
    "property_id": "abc123",
    "event_type": "PRICE_CHANGE",
    "event_time": "2025-12-15T10:00:00",
    "old_price": 900000000,
    "new_price": 850000000,
    "change_amount": -50000000,
    "change_percent": -5.56
}
```

**시나리오 2: 거래 완료**
```python
history_event = {
    "property_id": "abc123",
    "event_type": "SOLD",
    "event_time": "2025-12-20T15:30:00",
    "final_price": 850000000,
    "transaction_type": "TRADE"
}
```

---

## 5. 프로젝트 구조

### 5.1 디렉토리 구조

```
HomePick/
│
├── docker-compose.yml          # 전체 서비스 오케스트레이션
├── Makefile                    # 편의 명령어 모음
├── README.md                   # 프로젝트 개념 설명
│
├── backend/                    # Django REST API
│   ├── core/                   # 프로젝트 설정
│   ├── users/                  # 사용자 관리
│   ├── properties/             # 매물 검색/조회
│   ├── chatbot/                # AI 챗봇
│   ├── map/                    # 지도 서비스
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Vue.js 3
│   ├── src/
│   │   ├── views/              # 페이지 컴포넌트
│   │   ├── components/         # 재사용 컴포넌트
│   │   ├── router/             # Vue Router
│   │   └── main.js
│   ├── Dockerfile
│   └── package.json
│
├── transaction-kafka-producer/ # 거래 데이터 수집기
│   ├── main.py                 # Producer 메인
│   ├── fetchers/               # API 호출 로직
│   │   ├── apartment_trade.py
│   │   ├── apartment_rent.py
│   │   ├── house_multi_trade.py
│   │   ├── officetel_trade.py
│   │   └── commercial_trade.py
│   ├── messaging/              # Kafka Producer
│   └── state/                  # 체크포인트 관리
│
├── flink/                      # Apache Flink Job
│   ├── job/
│   │   ├── transaction-job.py  # 메인 스트림 처리 로직
│   │   └── sinks.py            # Elasticsearch Sink
│   ├── config.py               # Flink 설정
│   ├── Dockerfile
│   └── requirements.txt
│
├── elasticsearch/              # ES 템플릿
│   └── realestate_current_template.json
│
├── kafka/                      # Kafka 설정
│   └── config/
│       └── server.properties
│
└── geo-enricher/               # 좌표 보강 서비스
    ├── main.py
    └── Dockerfile
```

### 5.2 환경 변수 (.env)

프로젝트 루트에 `.env` 파일 생성:

```bash
# Database
DB_NAME=homepick_db
DB_USER=homepick_user
DB_PASSWORD=your_secure_password

# Django
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
KAKAO_REST_API_KEY=your_kakao_rest_api_key
VUE_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Public Data API
PUBLIC_DATA_API_KEY=your_public_data_portal_api_key

# Frontend
FRONTEND_URL=http://localhost:8080
KAKAO_REDIRECT_URI=http://localhost:8000/api/v1/auth/social/login/kakao/callback/

# Kafka
KAFKA_BROKERS=kafka:9092

# Elasticsearch
ES_HOST=http://elasticsearch:9200
```

---

## 6. 환경 구성 및 실행 방법

### 6.1 사전 요구사항

- Docker 20.10+
- Docker Compose 2.0+
- 최소 8GB RAM (권장 16GB)
- 최소 20GB 디스크 여유 공간

### 6.2 초기 실행 (Full Setup)

```bash
# 1. 레포지토리 클론
git clone <repository-url>
cd HomePick

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (API 키 등 입력)

# 3. 완전 초기화 (이전 데이터 삭제)
make reset

# 4. Docker 이미지 빌드
make build

# 5. 전체 서비스 시작
make up

# 6. Elasticsearch 템플릿 적용
make es-template-current

# 7. Kafka 토픽 생성
make topics-create

# 8. Flink Job 실행
make run-flink

# 9. Kafka Producer 시작 (거래 데이터 수집)
make run-transaction-producer
```

### 6.3 서비스 확인

**웹 브라우저에서 접속:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Flink Dashboard: http://localhost:8081
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

**서비스 상태 확인:**
```bash
# 컨테이너 상태
make ps

# 로그 확인
make logs                  # 전체 로그
make logs-flink           # Flink JobManager
make logs-kafka           # Kafka
make logs-producer        # Transaction Producer
```

### 6.4 개발 모드 실행 (코드 수정 후)

```bash
# 컨테이너 재시작
make restart

# Flink Job 재실행 (코드 변경 시)
make run-flink
```

### 6.5 데이터 초기화 (문제 발생 시)

```bash
# 컨테이너 + 볼륨 삭제 (데이터 완전 삭제)
make reset

# 컨테이너만 삭제 (볼륨 유지)
make clean

# 안 쓰는 이미지/캐시 정리
make prune

# Docker 완전 초기화 (⚠️ 주의)
make nuke
```

---

## 7. 웹 서비스 사용 방법

### 7.1 회원가입 및 로그인

**카카오 소셜 로그인:**
1. 홈페이지 접속 (http://localhost:8080)
2. "카카오 로그인" 버튼 클릭
3. 카카오 계정으로 인증
4. 자동으로 회원가입 및 로그인 완료

### 7.2 매물 검색

**기본 검색:**
1. 상단 검색창에 지역명 입력 (예: "강남구", "마포구")
2. 자동완성 목록에서 선택
3. 매물 목록 표시

**필터 적용:**
```
- 거래 유형: 매매 / 전세 / 월세
- 자산 유형: 아파트 / 다세대 / 오피스텔 / 상업용
- 가격 범위: 최소 ~ 최대
- 면적 범위: 최소 ~ 최대 (m²)
- 층수: 특정 층 선택
```

**정렬:**
- 최신순 (기본)
- 가격 낮은 순
- 가격 높은 순
- 면적 넓은 순

### 7.3 매물 상세 정보

**매물 카드 클릭 시 표시되는 정보:**
- 기본 정보 (주소, 면적, 층수, 건축년도)
- 거래 정보 (가격, 거래일, 거래 유형)
- 지도 위치 (구글 맵)
- 가격 변동 그래프 (이력이 있는 경우)
- 주변 편의시설

### 7.4 관심 매물 (찜)

1. 매물 상세 페이지에서 "하트" 아이콘 클릭
2. 상단 메뉴 > "관심 매물" 페이지에서 확인
3. 가격 변동 시 알림 수신 (추후 기능)

### 7.5 AI 챗봇 사용

**챗봇 시작:**
1. 하단 탭 > "챗봇" 아이콘 클릭
2. 대화창에 질문 입력

**질문 예시:**
```
- "강남구 아파트 시세 알려줘"
- "전세 보증금 1억 이하 매물 추천해줘"
- "역세권 오피스텔 찾아줘"
- "청약이 뭐야?"
- "전세자금대출 조건 알려줘"
```

**챗봇 기능:**
- 매물 추천
- 부동산 용어 설명
- 시세 정보 제공
- 거래 절차 안내

### 7.6 지도 기반 탐색

1. 상단 메뉴 > "지도" 클릭
2. 지도 이동 및 확대/축소
3. 매물 마커 클릭 → 간단 정보 팝업
4. "상세 보기" → 매물 상세 페이지로 이동

---

## 8. API 엔드포인트

### 8.1 인증 (Authentication)

**카카오 로그인:**
```http
GET /api/v1/auth/social/login/kakao/
```

**카카오 콜백:**
```http
GET /api/v1/auth/social/login/kakao/callback/
```

**토큰 갱신:**
```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

### 8.2 매물 검색 (Properties)

**매물 목록 조회:**
```http
GET /api/v1/properties/search/
Query Parameters:
  - asset_type: apartment|house|officetel|commercial
  - transaction_type: TRADE|RENT
  - sido: 시도명
  - sigungu: 시군구명
  - min_price: 최소 가격
  - max_price: 최대 가격
  - min_area: 최소 면적 (m²)
  - max_area: 최대 면적 (m²)
  - page: 페이지 번호
  - page_size: 페이지당 개수 (기본 20)

Response:
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/properties/search/?page=2",
  "previous": null,
  "results": [
    {
      "property_id": "abc123...",
      "address": {
        "sido": "서울특별시",
        "sigungu": "강남구",
        "umd": "역삼동",
        "display": "역삼동 타워팰리스 101동"
      },
      "transaction_type": "TRADE",
      "price": 3500000000,
      "area_sqm": 84.5,
      "floor": 15,
      "deal_date": "2025-12-15",
      "location": {
        "lat": 37.4979,
        "lon": 127.0276
      }
    }
  ]
}
```

**매물 상세 조회:**
```http
GET /api/v1/properties/{property_id}/

Response:
{
  "property_id": "abc123...",
  "current_state": { ... },
  "history": [
    {
      "event_type": "PRICE_CHANGE",
      "event_time": "2025-12-10T10:00:00Z",
      "old_price": 3600000000,
      "new_price": 3500000000
    }
  ]
}
```

### 8.3 지도 (Map)

**지역 좌표 변환:**
```http
GET /api/v1/map/geocode/
Query Parameters:
  - address: 주소 문자열

Response:
{
  "lat": 37.4979,
  "lon": 127.0276,
  "formatted_address": "서울특별시 강남구 역삼동"
}
```

### 8.4 챗봇 (Chatbot)

**대화 요청:**
```http
POST /api/v1/chatbot/chat/
Content-Type: application/json
Authorization: Bearer your_access_token

{
  "message": "강남구 아파트 시세 알려줘"
}

Response:
{
  "response": "강남구 아파트 평균 시세는...",
  "suggested_properties": [
    {
      "property_id": "...",
      "address": "...",
      "price": 3500000000
    }
  ]
}
```

### 8.5 관심 매물 (Favorites)

**관심 매물 추가:**
```http
POST /api/v1/favorites/
Content-Type: application/json
Authorization: Bearer your_access_token

{
  "property_id": "abc123..."
}
```

**관심 매물 목록:**
```http
GET /api/v1/favorites/
Authorization: Bearer your_access_token
```

**관심 매물 삭제:**
```http
DELETE /api/v1/favorites/{property_id}/
Authorization: Bearer your_access_token
```

---

## 9. 개발 가이드

### 9.1 Backend 개발

**새로운 앱 추가:**
```bash
docker compose exec web python manage.py startapp myapp
```

**마이그레이션:**
```bash
# 마이그레이션 파일 생성
docker compose exec web python manage.py makemigrations

# 마이그레이션 적용
docker compose exec web python manage.py migrate
```

**슈퍼유저 생성:**
```bash
docker compose exec web python manage.py createsuperuser
```

**Django Shell:**
```bash
docker compose exec web python manage.py shell
```

### 9.2 Frontend 개발

**패키지 설치:**
```bash
docker compose exec frontend npm install package-name
```

**빌드:**
```bash
docker compose exec frontend npm run build
```

**Lint:**
```bash
docker compose exec frontend npm run lint
```

### 9.3 Flink Job 개발

**로컬 테스트:**
```python
# flink/job/test_transaction_job.py
from transaction_job import parse_transaction

def test_parse():
    raw = '{"dealAmount": "1,000", ...}'
    result = parse_transaction(raw)
    assert result['price'] == 1000
```

**Job 재배포:**
```bash
# 1. 코드 수정
vim flink/job/transaction-job.py

# 2. Flink Job 재실행
make run-flink
```

**체크포인트 확인:**
```bash
# Flink 볼륨에 저장됨
docker compose exec flink-jobmanager ls -la /opt/flink/checkpoints
```

### 9.4 Kafka 토픽 관리

**토픽 생성:**
```bash
docker compose exec kafka kafka-topics.sh \
  --create \
  --topic my.new.topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

**토픽 목록:**
```bash
make topics-list
```

**메시지 확인 (Consumer):**
```bash
docker compose exec kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic apartment.trade \
  --from-beginning \
  --max-messages 10
```

### 9.5 Elasticsearch 쿼리

**인덱스 조회:**
```bash
curl -X GET "http://localhost:9200/_cat/indices?v"
```

**매물 검색 예시:**
```bash
curl -X GET "http://localhost:9200/realestate_current_apartment/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"match": {"address.sigungu": "강남구"}},
          {"range": {"price": {"gte": 1000000000, "lte": 5000000000}}}
        ]
      }
    },
    "sort": [{"deal_date": {"order": "desc"}}]
  }'
```

---

## 10. 트러블슈팅

### 10.1 Kafka 연결 오류

**증상:**
```
Failed to connect to Kafka broker
```

**해결 방법:**
```bash
# 1. Kafka 상태 확인
docker compose ps kafka zookeeper

# 2. Kafka 로그 확인
make logs-kafka

# 3. Kafka 재시작
docker compose restart kafka

# 4. 토픽 존재 확인
make topics-list
```

### 10.2 Flink Job 실패

**증상:**
```
Job execution failed
```

**해결 방법:**
```bash
# 1. Flink JobManager 로그 확인
make logs-flink

# 2. TaskManager 로그 확인
docker compose logs flink-taskmanager

# 3. 체크포인트 초기화 (필요시)
docker compose down
docker volume rm homepick_flink_checkpoints
make up
make run-flink
```

### 10.3 Elasticsearch 인덱싱 오류

**증상:**
```
Mapping conflict or type mismatch
```

**해결 방법:**
```bash
# 1. 인덱스 삭제
curl -X DELETE "http://localhost:9200/realestate_current_*"

# 2. 템플릿 재적용
make es-template-current

# 3. Flink Job 재시작
make run-flink
```

### 10.4 Django Database 마이그레이션 오류

**증상:**
```
django.db.utils.ProgrammingError: relation does not exist
```

**해결 방법:**
```bash
# 1. 마이그레이션 상태 확인
docker compose exec web python manage.py showmigrations

# 2. 마이그레이션 재실행
docker compose exec web python manage.py migrate --fake-initial

# 3. 데이터베이스 초기화 (필요시)
make reset
docker compose up -d db web
docker compose exec web python manage.py migrate
```

### 10.5 Frontend CORS 오류

**증상:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**해결 방법:**
```python
# backend/core/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
CORS_ALLOW_CREDENTIALS = True
```

### 10.6 메모리 부족

**증상:**
```
Container exited with code 137 (OOM Killed)
```

**해결 방법:**
```yaml
# docker-compose.yml에 메모리 제한 완화
services:
  flink-jobmanager:
    environment:
      - jobmanager.memory.process.size: 2048m  # 1024m → 2048m
  
  flink-taskmanager:
    environment:
      - taskmanager.memory.process.size: 2048m  # 1024m → 2048m
```

---

## 부록 A: Makefile 명령어 요약

```bash
# 기본 실행
make up                     # 전체 서비스 시작
make down                   # 전체 서비스 종료
make restart                # 재시작
make ps                     # 컨테이너 상태

# 빌드
make build                  # Docker 이미지 빌드
make rebuild                # 캐시 없이 전체 빌드

# 초기화
make reset                  # 컨테이너 + 볼륨 삭제
make clean                  # 컨테이너만 삭제
make prune                  # 안 쓰는 리소스 정리
make nuke                   # Docker 완전 초기화 (⚠️)

# Elasticsearch
make es-template-current    # 인덱스 템플릿 적용
make es-template-check      # 템플릿 확인

# Kafka
make topics-create          # 토픽 생성
make topics-list            # 토픽 목록

# Flink
make run-flink              # Flink Job 실행
make logs-flink             # Flink 로그

# Producer
make run-transaction-producer  # 거래 데이터 수집 시작
make logs-producer             # Producer 로그

# 로그
make logs                   # 전체 로그
make logs-kafka             # Kafka 로그
```

---

## 부록 B: 환경별 설정

### B.1 개발 환경 (로컬)

- Docker Compose 사용
- 볼륨 마운트로 코드 변경 자동 반영
- DEBUG=True
- 모든 포트 외부 노출

### B.2 스테이징 환경

- 동일한 docker-compose.yml 사용
- 환경변수만 변경 (.env.staging)
- HTTPS 적용 (Let's Encrypt)
- Nginx 리버스 프록시

### B.3 프로덕션 환경

**권장 구성:**
- Kubernetes 또는 AWS ECS
- Managed Kafka (AWS MSK, Confluent Cloud)
- Managed Elasticsearch (AWS OpenSearch)
- RDS PostgreSQL
- CloudFront + S3 (프론트엔드)
- 모니터링: Prometheus + Grafana
- 로깅: ELK Stack 또는 CloudWatch

---

## 부록 C: 성능 최적화

### C.1 Flink 최적화

```python
# Checkpoint 간격 조정
env.enable_checkpointing(60000)  # 1분

# Parallelism 설정
env.set_parallelism(4)

# State Backend: RocksDB (대용량)
env.set_state_backend(RocksDBStateBackend(...))
```

### C.2 Elasticsearch 최적화

```json
{
  "index": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "refresh_interval": "30s"
  }
}
```

### C.3 Django 최적화

```python
# 캐싱
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# 데이터베이스 쿼리 최적화
properties = Property.objects.select_related('owner').prefetch_related('images')
```

---

## 참고 자료

- [Apache Flink 공식 문서](https://flink.apache.org/docs/)
- [Kafka 공식 문서](https://kafka.apache.org/documentation/)
- [Elasticsearch 가이드](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js 3 가이드](https://vuejs.org/guide/)
- [공공데이터 포털](https://www.data.go.kr/)

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

---

**작성일:** 2025년 12월 26일  
**버전:** 1.0.0
