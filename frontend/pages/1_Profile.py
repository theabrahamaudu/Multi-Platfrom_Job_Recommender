import streamlit as st
from copy import deepcopy
from time import sleep
from streamlit_extras.switch_page_button import switch_page
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
    page_title="My Profile",
    page_icon="🕸",
)

page_bg('./assets/bg_img.jpg')
form_bg('./assets/form_bg.jpg')

# # session state variables
# if "skills" not in st.session_state:
#     st.session_state["skills"] = set[str]()

if st.session_state.get("user") is None:
    st.subheader(color(bold_italics("Login to view and edit your profile..."),
                       "white"))
    
else:
    # After loging in
    user = st.session_state.get("user")
    temp_user = deepcopy(user)
    st.subheader(f"Hey there {user['first_name'].capitalize()}, how's\
                 it going?")
    st.info("You can edit your **profile** here.\
                You can also delete your **account** here.")
    with st.form("General Profile"):
        st.subheader(bold("General Profile"))

        username = st.text_input(bold("Username"),
                                 value=user["username"],
                                 disabled=True)
        first_name = st.text_input(bold("First Name"),
                                   value=user["first_name"])
        last_name = st.text_input(bold("Last Name"),
                                   value=user["last_name"])
        email = st.text_input(bold("Email"),
                              value=user["email"])
        modify = st.form_submit_button("Modify")

        if modify:
            temp_user["first_name"] = first_name
            temp_user["last_name"] = last_name
            temp_user["email"] = email
            st.write(color("Changes noted but not saved yet", "green"))

    with st.form("Skills"):
        st.subheader(bold("Skills"))
        st.info("You can add or remove your **skills** here.")
        if len(temp_user["skills"]) < 1:
            skills = st.text_input(
                bold("Skills"),
                placeholder="Enter skills separated by commas",
            )
        else:
            skills = st.text_input(
                bold("Skills"),
                value=', '.join(temp_user["skills"]),
            )
        modify = st.form_submit_button("Modify")

        if modify:
            temp_user["skills"] = set(
                [skill.strip() for skill in skills.split(",")]
            )
            st.write(color("Changes noted but not saved yet", "green"))

    with st.divider():
        st.subheader(bold("Work History"))
        st.info("You can add or remove your **work history** here.")
        if len(temp_user["work_history"]) < 1:
            with st.form("Add Work History"):
                st.subheader(bold("Add Work History"))
                company = st.text_input(bold("Company"))
                position = st.text_input(bold("Position"))
                description = st.text_area(bold("Description"))
                start_date = st.date_input(bold("Start Date"))
                end_date = st.date_input(bold("End Date"))
                add = st.form_submit_button("Add")
                if add and str(start_date) < str(end_date):
                    temp_user["work_history"].append({
                        "company": company,
                        "position": position,
                        "description": description,
                        "start_date": start_date,
                        "end_date": end_date
                    })
                    st.write(color("Changes noted but not saved yet", "green"))
                else:
                    st.write(color("Can't end the job before you start it, no?", "red"))
        else:
            n = 0
            for experience in temp_user["work_history"]:
                n += 1
                with st.form(f"Work History {n}"):
                    st.subheader(bold(f"Work History {n}"))
                    company = st.text_input(bold("Company"),
                                            value=experience["company"])
                    position = st.text_input(bold("Position"),
                                             value=experience["position"])
                    description = st.text_area(bold("Description"),
                                               value=experience["description"])
                    start_date = st.date_input(bold("Start Date"),
                                               value=experience["start_date"])
                    end_date = st.date_input(bold("End Date"),
                                             value=experience["end_date"])
                    add = st.form_submit_button("Modify")
                    if add and str(start_date) < str(end_date):
                        temp_user["work_history"].append({
                            "company": company,
                            "position": position,
                            "description": description,
                            "start_date": start_date,
                            "end_date": end_date
                        })
                        st.write(color("Changes noted but not saved yet", "green"))
                    else:
                        st.write(color("Can't end the job before you start it, no?", "red"))
            with st.form("Add New Work History"):
                st.subheader(bold("Add Work History"))
                company = st.text_input(bold("Company"))
                position = st.text_input(bold("Position"))
                description = st.text_area(bold("Description"))
                start_date = st.date_input(bold("Start Date"))
                end_date = st.date_input(bold("End Date"))
                add = st.form_submit_button("Add")
                if add and str(start_date) < str(end_date):
                    temp_user["work_history"].append({
                        "company": company,
                        "position": position,
                        "description": description,
                        "start_date": start_date,
                        "end_date": end_date
                    })
                    st.write(color("Changes noted but not saved yet", "green"))
                else:
                    st.write(color("Can't end the job before you start it, no?", "red"))

    with st.divider():
        st.subheader(bold("Preferences"))
        st.info("You can add or remove your **preferences** here.")
        if len(temp_user["preferences"]) < 1:
            with st.form("Add Preferences"):
                st.subheader(bold("Add Preferences"))
                location = st.text_input(
                    bold("Location"),
                    placeholder="Lagos, Kaduna, etc.")
                setting = st.selectbox(
                    bold("Setting"),
                    ["On-site", "Remote", "Hybrid"],
                )
                industry = st.text_input(
                    bold("Industry"),
                    placeholder="Technology, Finance, etc.")
                job_role = st.text_input(
                    bold("Job Role"),
                    placeholder="Software Engineer, Data Scientist, etc.")

                add = st.form_submit_button("Add")
                if add:
                    temp_user["preferences"] = {
                        "location": location,
                        "setting": setting,
                        "industry": industry,
                        "job_role": job_role
                    }
                    st.write(color("Changes noted but not saved yet", "green"))
        else:
            with st.form("Preferences"):
                st.subheader(bold("Edit Preferences"))
                location = st.text_input(
                    bold("Location"),
                    placeholder="Lagos, Kaduna, etc.",
                    value=', '.join(temp_user["preferences"]["location"]))
                setting = st.selectbox(
                    bold("Setting"),
                    ["On-site", "Remote", "Hybrid"],
                    placeholder=temp_user["preferences"]["setting"],
                )
                industry = st.text_input(
                    bold("Industry"),
                    placeholder="Technology, Finance, etc.",
                    value=', '.join(temp_user["preferences"]["industry"]))
                job_role = st.text_input(
                    bold("Job Role"),
                    placeholder="Software Engineer, Data Scientist, etc.",
                    value=', '.join(temp_user["preferences"]["job_role"]))

                add = st.form_submit_button("Modify")
                if add:
                    temp_user["preferences"] = {
                        "location": location,
                        "setting": setting,
                        "industry": industry,
                        "job_role": job_role
                    }
                    st.write(color("Changes noted but not saved yet", "green"))

    with st.form("Change Password"):
        st.subheader(bold("Change Password"))
        st.warning("You can change your **password** here.")
        old_password = st.text_input(
            bold("Current Password"),
            type="password",
        )
        new_password = st.text_input(
            bold("New Password"),
            type="password",
        )
        confirm_password = st.text_input(
            bold("Confirm New Password"),
            type="password",
        )
        change = st.form_submit_button("Change")
        if change:
            if new_password == confirm_password:
                if hash_password(old_password) == user["password"]:
                    temp_user["password"] = hash_password(new_password)
                    st.write(color("Changes noted but not saved yet", "green"))
                else:
                    st.write(color("Wrong current password", "red"))
            else:
                st.write(color("New Passwords do not match", "red"))

    cancel, save = st.columns([1, 1])
    if cancel.button("Clear Changes"):
        temp_user = deepcopy(user)
        refresh()
    if save.button("Save Changes", type="primary"):
        try:
            user_id = user["user_id"]
            requests.put(f"{server}/users/update/{user_id}", json=temp_user)
            st.success("Changes Saved! 🙂")
            sleep(0.5)
            refresh()
        except requests.RequestException as e:
            logger.error(
                "Unable to connect to the server: %s", e, exc_info=True
            )
            st.error(
                "Oops! We were unable to connect to the server.\n"
                "Please try again later."
            )

    st.divider()
    st.subheader(bold("Danger Zone! :skull:"))
    with st.form("Delete Account"):
        st.error("You can delete your **account** here.")
        password = st.text_input(
            bold("Password"),
            type="password",
            placeholder="Enter your password to delete your account",
        )
        st.error("Warning: This action is **irreversible**.")
        delete = st.form_submit_button("Delete Account", type="primary")
        if delete:
            if hash_password(password) == user["password"]:
                user_id = user["user_id"]
                try:
                    requests.delete(f"{server}/users/delete/{user_id}")
                    st.session_state["user"] = None
                    st.session_state["signup"] = False
                    st.session_state["skills"] = set[str]()
                    st.success("Account Deleted! 🙂")
                    sleep(0.5)
                    refresh()
                    switch_page("Home")
                except requests.RequestException as e:
                    logger.error(
                        "Unable to connect to the server: %s", e, exc_info=True
                    )
                    st.error(
                        "Oops! We were unable to connect to the server.\
                            Please try again 😬"
                    )
