"""
This module contains the SetupDB class, which manages setup and
cleaning operations for the Chroma database.
"""

from etl.databases.chroma.chroma_conn import ChromaConn
from src.utils.pipeline_log_config import pipeline as logger


class SetupDB(ChromaConn):
    """
    Manages setup and cleaning operations for the Chroma database.

    Inherits from ChromaConn, providing the ability to interact with Chroma.

    Methods:
    - setup_database(): Creates a new collection within the Chroma database.
    - clean_database(): Deletes all collections within the Chroma database.
    """
    def __init__(self):
        # Initialize Chroma connection
        ChromaConn.__init__(self)

    def setup_database(self):
        """
        Creates a new collection within the Chroma database.
        """
        try:
            # create new collection
            self.collection = self.session.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
            logger.info(
                "Created new Chroma collection >>> %s",
                self.collection_name
            )
        except Exception as e:
            logger.error("Error creating Chroma collection: %s", e)

    def clean_database(self):
        """
        Deletes all collections within the Chroma database.
        """
        try:
            # delete all collections
            for collection in self.session.list_collections():
                self.session.delete_collection(collection.name)
            logger.info("Deleted all Chroma collections")
        except Exception as e:
            logger.error("Error deleting Chroma collections: %s", e)


if __name__ == "__main__":
    setup_db = SetupDB()
    setup_db.clean_database()
    setup_db.setup_database()
