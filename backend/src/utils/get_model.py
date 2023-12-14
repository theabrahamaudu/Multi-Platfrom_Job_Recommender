"""
This script is used to get the embedding model if it is not
already loaded from huggingface hub.
"""

import os
from transformers import AutoModel


def get_model():
    """
    This function is used to get the embedding model if it is not
    already loaded from huggingface hub.
    """
    model_dir = "./models/"
    model_name = "sentence-transformers/all-mpnet-base-v2"

    if not os.path.exists(
       os.path.join(model_dir, model_name)
       ):
        print("Downloading model...")
        # download model
        model = AutoModel.from_pretrained(
            "sentence-transformers/all-mpnet-base-v2",
        )
        # save model
        model.save_pretrained(
            "./models/sentence-transformers/all-mpnet-base-v2")
        print(f"Model downloaded and saved to {model_dir + model_name}")
    else:
        print("Model already exists at", model_dir + model_name)


if __name__ == '__main__':
    get_model()
