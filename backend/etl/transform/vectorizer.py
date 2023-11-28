from backend.src.models.embedding_model import model
from numpy import ndarray


def vectorize(input: str | dict) -> ndarray:
    match input:
        case str():
            return model.encode(input)  # type: ignore

        case dict():
            full_text = str()
            fields = list(input.keys())[1:]

            for field in fields:
                full_text += str(input[field]) + " "
            return model.encode(full_text)  # type: ignore
        case _:
            raise ValueError
