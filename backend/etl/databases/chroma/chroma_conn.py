"""
This module manages connections to the Chroma database.
"""

import os
import dotenv
import yaml
from chromadb import HttpClient
from chromadb.config import Settings
from etl.transform.vectorizer import Embed
from src.utils.pipeline_log_config import pipeline as logger


class ChromaConn:
    """
    Manages connections to the Chroma database.

    Attributes:
    - username (str): The username used for database authentication.
    - password (str): The password associated with the username for
      database authentication.
    - host (str): The hostname or IP address of the Chroma database.
    - port (int): The port number used for database communication.
    - collection_name (str): The name of the collection in the Chroma database.
    - embedding_function (Embed): The embedding function
      associated with Chroma.
    - session (HttpClient): The HTTP client session used for
      connecting to Chroma.
    """
    def __init__(self):
        # load environment variables from .env file
        dotenv.load_dotenv(dotenv_path="./config/.env")

        # load configuration from config.yaml
        with open("./config/config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error("Error loading config file: %s", exc)

        # set credentials
        self.username = self.config["database"]["chroma"]["username"]
        self.password = str(os.getenv('CHROMA_PASSWORD'))
        self.host = self.config["database"]["chroma"]["host"]
        self.port = self.config["database"]["chroma"]["port"]
        self.collection_name =\
            self.config["database"]["chroma"]["collection"]

        # set embedding function
        self.embedding_function = Embed()

        # connect to chroma
        try:
            self.session = HttpClient(
                host=self.host,
                port=self.port,
                settings=Settings(
                    chroma_client_auth_provider="basic",
                    chroma_client_auth_credentials=f"{self.username}:{self.password}" # noqa E501
                )
            )
            logger.info("Connected to Chroma")
        except Exception as e:
            logger.error("Error connecting to Chroma: %s", e)
