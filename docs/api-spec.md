# 📑 API 명세서 (Draft)
## 1. 매물 및 실거래가 조회 (지도/목록)
| 기능 | Method | Endpoint | 설명 |
| - | - | - | - |
| 지도 범위 내 매물 조회 | `GET` | `/api/map/search` | 특정 좌표 범위(bbox) 내 최신 실거래가 마커 목록 조회 (ES current 인덱스 활용) |
| 단지 상세 정보 조회 | `GET` | `/api/v1/properties/{property_id}` | 특정 아파트/빌라의 기본 정보 및 현재 최신 실거래 상태 조회 |
## 2. 히스토리 및 분석 (Flink 생성 데이터)
| 기능 | Method | Endpoint | 설명 |
| - | - | - | - |
| 실거래가 변동 이력 | `GET` | `/api/v1/properties/{property_id}/history` | 해당 매물의 가격 변동 타임라인 조회 (ES history 인덱스 기반) |
## 3. 민간 매물 연동 (직방 실시간 수집)
| 기능 | Method | Endpoint | 설명 |
| - | - | - | - |
| 실시간 매물 목록 | `GET` | `/api/v1/properties/{property_id}/listings` | 실거래 데이터와 매칭된 현재 판매 중인 매물(직방) 리스트 |
## 4. 인텔리전스 서비스 (AI 챗봇)
| 기능 | Method | Endpoint | 설명 |
| - | - | - | - |
| 부동산 질의응답 | `POST` | `/api/v1/chatbot` | 실거래 데이터 기반 RAG 챗봇 질의 (서울/경기 특화) |