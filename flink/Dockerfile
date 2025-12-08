# HomePick/flink/Dockerfile
# Flink base image for local JobManager/TaskManager.
FROM flink:1.17.2-scala_2.12-java11

WORKDIR /opt/flink

# 기본 설정 복사. 필요 시 compose 환경변수로 덮어쓰기 가능.
COPY conf/flink-conf.yaml /opt/flink/conf/flink-conf.yaml
COPY conf/log4j-console.properties /opt/flink/conf/log4j-console.properties
