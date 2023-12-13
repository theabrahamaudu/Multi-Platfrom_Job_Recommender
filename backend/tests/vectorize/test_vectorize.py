from backend.etl.transform.vectorizer import vectorize, Embed


def test_vectorize_string():
    text = "Sample text"
    embeddings = vectorize(text)
    assert len(embeddings[0]) == 768
    assert type(embeddings) is list
    assert type(embeddings[0]) is list
    assert type(embeddings[0][0]) is float


def test_vectorize_dict():
    text = {"text": "Sample text"}
    embeddings = vectorize(text)
    assert len(embeddings[0]) == 768
    assert type(embeddings) is list
    assert type(embeddings[0]) is list
    assert type(embeddings[0][0]) is float


def test_vectorize_list_dict():
    text = [{"text": "Sample text"}]
    embeddings = vectorize(text)
    assert type(embeddings) is list
    assert type(embeddings[0]) is list
    assert type(embeddings[0][0]) is float


def test_embed_interface():
    text = "Sample text"
    embed = Embed()
    embeddings = embed([text])
    assert type(embed) is Embed
    assert type(embeddings) is list
    assert type(embeddings[0]) is list
    assert type(embeddings[0][0]) is float
