from src.utils.page_styling import (
    bold, italics, bold_italics, color
)


def test_bold():
    text = "man"

    bold_text = bold(text)

    assert bold_text == "**man**"


def test_italics():
    text = "man"

    italics_text = italics(text)

    assert italics_text == "*man*"


def test_bold_italics():
    text = "man"

    bold_italics_text = bold_italics(text)

    assert bold_italics_text == "**_man_**"


def test_color():
    text = "man"
    color_text = color(text, "red")

    assert color_text == ":red[man]"
