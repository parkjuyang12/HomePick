## 구조 정의

| 역할            | 정체성              |
| ------------- | ---------------- |
| Flink Cluster | **플랫폼 / 실행 환경**  |
| Flink Job     | **비즈니스 로직 (코드)** |

## 해당 구조로 나누는 이유

### 생명주기의 차이
| 항목    | Cluster | Job   |
| ----- | ------- | ----- |
| 실행 시점 | 항상      | 필요할 때 |
| 수정 빈도 | 거의 없음   | 매우 잦음 |
| 책임    | 실행      | 처리    |

👉 같이 두면:
- job 코드 바꿀 때마다 Flink 클러스터 이미지 재빌드 필요

### python 의존성 문제
- PyFlink Job은:
    - apache-flink
    - confluent-kafka
    - elasticsearch
이런 걸 필요로 함.

- Flink Cluster는:
    - Java
    - JVM
설정만 필요


## 컨테이너 분리
#### JobManager
- Job을 받아서 실행 계획(DAG) 만들고 
TaskManager에게 일 분배

    👉 “관리자”

#### TaskManager
- 실제 데이터 처리
CPU / 메모리 / 슬롯 보유

    👉 “일꾼”

#### Job
- PyFlink
Kafka 읽고, 처리하고, 쓰는 로직

    👉 “업무 지시서”

# =====================

## Flink 처리 흐름
```
Kafka (거래 이벤트)
        │
        ▼
Parse (JSON)
        │
        ▼
Map: 거래 → (property_id 생성)
        │
        ▼
keyBy(property_id)
        │
        ├─▶ current_property_stream  (UPDATE)
        │
        └─▶ trade_history_stream     (APPEND)
```