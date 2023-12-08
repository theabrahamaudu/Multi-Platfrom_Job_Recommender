"""
Module for setting up the keyspace and tables in the Cassandra database.
"""
from venv import logger
import dotenv
from etl.databases.cassandra.cassandra_conn import CassandraConn
from cassandra.cqlengine import management
# Table models
from etl.databases.cassandra.table_models import (
    Users, JobListings, ClicksMetadata, SearchMetadata
)


class SetupDB(CassandraConn):
    """
    Handles setting up the keyspace and tables in the database.

    Methods:
    - setup_keyspace(): Creates the keyspace and necessary tables.
    - clean_keyspace(): Drops existing tables from the keyspace if they exist.
    """
    # load environment variables from .env file
    dotenv.load_dotenv(dotenv_path="./config/.env")

    def setup_keyspace(self):
        """
        Creates the keyspace and necessary tables.

        Creates keyspace with replication factor 1 and durable writes.
        Then creates `users`, `job_listings`, `search_metadata`,
        and `clicks_metadata` tables.
        """
        # create keyspace
        try:
            management.create_keyspace_simple(
                self.keyspace_name,
                replication_factor=1,
                durable_writes=True,
                connections=[self.session_name]
            )
            logger.info(f"Created keyspace: {self.keyspace_name}")
        except Exception as e:
            logger.error(f"Error creating keyspace: {e}")

        try:
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
            logger.info("Created tables")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")

    def clean_keyspace(self):
        """
        Drops existing tables from the keyspace if they exist.

        Drops `users`, `job_listings`, `search_metadata`, and
        `clicks_metadata` tables.
        """
        # drop tables from keyspace if they exist
        try:
            management.drop_table(Users)
            management.drop_table(JobListings)
            management.drop_table(SearchMetadata)
            management.drop_table(ClicksMetadata)
            logger.info("Dropped tables")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")


if __name__ == "__main__":
    setup = SetupDB()
    setup.clean_keyspace()
    setup.setup_keyspace()
