from pymilvus import CollectionSchema, FieldSchema, DataType
import yaml

# load configuration from config.yaml
with open("./config/config.yaml", "r") as stream:
    config = yaml.safe_load(stream)

collection_name = config["database"]["milvus"]["collection"]

# define fields
uuid = FieldSchema(
    name="uuid",
    dtype=DataType.VARCHAR,
    max_length=36,
    description="Job UUID",
    is_primary=True
)

embedding = FieldSchema(
    name="embedding",
    dtype=DataType.FLOAT_VECTOR,
    description="Job Embedding",
    dim=768
)

# create schema
schema = CollectionSchema(
    fields=[
        uuid,
        embedding
    ],
    description="Jobs embedding collection schema",
    enable_dynamic_field=True
)
