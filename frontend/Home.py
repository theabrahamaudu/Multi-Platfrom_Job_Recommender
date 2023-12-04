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
if "query" not in st.session_state:
    st.session_state["query"] = None
if "old_query" not in st.session_state:
    st.session_state["old_query"] = None
if "search_results" not in st.session_state:
    st.session_state["search_results"] = []
if "recommeded_jobs" not in st.session_state:
    st.session_state["recommended_jobs"] = None

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
    
    # Quick search
    search, profile = st.columns([1, 1], gap="large")
    with search.form("Quick Search"):
        st.subheader(bold("Lets get you employed 💼"))
        search_query = st.text_input(bold("Search Jobs..."),
                                     placeholder="e.g. Python Developer")
        submitted = st.form_submit_button("Search 🕵", type="primary")
        if submitted:
            if search_query == "":
                search_query = " "
            st.session_state["query"] = search_query
            switch_page("Search Jobs")
    # Profile shortcut/reminder
    with profile.form("Profile"):
        to_update = []
        if st.session_state.get("user")["skills"] == []:
            to_update.append("Skills")
        if st.session_state.get("user")["work_history"] == []:
            to_update.append("Work History")
        if st.session_state.get("user")["preferences"] == {}:
            to_update.append("Preferences")
        
        if len(to_update) > 0:
            st.subheader(bold("Pssst! This is important  🤧"))

        if len(to_update) > 2:
            st.warning(
                f"We want to help, but you need to work with us.\
                  Update your **{', '.join(to_update[:-1])}** and **{to_update[-1]}**\
                  to get better recommedations."
            )
        elif len(to_update) == 2:
            st.warning(
                f"We want to help, but you need to work with us.\
                  Update your **{to_update[0]}** and **{to_update[1]}**\
                  to get better recommedations."
            )
        elif len(to_update) == 1:
            st.warning(
                f"We want to help, but you need to work with us.\
                  Update your **{to_update[0]}**\
                  to get better recommedations."
            )
        if len(to_update) > 0:
            if st.form_submit_button("Update Profile", type="primary"):
                switch_page("Profile")
        else:
            if st.form_submit_button("View Profile"):
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

        # email
        email = st.text_input(bold("Email"))

        # password
        password = st.text_input(bold("Password"), type="password")
        confirm_password = st.text_input(bold("Confirm Password"),
                                         type="password")

        # store info
        submitted = st.form_submit_button(bold("Signup"), type="primary", )

        if submitted:
            # Validate Data
            validated = True
            if password == "":
                st.write(color("Ha-ha-ha, password cannot be blank.", "red"))
                validated = False

            if password != confirm_password:
                st.write(color("    We know you're excited, but the passwords have to match... 🥶", "red"))
                validated = False

            if username == 'dig_bick2023':
                validated = False

            if username == "":
                st.write(color("Ha-ha-ha, username cannot be blank.", "red"))
                validated = False

            if "@" not in email or len(email) < 4:
                st.write(color("Nope, invalid email.", "red"))
                validated = False

            if len(first_name) < 1 or len(last_name) < 1:
                validated = False
                st.write(color("Ha-ha-ha, name cannot be blank.", "red"))

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
                st.error("Please fix the errors above.")

    if st.button("**Cancel**"):
        st.session_state["signup"] = False
        refresh(time=0)
