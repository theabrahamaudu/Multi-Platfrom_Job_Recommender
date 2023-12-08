"""
This module manages connections and configuration for interacting
with a Cassandra database.
"""

import os
import dotenv
import yaml
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.metadata import Metadata
from cassandra.cqlengine import connection
from cassandra.query import dict_factory
from src.utils.pipeline_log_config import pipeline as logger


class CassandraConn:
    """
    Manages connections and configuration for interacting
    with a Cassandra database.

    This class handles the initialization of connections to Cassandra database
    using provided configuration details. It sets up connections,
    registers sessions, and defines keyspace and
    table setups for subsequent operations.

    Attributes:
    - username (str): Username used for authentication.
    - password (str): Password used for authentication.
    - host (str): Hostname or IP address of the Cassandra database.
    - port (int): Port number for the Cassandra database connection.
    - session_name (str): Name of the Cassandra session.
    - keyspace_name (str): Name of the keyspace in the Cassandra database.
    - cluster (Cluster): Cassandra cluster instance.
    - session (Session): Cassandra session instance for executing queries.
    - users_table (str): Name of the users table in the keyspace.
    - jobs_table (str): Name of the jobs table in the keyspace.
    - search_table (str): Name of the search table in the keyspace.
    - clicks_table (str): Name of the clicks table in the keyspace.

    Methods:
    - __init__(): Initializes the CassandraConn object and sets up connections
      to the Cassandra database.
    - close_conn(): Closes the connection to Cassandra.
    - get_metadata(): Fetches metadata related to the Cassandra connection.


    Example usage:

    ```python
    cassandra = CassandraConn()
    # Access the initialized Cassandra session
    session = cassandra.session
    ```
    """
    def __init__(self):
        # load environment variables from .env file
        dotenv.load_dotenv(dotenv_path="./config/.env")

        # load configuration from config.yaml
        with open("./config/config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error("Error loading config.yaml: %s", exc)
        # set cassandra credentials
        self.username = self.config["database"]["cassandra"]["username"]
        self.password = os.getenv('CASSANDRA_PASSWORD')
        self.host = self.config["database"]["cassandra"]["host"]
        self.port = self.config["database"]["cassandra"]["port"]
        self.session_name =\
            self.config["database"]["cassandra"]["session_name"]
        self.keyspace_name =\
            self.config["database"]["cassandra"]["keyspace"]

        # connect to cassandra
        try:
            self.cluster = Cluster(
                port=self.port,
                auth_provider=PlainTextAuthProvider(
                    username=self.username,
                    password=self.password
                )
            )
            self.session = self.cluster.connect(self.keyspace_name)

            # set row factory
            self.session.row_factory = dict_factory

            # add conncection to connection registry
            connection.set_session(self.session)
            connection.register_connection(
                self.session_name,
                session=self.session,
            )
            logger.info("Cassandra connection established.")
        except Exception as e:
            logger.error("Error connecting to Cassandra: %s", e)

        # keyspace and tables setup
        self.keyspace_name =\
            self.config["database"]["cassandra"]["keyspace"]
        self.users_table =\
            self.config["database"]["cassandra"]["tables"]["users"]
        self.jobs_table =\
            self.config["database"]["cassandra"]["tables"]["jobs"]
        self.search_table =\
            self.config["database"]["cassandra"]["tables"]["search"]
        self.clicks_table =\
            self.config["database"]["cassandra"]["tables"]["clicks"]

    def close_conn(self):
        """
        Closes the connection to Cassandra.
        """
        self.cluster.shutdown()

    def get_metadata(self):
        """
        Fetches metadata related to the Cassandra connection.

        Returns:
        - Metadata: Metadata related to the Cassandra connection.
        """
        return Metadata()
