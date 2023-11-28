from typing import List
from pydantic import BaseModel


class JobEmbedding(BaseModel):
    uuid: str
    embedding: List[float]
