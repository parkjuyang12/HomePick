FROM flink:1.18.1-scala_2.12-java11

USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Flink Kafka Connector (1.18 대응)
RUN curl -fSL \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.0.1-1.18/flink-connector-kafka-3.0.1-1.18.jar \
    -o /opt/flink/lib/flink-connector-kafka.jar

# Kafka Client (OffsetResetStrategy 포함)
RUN curl -fSL \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.1/kafka-clients-3.6.1.jar \
    -o /opt/flink/lib/kafka-clients.jar

RUN chown flink:flink /opt/flink/lib/*.jar
USER flink
