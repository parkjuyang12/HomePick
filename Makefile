# ================================
# HomePick Project Makefile
# ================================
# 목적:
# - 로컬 개발 환경을 한 번에 띄우기
# - 캐시 / 볼륨 / 이미지 완전 초기화
# - Flink Job 실행을 표준화
#
# 사용 가이드:
#
# ▶ 최초 실행 (완전 초기 상태)
#   make reset
#   make build
#   make up
#   make run-flink
#
# ▶ 코드만 수정 후 재실행
#   make up
#   make run-flink
#
# ▶ Docker 환경 꼬였을 때
#   make nuke
#
# ================================

PROJECT_NAME=homepick
ES_HOST ?= http://localhost:9200

.PHONY: help up down restart build rebuild logs ps \
        reset clean prune nuke \
        run-flink logs-flink logs-kafka logs-producer

# ------------------------
# 기본 도움말
# ------------------------
help:
	@echo "Available commands:"
	@echo ""
	@echo "▶ 기본 실행"
	@echo "  make up                     - 모든 컨테이너 실행"
	@echo "  make down                   - 컨테이너 종료"
	@echo "  make restart                - 컨테이너 재시작"
	@echo "  make ps                     - 컨테이너 상태 확인"
	@echo ""
	@echo "▶ 빌드"
	@echo "  make build                  - Docker 이미지 빌드"
	@echo "  make rebuild                - 캐시 없이 전체 빌드"
	@echo ""
	@echo "▶ 초기화 / 정리"
	@echo "  make reset                  - 컨테이너 + 볼륨 삭제 (데이터 초기화)"
	@echo "  make clean                  - 컨테이너만 삭제 (볼륨 유지)"
	@echo "  make prune                  - 안 쓰는 이미지/캐시 정리"
	@echo "  make nuke                   - Docker 완전 초기화 (⚠️ 위험)"
	@echo ""
	@echo "▶ ⚙️ Elasticsearch"
	@echo "  make es-template-current    - realestate_current_* 인덱스 템플릿 적용 (geo_point)"
	@echo "  make es-template-check      - 현재 적용된 ES 템플릿 확인"
	@echo ""
	@echo "▶ ⚙️ Kafka"
	@echo "  make topics-create          - Kafka 토픽 생성 (apartment/house/officetel/commercial)"
	@echo "  make topics-list            - Kafka 토픽 목록 조회"
	@echo "  make run-transaction-producer - 거래 데이터 Kafka Producer 실행"
	@echo "  make logs-kafka             - Kafka 로그 확인"
	@echo "  make logs-producer          - Kafka Producer 로그 확인"
	@echo ""
	@echo "▶ ⚙️ Flink"
	@echo "  make run-flink              - Flink Transaction Job 실행"
	@echo "  make logs-flink             - Flink JobManager 로그 확인"
	@echo ""
	@echo "▶ ✅ 권장 실행 순서 (데이터 파이프라인 초기 세팅)"
	@echo "  make reset"
	@echo "  make build"
	@echo "  make up"
	@echo "  make es-template-current"
	@echo "  make topics-create"
	@echo "  make run-flink"
	@echo "  make run-transaction-producer"

# ------------------------
# Docker Compose 제어
# ------------------------
up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d

ps:
	docker compose ps

log:
	docker compose logs -f

# ------------------------
# Build
# ------------------------
build:
	docker compose build

rebuild:
	docker compose build --no-cache

# ------------------------
# 정리 / 초기화
# ------------------------

# 컨테이너 + 볼륨 삭제 (데이터 초기화)
reset:
	docker compose down -v

# 컨테이너만 삭제 (볼륨 유지)
clean:
	docker compose down

# 안 쓰는 이미지 / 캐시 정리
prune:
	docker system prune -f

# ⚠️ 전부 삭제 (이미지, 볼륨, 캐시 포함)
# Docker 환경 꼬였을 때만 사용
nuke:
	docker compose down -v
	docker system prune -af
	docker volume prune -f

# ------------------------
# Flink
# ------------------------
# Flink Job 실행
run-flink:
	docker exec -it flink_jobmanager \
	/opt/flink/bin/flink run \
	-py /opt/flink/job/transaction-job.py

logs-flink:
	docker logs -f flink_jobmanager

# ------------------------
# Kafka
# ------------------------
topics-create:
	docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.apartment   --partitions 1 --replication-factor 1 || true
	docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.house       --partitions 1 --replication-factor 1 || true
	docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.officetel   --partitions 1 --replication-factor 1 || true
	docker exec kafka kafka-topics --bootstrap-server kafka:9092 --create --topic realestate.commercial  --partitions 1 --replication-factor 1 || true
topics-list:
	docker exec kafka kafka-topics --bootstrap-server kafka:9092 --list
run-transaction-producer:
	docker exec -it kafka_producer python /app/main.py
logs-kafka:
	docker logs -f kafka

logs-producer:
	docker logs -f kafka_producer

# ------------------------
# Elasticsearch
# ------------------------
.PHONY: es-template-current es-template-check

es-template-current:
	@echo "▶ Applying Elasticsearch index template (realestate_current_*)"
	curl -s -X PUT "$(ES_HOST)/_index_template/realestate_current_template" \
		-H "Content-Type: application/json" \
		-d @elasticsearch/realestate_current_template.json \
		| jq . || true

es-template-check:
	curl -s "$(ES_HOST)/_index_template/realestate_current_template" | jq . || true
