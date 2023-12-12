"""
This module contains functions to style the elements of pages
"""

import base64
import streamlit as st
from time import sleep
from streamlit.components.v1 import html


# set background image
def page_bg(main_bg: str, main_bg_ext: str = "jpg"):
    """
    Sets the background image of the Streamlit app from an image file.

    Args:
    - main_bg (str): The filename of the main background image.
    - main_bg_ext (str, optional): The extension of the main background image.
      Defaults to 'jpg'.

    This function takes the filename of an image file, encodes it into base64,
    and sets it as the background image for the Streamlit app.
    The 'main_bg_ext' argument is used to specify the image extension.
    The background image is styled with CSS properties to cover the entire app.
    """

    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(
                 open(main_bg, "rb").read()
                ).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


def form_bg(form_bg: str, form_bg_ext: str = "jpg"):
    """
    Sets the background image of a Streamlit form from an image file.

    Args:
    - form_bg (str): The filename of the form background image.
    - form_bg_ext (str, optional): The extension of the form background image.
      Defaults to 'jpg'.

    This function sets the background image for a Streamlit form. The
    'form_bg_ext' argument specifies the image extension. It uses CSS styling
    to set the background image, add border radius, create a shadow effect,
    and apply a mask to the form to achieve a visually appealing design.
    The function reads the image file from the root folder, encodes it into
    base64, and applies it as the background of the Streamlit form.
    """

    st.markdown(
        f"""
        <style>
        [data-testid="stForm"] > div:first-child {{
            background: url(data:image/{form_bg_ext};base64,{base64.b64encode(
                open(form_bg, "rb").read()
            ).decode()});
        border-radius: 5px;
        overflow: hidden;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), \
            0 6px 20px 0 rgba(0, 0, 0, 0.19);
        mask-image: linear-gradient(
        to right,
        rgba(0, 0, 0, 1) 0%,
        rgba(0, 0, 0, 1) 10%,
        rgba(0, 0, 0, 1) 100%,
        rgba(0, 0, 0, 0) 100%
        );
        }}
        </style>
        """,
        unsafe_allow_html=True,
        )


def open_link(url: str):
    """
    Opens a URL in a new browser tab.

    Args:
    - url (str): The URL to be opened.

    This function generates and executes a JavaScript script that opens the
    provided URL in a new browser tab when invoked. It takes the 'url'
    argument and constructs a script to execute in the browser.
    The script opens the URL in a new tab using the 'window.open' method with
    the '_blank' parameter, ensuring the focus is set to the new tab.
    """
    open_script = """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)


def bold(text: str) -> str:
    """
    Returns the input text formatted in bold.

    Args:
    - text (str): The text to be formatted.

    Returns:
    - str: The input text wrapped in bold markdown format
        (double asterisks '**').
    """
    return f"**{text}**"


def italics(text: str) -> str:
    """
    Returns the input text formatted in italics.

    Args:
    - text (str): The text to be formatted.

    Returns:
    - str: The input text wrapped in italics markdown format
        (single asterisks '*').
    """
    return f"*{text}*"


def bold_italics(text: str) -> str:
    """
    Returns the input text formatted in bold and italics.

    Args:
    - text (str): The text to be formatted.

    Returns:
    - str: The input text wrapped in bold and italics markdown format
        ('**_'text'_**').
    """
    return f"**_{text}_**"


def color(text: str, color: str) -> str:
    """
    Formats the input text with the specified color using markdown.

    Args:
    - text (str): The text to be formatted.
    - color (str): The color name or code to apply to the text.

    Returns:
    - str: The input text wrapped in markdown syntax to display with the
        specified color.
    """
    return f":{color}[{text}]"


def refresh(emoji: str = "🍲", time: int = 1):
    """
    Simulates a cooking animation using Streamlit's spinner.

    Args:
    - emoji (str, optional): The emoji to display during the cooking animation.
        Defaults to "🍲".
    - time (int, optional): The duration of the cooking simulation in seconds.
        Defaults to 1.

    Displays a spinner with a cooking emoji and waits for the specified time
    before refreshing the Streamlit app.
    """
    with st.spinner(f"Cooking... {emoji}"):
        sleep(time)
        st.rerun()
