import os
import dotenv
import yaml
from chromadb import HttpClient
from chromadb.config import Settings
from etl.transform.vectorizer import Embed


class ChromaConn:
    def __init__(self):
        # load environment variables from .env file
        dotenv.load_dotenv(dotenv_path="./config/.env")

        # load configuration from config.yaml
        with open("./config/config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.username = self.config["database"]["chroma"]["username"]
        self.password = str(os.getenv('CHROMA_PASSWORD'))
        self.host = self.config["database"]["chroma"]["host"]
        self.port = self.config["database"]["chroma"]["port"]
        self.collection_name =\
            self.config["database"]["chroma"]["collection"]

        # set embedding function
        self.embedding_function = Embed()

        # connect to chroma
        self.session = HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(
                chroma_client_auth_provider="basic",
                chroma_client_auth_credentials=f"{self.username}:{self.password}" # noqa E501
            )
        )
