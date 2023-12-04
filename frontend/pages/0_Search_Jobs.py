from copy import deepcopy
import streamlit as st
from time import sleep
from datetime import datetime
import time
from streamlit_extras.switch_page_button import switch_page
import requests
from src.utils.hasher import hash_password
from src.utils.page_styling import (
    page_bg, form_bg, bold, italics, bold_italics, color,
    refresh, open_link
)
from src.utils.frontend_log_config import frontend as logger
from src.utils.config import test_server


# server url
server = test_server

# page config
st.set_page_config(
    page_title="Search Jobs",
    page_icon="🕸",
    layout="wide"
)

page_bg('./assets/bg_img.jpg')
form_bg('./assets/form_bg.jpg')

# # session state variables

# Page content
if st.session_state.get("user") is None:
    st.subheader(color(bold_italics("Login to search jobs..."),
                       "white"))
else:
    # After loging in
    with st.sidebar:
        if st.button("Logout", type="primary"):
            for key in st.session_state.keys():
                del st.session_state[key]
            switch_page("Home")
            refresh()
    with st.form("Search"):
        st.subheader(bold("Lets get you employed 💼"))
        if st.session_state.get("query") is None or\
           st.session_state.get("query") == " ":
            search_query = st.text_input(bold("Search Jobs..."),
                                         placeholder="e.g. Python Developer")
        else:
            search_query = st.text_input(bold("Search Jobs..."),
                                         placeholder="e.g. Python Developer",
                                         value=st.session_state.get("query"))
        submitted = st.form_submit_button("Search 🕵", type="primary")
        if submitted:
            if search_query == "":
                search_query = " "
            st.session_state["query"] = search_query
            refresh()

    if st.session_state.get("query") is None or\
       st.session_state.get("query") == " ":
        st.subheader(bold("Because we're nice"))
        st.write(bold("We know you're lazy, so here are a few of our top \
        recommended jobs:"))
        if st.session_state.get("recommended_jobs") is None:
            with st.spinner("Ransacking the data base... 🧮"):
                try:
                    payload = {
                        "query": " ",
                        "user_id": f"{st.session_state.get('user')['user_id']}",
                    }
                    st.session_state["recommended_jobs"] = requests.get(
                        f"{server}/index/search/{payload['user_id']}&&{payload['query']}",
                        json=payload
                    ).json()
                    
                except requests.RequestException as e:
                    logger.error(
                        "Unable to connect to the server: %s", e, exc_info=True
                    )
                    st.warning("Oops! The universe is not on your side.\
                            We couldn't cook any recommendations for you.")

        if st.session_state.get("recommended_jobs") is not None:
            for job_id in st.session_state.get("recommended_jobs")[:3]:
                with st.container():
                    job = requests.get(
                        f"{server}/jobs/fetch/{job_id}",
                        json={"job_id": f"{job_id}"}
                    ).json()
                    job = job[0]
                    with st.form(str(job_id)):
                        st.write(
                            bold_italics(
                                f"{job['job_title']} - {job['company_name']} - {job['location']}"
                            ))
                        st.write(bold(f"Source: {job['source']}"))
                        with st.expander(bold("Job Description:")):
                            st.write(f"{job['job_desc']}")
                        st.write(f"Seniority: {job['seniority']}")
                        st.write(f"Type: {job['emp_type']}")
                        st.write(f"Function: {job['job_func']}")
                        st.write(f"Industry: {job['ind']}")
                        click = st.form_submit_button(
                            "Apply", type="primary"
                        )
                        if click:
                            # store user click metadata
                            click_metadata = {
                                "user_id": f"{st.session_state.get('user')['user_id']}",
                                "click_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # placeholder
                                "click_timestamp": "2023-12-03T15:04:53.303Z",  # placeholder
                                "job_id": f"{job_id}"
                            }
                            requests.post(
                                f"{server}/clicks/new", json=click_metadata
                            )
                            # open job link in new tab
                            open_link(
                                job["job_link"]
                            )
    if st.session_state.get("query") is not None and\
       st.session_state.get("query") != " ":
        st.subheader(bold("Here you go..."))
        st.write(bold("Top jobs that match your search:"))
        if st.session_state.get("query") != st.session_state.get("old_query"):
            with st.spinner("Ransacking the data base... 🧮"):
                try:
                    start = time.time()
                    payload = {
                        "query": f"{st.session_state.get('query')}",
                        "user_id": f"{st.session_state.get('user')['user_id']}",
                    }
                    st.session_state["search_results"] = requests.get(
                        f"{server}/index/search/{payload['user_id']}&&{payload['query']}",
                        json=payload
                    ).json()
                    elapsed = time.time() - start
                    st.info(f"Search time: {elapsed:.2f} seconds  🕒")

                    # store search metadata
                    search_metadata = {
                        "user_id": f"{st.session_state.get('user')['user_id']}",
                        "search_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # placeholder
                        "search_timestamp": "2023-12-04T09:19:28.925Z",  # placeholder
                        "search_query": f"{st.session_state.get('query')}",
                        "search_results": st.session_state.get("search_results")
                    }
                    requests.post(
                        f"{server}/search/new",
                        json=search_metadata
                    )
                    st.session_state["old_query"] = st.session_state.get("query")
                except requests.RequestException as e:
                    logger.error(
                        "Unable to connect to the server: %s", e, exc_info=True
                    )
                    st.warning("Oops! We were unable to connect to the server.\
                            Please try again 😬.")

        for job_id in st.session_state.get("search_results"):
            with st.container():
                try:
                    job = requests.get(
                        f"{server}/jobs/fetch/{job_id}",
                        json={"job_id": f"{job_id}"}
                    ).json()
                    job = job[0]
                    with st.form(str(job_id)):
                        st.write(
                            bold_italics(
                                f"{job['job_title']} - {job['company_name']} - {job['location']}"
                            ))
                        st.write(bold(f"Source: {job['source']}"))
                        with st.expander(bold("Job Description:")):
                            st.write(f"{job['job_desc']}")
                        st.write(f"Seniority: {job['seniority']}")
                        st.write(f"Type: {job['emp_type']}")
                        st.write(f"Function: {job['job_func']}")
                        st.write(f"Industry: {job['ind']}")
                        click = st.form_submit_button(
                            "Apply", type="primary"
                        )
                        if click:
                            # store user click metadata
                            click_metadata = {
                                "user_id": f"{st.session_state.get('user')['user_id']}",
                                "click_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # placeholder
                                "click_timestamp": "2023-12-03T15:04:53.303Z",  # placeholder
                                "job_id": f"{job_id}"
                            }
                            requests.post(
                                f"{server}/clicks/new", json=click_metadata
                            )
                            # open job link in new tab
                            open_link(
                                job["job_link"]
                            )
                except Exception as e:
                    logger.error(
                        "Unable to connect to the server: %s", e,
                        exc_info=True
                    )
                    st.warning("Oops! Couldn't load this job. Shame, it\
                                might have been the one you were\
                                looking for 😂.")
