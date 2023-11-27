import os
import dotenv
import yaml
from pymilvus import connections, db, Collection
from backend.etl.databases.milvus.table_models import (
    collection_name,
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
        self.session_name =\
            self.config["database"]["milvus"]["session_name"]
        self.database_name =\
            self.config["database"]["milvus"]["database"]
        self.collection_name =\
            self.config["database"]["milvus"]["collection"]

        # connect to milvus default database
        self.session = connections.connect(
            alias=self.session_name,
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password
        )

    def setup_database(self):
        # create new database
        db.create_database(
            db_name=self.database_name,
            using=self.session_name
        )

        # reconnect to milvus with new database
        self.session = connections.connect(
            alias=self.session_name,
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            db_name=self.database_name
        )

        # create collection
        collection = Collection(
            name=collection_name,
            schema=schema,
            using=self.session_name,
            db_name=self.database_name,
            consistency_level="Strong"
        )
        print(collection.schema)

    def clean_database(self):
        db.drop_database(
            db_name=self.database_name,
            using=self.session_name
        )

    def close_conn(self):
        connections.disconnect(self.session_name)


if __name__ == "__main__":
    setup_db = SetupDB()
    setup_db.clean_database()
    setup_db.setup_database()
    setup_db.close_conn()
