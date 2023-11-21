import dotenv
from backend.etl.databases.cassandra.cassandra_conn import CassandraConn
from cassandra.cqlengine import management
# Table models
from backend.etl.databases.cassandra.table_models import (
    Users, JobListings, ClicksMetadata, SearchMetadata
)


class SetupDB(CassandraConn):
    # load environment variables from .env file
    dotenv.load_dotenv(dotenv_path="./config/.env")

    def setup_keyspace(self):
        # create keyspace
        management.create_keyspace_simple(
            self.keyspace_name,
            replication_factor=1,
            durable_writes=True,
            connections=[self.session_name]
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

        self.close_conn()

    def clean_keyspace(self):
        try:
            management.drop_table(Users)
            management.drop_table(JobListings)
            management.drop_table(SearchMetadata)
            management.drop_table(ClicksMetadata)
        except:
            pass


if __name__ == "__main__":
    setup = SetupDB()
    setup.clean_keyspace()
    setup.setup_keyspace()
