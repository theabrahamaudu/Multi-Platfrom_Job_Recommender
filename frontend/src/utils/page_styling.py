import base64
import streamlit as st
from time import sleep


# set background image
def page_bg(main_bg: str, main_bg_ext: str = "jpg"):
    '''
    A function to unpack an image from root folder and set as bg.

    Returns
    -------
    The background.
    '''

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


def form_bg(side_bg: str, side_bg_ext: str = "jpg"):

    st.markdown(
        f"""
        <style>
        [data-testid="stForm"] > div:first-child {{
            background: url(data:image/{side_bg_ext};base64,{base64.b64encode(
                open(side_bg, "rb").read()
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


def bold(text):
    return f"**{text}**"


def italics(text):
    return f"*{text}*"


def bold_italics(text):
    return f"**_{text}_**"


def color(text, color):
    return f":{color}[{text}]"


def refresh(emoji: str = "🍲", time: int = 1):
    with st.spinner(f"Cooking... {emoji}"):
        sleep(time)
        st.rerun()
