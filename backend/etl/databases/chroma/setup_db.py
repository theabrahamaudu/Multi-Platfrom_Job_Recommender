from etl.databases.chroma.chroma_conn import ChromaConn


class SetupDB(ChromaConn):
    def __init__(self):
        # Initialize Chroma connection
        ChromaConn.__init__(self)

    def setup_database(self):
        # create new collection
        self.collection = self.session.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
        )

    def clean_database(self):
        try:
            for collection in self.session.list_collections():
                self.session.delete_collection(collection.name)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    setup_db = SetupDB()
    setup_db.clean_database()
    setup_db.setup_database()
