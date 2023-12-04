from typing import List, Sequence
from pydantic import BaseModel


class JobEmbedding(BaseModel):
    uuid: str
    embedding: List[Sequence[float]]
