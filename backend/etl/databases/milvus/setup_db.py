import os
import dotenv
import yaml
from pymilvus import connections, db, Collection
from backend.etl.databases.milvus.table_models import (
    collection_name,
    database_name,
    schema
)


class SetupDB():
    def __init__(self):
        # load environment variables from .env file
        dotenv.load_dotenv(dotenv_path="./config/.env")

        # load configuration from config.yaml
        with open("./config/config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.username = self.config["database"]["milvus"]["username"]
        self.password = str(os.getenv('MILVUS_PASSWORD'))
        self.host = self.config["database"]["milvus"]["host"]
        self.port = self.config["database"]["milvus"]["port"]
        self.database_name =\
            self.config["database"]["milvus"]["database"]
        self.collection_name =\
            self.config["database"]["milvus"]["collection"]

        # connect to milvus
        self.session = connections.connect(
            alias='default',
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password
        )

    def setup_database(self):
        # create database
        db.create_database(self.database_name)

        # create collection
        Collection(
            name=collection_name,
            schema=schema,
            using=database_name,
        )

    def clean_database(self):
        db.drop_database(self.database_name)
