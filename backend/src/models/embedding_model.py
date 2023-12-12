"""
This module contains the embedding model for the core
recommender engine.

Uses stock sentence-transformers for now, but can be
replaced with any other embedding model.
"""

from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    './models/sentence-transformers/all-mpnet-base-v2'
)
