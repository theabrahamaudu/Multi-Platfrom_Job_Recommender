from src.models.embedding_model import model
from chromadb import Documents, EmbeddingFunction, Embeddings


class Embed(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return model.encode(  # type: ignore
            list(input),
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()  # type: ignore


def vectorize(input: str | dict[str, str] | list[dict[str, str]]) -> Embeddings:  # noqa E501
    match input:
        case str():
            return Embed()([input])

        case dict():
            full_text = str()
            fields = list(input.keys())[1:]

            for field in fields:
                full_text += str(input[field]) + " "
            return Embed()([full_text])

        case list():
            texts = list()
            for item in input:
                full_text = str()
                fields = list(item.keys())[1:]
                for field in fields:
                    full_text += str(item[field]) + " "
                texts.append(full_text)
            return Embed()(texts)
        case _:
            raise ValueError
