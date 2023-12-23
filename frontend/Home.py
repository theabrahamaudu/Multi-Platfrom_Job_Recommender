"""
This module contains the code for the Home page.
"""

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
from src.utils.config import LoadConfig

# load config yaml file details
config = LoadConfig()
server = config.get_server()
admin_username, admin_password = config.get_admin()

# page config
st.set_page_config(
    page_title="Job Recommender",
    page_icon="🕸",
    layout="wide"
)

page_bg('./assets/bg_img.jpg')
form_bg('./assets/form_bg.jpg')


# session state variables
if "admin" not in st.session_state:
    st.session_state["admin"] = None

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
if st.session_state.get("user") is None:  # noqa
    st.subheader(color(
        bold_italics("Not your first rodeo? Login to continue..."),
        "white"))
    with st.form("Login"):
        username = st.text_input("**Username**")
        password = st.text_input("**Password**", type="password")
        submitted = st.form_submit_button("**Login**", type="primary")

        # hash user password for comparison with database
        given_pword = hash_password(password)

        if submitted:
            # check if login is by admin and load admin view
            if username == admin_username and given_pword == admin_password:
                st.session_state["admin"] = True
                logger.info("Admin logged in")
            # else, login as user
            else:
                try:
                    user = requests.get(server+f"/users/login/{username}",
                                        json={"username": f"{username}"})

                    if user.status_code == 200:
                        user = user.json()
                        actual_pword = user["password"]
                        if given_pword == actual_pword:
                            st.session_state["user"] = user
                            st.session_state["temp_user"] = deepcopy(user)
                            logger.info("User %s logged in", user["user_id"])
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

    # Admin View
    # load admin view if admin session state is true
    if st.session_state.get("admin") is True:
        with st.form("Admin"):
            st.success("Welcome back, Admin. 🙂")
            st.subheader("Setup Database")
            setup_databse = st.form_submit_button(
                "Setup Database",
                type="primary")

            if setup_databse:
                cassandra_msg = requests.get(server+"/cassandra")
                if cassandra_msg.status_code == 200:
                    st.success("Cassandra database setup successful!")
                else:
                    st.warning(cassandra_msg.json()["message"])
                chroma_msg = requests.get(server+"/chroma")
                if chroma_msg.status_code == 200:
                    st.success("Chroma database setup successful!")
                else:
                    st.warning(chroma_msg.json()["message"])

        with st.form("Scrape"):
            st.subheader("Manually Scrape Jobs")
            scrape = st.form_submit_button(
                "Trigger Scrape",
                type="primary"
            )
            if scrape:
                scrape_msg = requests.get(server+"/scrape_jobs")
                if scrape_msg.status_code == 200:
                    st.success(
                        "Scraper running. Do not click " +
                        "again for 30 minutes. 🙂")
                else:
                    st.warning(scrape_msg.json()["message"])

        with st.form("Statistics"):
            st.subheader("Statistics")
            stats = st.form_submit_button(
                "**Get Stats**", type="primary"
            )
            if stats:
                user_count = requests.get(server+"/user_count")
                if user_count.status_code == 200:
                    st.info(f'Number of users: {user_count.json()["count"]}')
                else:
                    st.warning(user_count.json()["message"])
                job_count = requests.get(server+"/job_count")
                if job_count.status_code == 200:
                    st.info(f'Number of jobs: {job_count.json()["count"]}')
                else:
                    st.warning(job_count.json()["message"])

        if st.button("**Exit Admin**"):
            for key in st.session_state.keys():
                del st.session_state[key]
            logger.info("Admin logged out")
            refresh(time=0)

    # Prompt to create new account
    st.subheader(italics("TBH, I'm new here..."))

    # signup button which sets 'signup' session state to true
    if st.button("**Create Account**"):
        st.session_state["signup"] = True

# load user home page if user is logged in
else:
    # After loging in
    user = st.session_state.get("user")
    st.subheader(f"Welcome, {user['first_name'].capitalize()}!")  # type: ignore  # noqa

    with st.sidebar:
        if st.button("Logout", type="primary"):
            for key in st.session_state.keys():
                del st.session_state[key]
            logger.info("User %s logged out", user["user_id"])  # type: ignore  # noqa
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

    # Profile shortcut/profile update reminder
    with profile.form("Profile"):
        # check user data and prompt to update any missing fields

        # populate list of missing fields
        to_update = []
        if st.session_state.get("user")["skills"] == []:  # type: ignore
            to_update.append("Skills")
        if st.session_state.get("user")["work_history"] == []:  # type: ignore
            to_update.append("Work History")
        if st.session_state.get("user")["preferences"] == {}:  # type: ignore
            to_update.append("Preferences")

        # prompt the user based on the number of missing fields
        if len(to_update) > 0:
            st.subheader(bold("Pssst! This is important  🤧"))

        if len(to_update) > 2:
            st.warning(
                f"We want to help, but you need to work with us.\
                  Update your **{', '.join(to_update[:-1])}** and\
                  **{to_update[-1]}**\
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
        # Dynamic profile section button based on number of miisng fields
        if len(to_update) > 0:
            if st.form_submit_button("Update Profile", type="primary"):
                switch_page("Profile")
        else:
            if st.form_submit_button("View Profile"):
                switch_page("Profile")

# signup form if user is not logged in
# and the signup session state is true
if st.session_state.get("signup"):  # noqa
    with st.form("Signup"):
        st.warning("We know you might want to get creative, but\
                    choose your **username** wisely, because you can't change\
                    it later. Also, **_'dig_bick2023'_** is reserved 😎.")
        # username
        username = st.text_input(bold("Username"),
                                 placeholder="Anything but 'dig_bick2023'")
        if username == 'dig_bick2023':
            st.write(color(
                "Listen here you little s***," +
                " **_dig_bick2023_** is reserved! 🤬",
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
                st.write(color(
                    "We know you're excited, " +
                    "but the passwords have to match... 🥶",
                    "red"))
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
                # create new user on database
                try:
                    user = requests.post(server+"/users/new", json={
                        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # placeholder  # noqa
                        "created_at": "2023-11-30T22:16:56.836Z",  # placeholder  # noqa
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "password": hash_password(password),
                        "skills": [],
                        "work_history": [],
                        "preferences": {}

                    })
                    # set session user data to new user and
                    # refresh the page
                    if user.status_code == 200:
                        st.session_state["user"] = user.json()
                        st.success("Signup Successful! 🤟")
                        st.session_state["signup"] = False
                        refresh()

                    else:
                        # return error message if creation fails
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
                # prompt the user if there are validation errors
                st.error("Please fix the errors above.")

    # set the signup session state to false
    # if the user cancels
    if st.button("**Cancel**"):
        st.session_state["signup"] = False
        refresh(time=0)
