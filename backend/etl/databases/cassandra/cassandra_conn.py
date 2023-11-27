import os
import dotenv
import yaml
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.metadata import Metadata
from cassandra.cqlengine import connection
from cassandra.query import dict_factory


class CassandraConn:
    def __init__(self):
        # load environment variables from .env file
        dotenv.load_dotenv(dotenv_path="./config/.env")

        # load configuration from config.yaml
        with open("./config/config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.username = self.config["database"]["cassandra"]["username"]
        self.password = os.getenv('CASSANDRA_PASSWORD')
        self.host = self.config["database"]["cassandra"]["host"]
        self.port = self.config["database"]["cassandra"]["port"]
        self.session_name =\
            self.config["database"]["cassandra"]["session_name"]
        self.keyspace_name =\
            self.config["database"]["cassandra"]["keyspace"]

        # connect to cassandra
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

        connection.set_session(self.session)
        connection.register_connection(
            self.session_name,
            session=self.session,
        )

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
        self.cluster.shutdown()

    def get_metadata(self):
        return Metadata()
