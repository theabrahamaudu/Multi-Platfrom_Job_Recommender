import os
import dotenv
import yaml
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.metadata import Metadata
from cassandra.cqlengine import management

# Table models
from backend.etl.databases.cassandra.table_models import (
    Users, JobListings, ClicksMetadata, SearchMetadata
)


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

        self.cluster = Cluster(
            port=29042,
            auth_provider=PlainTextAuthProvider(
                username=self.username,
                password=self.password
            )
        )
        self.session = self.cluster.connect()

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

    def setup_keyspace(self):

        # create keyspace
        management.create_keyspace_simple(
            self.keyspace_name,
            replication_factor=1,
            durable_writes=True,
            connections=self.cluster
        )

        # create `users` table
        management.sync_table(
            model=Users
        )

        # create `job_listings` table
        management.sync_table(
            model=JobListings
        )

        # create `search_metadata` table
        management.sync_table(
            model=SearchMetadata
        )

        # create `clicks_metadata` table
        management.sync_table(
            model=ClicksMetadata
        )
