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

.PHONY: help up down restart build rebuild logs ps \
        reset clean prune nuke \
        run-flink logs-flink logs-kafka logs-producer

# ------------------------
# 기본 도움말
# ------------------------
help:
	@echo "Available commands:"
	@echo "  make up           - 모든 컨테이너 실행"
	@echo "  make down         - 컨테이너 종료"
	@echo "  make build        - 이미지 빌드"
	@echo "  make rebuild      - 캐시 없이 전체 빌드"
	@echo "  make reset        - 컨테이너 + 볼륨 삭제"
	@echo "  make clean        - 컨테이너만 삭제"
	@echo "  make prune        - 안 쓰는 이미지/캐시 정리"
	@echo "  make nuke         - Docker 완전 초기화 (위험)"
	@echo "  make run-flink    - Flink Job 실행"
	@echo "  make logs-flink   - Flink JobManager 로그"
	@echo "  make logs-kafka   - Kafka 로그"

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
	-py /opt/flink/job/job_test.py

logs-flink:
	docker logs -f flink_jobmanager

# ------------------------
# Kafka
# ------------------------
logs-kafka:
	docker logs -f kafka

logs-producer:
	docker logs -f kafka_producer
