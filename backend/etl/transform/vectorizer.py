"""
This module contains scripts to vectorize data and an interface
to the embedding model for ChromaDB
"""

from src.models.embedding_model import model
from chromadb import Documents, EmbeddingFunction, Embeddings


class Embed(EmbeddingFunction):
    """
    Interface to the embedding model for ChromaDB.

    This class acts as an interface to an embedding model within ChromaDB.
    It implements a `__call__` method
    to generate embeddings for a list of input documents.

    Args:
    - input (Documents): Input documents to be embedded.

    Returns:
    - Embeddings: Embeddings generated for the input documents.

    Example:
        embed_fn = Embed()

        documents = ["text1", "text2", ...]  # List of input documents

        embeddings = embed_fn(documents)

        Generates embeddings for the input documents using
        the embedding model in ChromaDB.
    """
    def __call__(self, input: Documents) -> Embeddings:
        """
        Generates embeddings for input documents using
        the embedding model from `src.models.embedding_model` in ChromaDB.

        Args:
        - input (Documents): Input documents to be embedded.

        Returns:
        - Embeddings: Embeddings generated for the input documents.
        """
        return model.encode(  # type: ignore
            list(input),
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()  # type: ignore


def vectorize(input: str | dict[str, str] | list[dict[str, str]]) -> Embeddings:  # noqa E501
    """
    Abstraction to simplify the application of the
    embedding module across the project.

    This function takes various input types and generates embeddings
    using an embedding module.
    It handles three types of input:
    1. Single text (string).
    2. Dictionary of texts (Job class-like object).
    3. List of dictionaries (Job class-like objects).

    Args:
    - input (str | dict[str, str] | list[dict[str, str]]): Input data to be
      vectorized.

    Returns:
    - Embeddings: Embeddings generated for the input data.

    Raises:
    - ValueError: If the input type is not supported.

    Example:
        >> Vectorize a single string

        text = "Sample text"

        embeddings = vectorize(text)

        >> Vectorize a dictionary of texts (Job class-like object)

        job_data = {"field1": "text1", "field2": "text2", ...}

        embeddings = vectorize(job_data)

        >> Vectorize a list of dictionaries (Job class-like objects)

        jobs_list = [
            {"field1": "text1_1", "field2": "text1_2", ...},

            {"field1": "text2_1", "field2": "text2_2", ...},
            ...
        ]

        embeddings = vectorize(jobs_list)
    """
    match input:
        # single text
        case str():
            return Embed()([input])

        # dictionary of texts (Job class-like object)
        case dict():
            full_text = str()
            fields = list(input.keys())[1:]

            for field in fields:
                full_text += str(input[field]) + " "
            return Embed()([full_text])

        # list of dictionaries (Job class-like objects)
        case list():
            texts = list()
            for item in input:
                full_text = str()
                fields = list(item.keys())[1:]
                for field in fields:
                    full_text += str(item[field]) + " "
                texts.append(full_text)
            return Embed()(texts)

        # unsupported input
        case _:
            raise ValueError
