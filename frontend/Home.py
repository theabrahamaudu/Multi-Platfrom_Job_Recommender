import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from copy import deepcopy
import requests
from src.utils.hasher import hash_password
from src.utils.page_styling import (
    page_bg, form_bg, bold, italics, bold_italics, color,
    refresh
)
from src.utils.frontend_log_config import frontend as logger
from src.utils.config import test_server


# server url
server = test_server

# page config
st.set_page_config(
    page_title="Job Recommender",
    page_icon="🕸",
    layout="wide"
)

page_bg('./assets/bg_img.jpg')
form_bg('./assets/form_bg.jpg')


# session state variables
if "user" not in st.session_state:
    st.session_state["user"] = None
# temporary user data to store changes temporarily
if "temp_user" not in st.session_state:
    st.session_state["temp_user"] = None
if "signup" not in st.session_state:
    st.session_state["signup"] = False

# page scripts
st.title("Multi-Platform Job Recommender")


# login form
if st.session_state.get("user") is None:
    st.subheader(color(bold_italics("Not your first rodeo? Login to continue..."),
             "white"))
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
                        st.session_state["temp_user"] = deepcopy(user)
                        st.success("Login Successful! 😀")
                        refresh()
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
    # Prompt to create new account
    st.subheader(italics("TBH, I'm new here..."))

    if st.button("**Create Account**"):
        st.session_state["signup"] = True

else:
    # After loging in
    user = st.session_state.get("user")
    st.subheader(f"Welcome, {user['first_name'].capitalize()}!")

    with st.sidebar:
        if st.button("Logout", type="primary"):
            for key in st.session_state.keys():
                del st.session_state[key]
            refresh()
    
    # extra nav buttons
    search, profile = st.columns([1, 1], gap="large")
    if search.button("Search Jobs"):
        switch_page("Search Jobs")
    if profile.button("View Profile"):
        switch_page("Profile")

# signup form
if st.session_state.get("signup"):
    with st.form("Signup"):
        st.warning("We know you might want to get creative, but\
                    choose your **username** wisely, because you can't change\
                    it later. Also, **_'dig_bick2023'_** is reserved 😎.")
        # username
        username = st.text_input(bold("Username"),
                                 placeholder="Anything but 'dig_bick2023'")
        if username == 'dig_bick2023':
            st.write(color("    Listen here you little s***, **_dig_bick2023_** is reserved! 🤬",
                           "red"))
        # name
        first_name = st.text_input(bold("First Name"))
        last_name = st.text_input(bold("Last Name"))
        if len(first_name) < 1 or len(last_name) < 1:
            st.write(color("Ha-ha-ha, name cannot be blank.", "red"))

        # email
        email = st.text_input(bold("Email"))
        if "@" not in email or len(email) < 4:
            st.write(color("Invalid email.", "red"))

        # password
        password = st.text_input(bold("Password"), type="password")
        confirm_password = st.text_input(bold("Confirm Password"),
                                         type="password")

        if password == confirm_password:
            pass
        else:
            st.write(color("    We know you're excited, but the passwords have to match... 🥶", "red"))
        
        # store info
        submitted = st.form_submit_button(bold("Signup"), type="primary", )

        if submitted:
            # Validate Data
            validated = True
            if password != confirm_password or password == "":
                validated = False

            if username == 'dig_bick2023':
                validated = False

            if "@" not in email:
                validated = False

            for value in [username, first_name, last_name, email]:
                if value == "":
                    validated = False

            if validated:
                try:
                    user = requests.post(server+"/users/new", json={
                        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # placeholder
                        "created_at": "2023-11-30T22:16:56.836Z",  # placeholder 
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "password": hash_password(password),
                        "skills": [],
                        "work_history": [],
                        "preferences": {}

                    })
                    if user.status_code == 200:
                        st.session_state["user"] = user.json()
                        st.success("Signup Successful! 🤟")
                        st.session_state["signup"] = False
                        refresh()

                    else:
                        message = user.json()
                        st.error(message["message"])
                except requests.RequestException as e:
                    logger.error(
                        "Unable to connect to the server: %s", e, exc_info=True
                    )
                    st.error(
                        "Oops! We were unable to connect to the server.\
                            Please try again 😬"
                    )
            else:
                st.error("Something's not right with the info you've provided")

    if st.button("**Cancel**"):
        st.session_state["signup"] = False
        refresh(time=0)
