FROM flink:1.18.1-scala_2.12-java11

USER root

# Python + pip + curl
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    openjdk-11-jdk-headless \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# 🔥 pemja 스킵 (절대 위치 중요)
ENV FLINK_PYTHON_REQUIREMENTS_SKIP_PEMJA=1

# pemja 빌드가 기대하는 경로에 JDK 헤더 심볼릭 링크 생성 (arm64 기준 경로 고정)
RUN mkdir -p /opt/java && \
    rm -rf /opt/java/openjdk && \
    ln -s /usr/lib/jvm/java-11-openjdk-arm64 /opt/java/openjdk

# Python 패키지 설치 (PyFlink 포함)
COPY requirements.txt /opt/flink/requirements.txt
RUN python -m pip install --no-cache-dir \
    apache-flink==1.18.1 \
    -r /opt/flink/requirements.txt \
    google \
    grpcio==1.59.3 \
    grpcio-tools==1.59.3

# Flink Kafka Connector (1.18 대응)
RUN curl -fSL \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.0.1-1.18/flink-connector-kafka-3.0.1-1.18.jar \
    -o /opt/flink/lib/flink-connector-kafka.jar

# Kafka Client (OffsetResetStrategy 포함)
RUN curl -fSL \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.1/kafka-clients-3.6.1.jar \
    -o /opt/flink/lib/kafka-clients.jar

# Flink Elasticsearch Connector (1.18 대응)
RUN curl -fSL \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-elasticsearch7/3.1.0-1.18/flink-connector-elasticsearch7-3.1.0-1.18.jar \
    -o /opt/flink/lib/flink-connector-elasticsearch7.jar

RUN chown flink:flink /opt/flink/lib/*.jar
USER flink
