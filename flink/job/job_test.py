from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

source = KafkaSource.builder() \
    .set_bootstrap_servers("kafka:9092") \
    .set_topics("raw.listing") \
    .set_group_id("pyflink-minimal") \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

ds = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    "Kafka Source"
)

ds.print()

env.execute("pyflink-minimal-test")
