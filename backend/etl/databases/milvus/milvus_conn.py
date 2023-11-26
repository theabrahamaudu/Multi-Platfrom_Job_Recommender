import os
import dotenv
import yaml
from pymilvus import connections


class MilvusConn:
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