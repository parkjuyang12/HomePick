# HomePick/kafka/Dockerfile
# Kafka base image for local deployments. Compose will supply env vars.
# Bitnami base image (use a broadly available tag to avoid pull failures).
FROM bitnami/kafka:latest

# Optional custom server configs. Extend or override as needed before build.
COPY config/server.properties /opt/bitnami/kafka/config/server.properties
