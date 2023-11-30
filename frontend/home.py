import streamlit as st
import requests
from src.utils.hasher import hash_password
from src.utils.page_styling import page_bg, form_bg, bold, italics, bold_italics, color
from src.utils.frontend_log_config import frontend as logger


# server url
server = "http://localhost:28000"

# page config
st.set_page_config(
    page_title="Job Recommender",
    page_icon="🕸",
)

page_bg('./assets/bg_img.jpg')
form_bg('./assets/form_bg.jpg')


# session state variables
st.session_state["user"] = None
st.session_state["signup"] = False

# page scripts
st.header("Multi-Platform Job Recommender")

st.write(color(bold_italics("Not your first rodeo? Login to continue..."),
               "white"))
# login form
with st.form("Login"):
    username = st.text_input("**Username**")
    password = st.text_input("**Password**", type="password")
    submitted = st.form_submit_button("**Login**", type="primary")

    given_pword = hash_password(password)

    if submitted:
        try:
            user = requests.get(server+f"/users/login/{username}",
                                json={"username": f"{username}"})

            if user.status_code == 200:
                user = user.json()
                actual_pword = user["password"]
                if given_pword == actual_pword:
                    st.session_state["user"] = user
                    st.success("Login Successful! 😀")
                else:
                    st.error("Incorrect Password, kinda sus 🧐")
            else:
                st.error("Sure you have an account?\
                            Cuz we couldn't find it 🤷‍♀️.\n\
                            Check your **username** and try again,\
                            or just sign up 😏.")
        except requests.RequestException as e:
            logger.error(
                "Unable to connect to the server: %s", e, exc_info=True
            )
            st.error(
                "Oops! We were unable to connect to the server.\
                    Please try again 😬"
            )

st.write("**_TBH, I'm new here..._**")
# signup form
if st.session_state["signup"] is False:
    if st.button("**Create Account**"):
        st.session_state["signup"] = True

if st.session_state["signup"]:
    with st.form("Signup"):
        st.warning("We know you might want to get creative, but\
                    choose your **username** wisely, because you can't change\
                    it later. Also _'dig_bick2023'_ is reserved 😎.")
        username = st.text_input(bold("Username"),
                                 placeholder="Anything but 'dig_bick2023'")
        password = st.text_input(bold("Password"), type="password")
        first_name = st.text_input(bold("First Name"))
        last_name = st.text_input(bold("Last Name"))
        email = st.text_input(bold("Email"))
        submitted = st.form_submit_button(bold("Signup"), type="primary")

        if submitted:
            try:
                user = requests.post(server+"/users/new", json={
                    "username": username,
                    "password": hash_password(password),
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email
                })
                assert user.status_code == 200
                st.session_state["user"] = user.json()
                st.success("Signup Successful! 🤟")
            except requests.RequestException as e:
                logger.error(
                    "Unable to connect to the server: %s", e, exc_info=True
                )
                st.error(
                    "Oops! We were unable to connect to the server.\
                        Please try again 😬"
                )
    if st.button("**Cancel**"):
        st.session_state["signup"] = False
