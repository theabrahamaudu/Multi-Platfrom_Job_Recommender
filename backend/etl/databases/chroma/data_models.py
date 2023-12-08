"""
This module contains the data models for the ChromaDB.
"""

from typing import List, Sequence
from pydantic import BaseModel


class JobEmbedding(BaseModel):
    """
    Represents the embedding of a job.

    Attributes:
    - uuid (str): The unique identifier for the job.
    - embedding (List[Sequence[float]]): List of float sequences
      representing the job embedding.
    """
    uuid: str
    embedding: List[Sequence[float]]
