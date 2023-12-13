# type: ignore
"""
This module contains the code for the Profile page.
"""

from copy import deepcopy
import streamlit as st
from time import sleep
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page
import requests
from src.utils.hasher import hash_password
from src.utils.page_styling import (
    page_bg, form_bg, bold, bold_italics, color,
    refresh
)
from src.utils.frontend_log_config import frontend as logger
from src.utils.config import LoadConfig

# load config yaml file details
config = LoadConfig()
server = config.get_server()

# page config
st.set_page_config(
    page_title="My Profile",
    page_icon="🕸",
    layout="wide"
)

page_bg('./assets/bg_img.jpg')
form_bg('./assets/form_bg.jpg')

# # session state variables

# state variables to track changes
if "change_general" not in st.session_state:
    st.session_state["change_general"] = False

if "change_skills" not in st.session_state:
    st.session_state["change_skills"] = False

if "change_history" not in st.session_state:
    st.session_state["change_history"] = False

if "change_preferences" not in st.session_state:
    st.session_state["change_preferences"] = False

if "change_password" not in st.session_state:
    st.session_state["change_password"] = False

if "deleted" not in st.session_state:
    st.session_state["deleted"] = False

# Page content
if st.session_state.get("user") is None:  # noqa
    st.subheader(color(bold_italics("Login to view and edit your profile..."),
                       "white"))
else:
    # After loging in
    # load state variables
    user = st.session_state.get("user")
    temp_user = st.session_state.get("temp_user")
    old_exps = deepcopy(user["work_history"])

    # logout button
    with st.sidebar:
        if st.button("Logout", type="primary"):
            for key in st.session_state.keys():
                del st.session_state[key]
            logger.info("User %s logged out", user.user_id)
            switch_page("Home")
            refresh()

    st.subheader(f"Hey there {user['first_name'].capitalize()}, how's\
                 it going?")
    st.info("You can edit your **profile** here.\
                You can also delete your **account** here.")

    # in the profile sections, changes are appended to the `temp_user`
    # when the modify button of each section is clicked, but the main
    # `user` is not updated until the save button is clicked

    # general profile section
    with st.form("General Profile"):
        st.subheader(bold("General Profile"))

        username = st.text_input(bold("Username"),
                                 value=temp_user["username"],
                                 disabled=True)
        first_name = st.text_input(bold("First Name"),
                                   value=temp_user["first_name"])
        last_name = st.text_input(bold("Last Name"),
                                  value=temp_user["last_name"])
        email = st.text_input(bold("Email"),
                              value=temp_user["email"])
        modify = st.form_submit_button("Modify")

        if modify:
            # update `temp_user`
            temp_user["first_name"] = first_name
            temp_user["last_name"] = last_name
            temp_user["email"] = email
            # check if any changes and update session state
            if (user["email"] != temp_user["email"]) or \
               (user["first_name"] != temp_user["first_name"]) or \
               (user["last_name"] != temp_user["last_name"]):
                st.session_state["change_general"] = True
            else:
                st.session_state["change_general"] = False
        if st.session_state.get("change_general") is True:
            st.write(color("Changes noted but not saved yet", "green"))

    # skills section
    st.divider()
    with st.form("Skills"):
        st.subheader(bold("Skills"))
        st.info("You can add or remove your **skills** here.")
        # use placeholder if no previous skills
        if len(temp_user["skills"]) < 1:
            skills = st.text_input(
                bold("Skills"),
                placeholder="Enter skills separated by commas",
            )
        # else, start off with previous skills
        else:
            skills = st.text_input(
                bold("Skills"),
                value=', '.join([skill for skill in temp_user["skills"]]),
            )
        modify = st.form_submit_button("Modify")

        if modify:
            # update `temp_user`
            temp_user["skills"] = [
                skill.strip() for skill in skills.split(",")
            ]
            # check if any changes and update session state
            if user["skills"] != temp_user["skills"]:
                st.session_state["change_skills"] = True
            else:
                st.session_state["change_skills"] = False
        if st.session_state.get("change_skills") is True:
            st.write(color("Changes noted but not saved yet", "green"))

    # work history section
    st.divider()
    st.subheader(bold("Work History"))
    st.info("You can add or remove your **work history** here.")
    # if no previous work history
    if len(temp_user["work_history"]) < 1:
        with st.form("Add Work History"):
            # prompt for work history data points
            st.subheader(bold("Add Work History"))
            company = st.text_input(bold("Company"))
            position = st.text_input(bold("Position"))
            description = st.text_area(bold("Description"))
            start_date = st.date_input(bold("Start Date"),
                                       value=None,
                                       help="Enter start date")
            end_date = st.date_input(
                bold("End Date"),
                value=None,
                help="Leave blank if you're still working here")
            add = st.form_submit_button("Add")
            # check if start date is before end date
            if add and str(start_date) <= str(end_date):
                temp_user["work_history"].append({
                    "company": company,
                    "position": position,
                    "description": description,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                })
                # check if any changes and update session state
                if user["work_history"] != temp_user["work_history"]:
                    st.session_state["change_history"] = True
                else:
                    st.session_state["change_history"] = False

            # check if start date is after end date
            elif add and len(str(start_date)) > 0 and \
                    len(str(end_date)) > 0 and \
                    str(start_date) > str(end_date):
                st.write(color(
                    "Can't end the job before you start it, no?",
                    "red"
                ))
            if st.session_state.get("change_history") is True:
                st.write(color("Changes noted but not saved yet", "green"))

    # if work history exists
    else:
        n = 0
        st.session_state["change_history"] = [
            False for _ in range(len(old_exps))
        ]
        st.session_state["deleted"] = [False for _ in range(len(old_exps))]
        # create a new form for each experience in containers
        for idx, experience in enumerate(old_exps):
            with st.container():
                n += 1
                with st.form(f"Work History {n}"):
                    # data points populated with existing data
                    st.subheader(bold(f"Work History {n}"))
                    company = st.text_input(bold("Company"),
                                            value=experience["company"])
                    position = st.text_input(bold("Position"),
                                             value=experience["position"])
                    description = st.text_area(bold("Description"),
                                               value=experience["description"])
                    start_date = st.date_input(
                        bold("Start Date"),
                        value=datetime.strptime(
                            experience["start_date"], "%Y-%m-%d"
                        )
                    )
                    end_date = st.date_input(
                        bold("End Date"),
                        value=datetime.strptime(
                            experience["end_date"], "%Y-%m-%d"
                        )
                    )
                    # buttons to modify or delete experience
                    modify, delete = st.columns([1, 1])
                    # modify button
                    add = modify.form_submit_button("Modify")
                    # delete button (only if not already deleted)
                    if st.session_state.get("deleted")[idx] is False:
                        if delete.form_submit_button("Delete", type="primary"):
                            temp_user["work_history"].pop(idx)
                            st.session_state["change_history"][idx] = True
                            st.session_state["deleted"][idx] = True

                    if add and str(start_date) <= str(end_date):
                        # update `temp_user`
                        temp_user["work_history"][idx] = {
                            "company": company,
                            "position": position,
                            "description": description,
                            "start_date": start_date.strftime("%Y-%m-%d"),
                            "end_date": end_date.strftime("%Y-%m-%d")
                        }
                        # check if any changes and update session state
                        if old_exps[idx] != temp_user["work_history"][idx]:
                            st.session_state["change_history"][idx] = True
                        else:
                            st.session_state["change_history"][idx] = False
                    # check if start date is after end date
                    elif add and len(str(start_date)) > 0 and \
                            len(str(end_date)) > 0 and \
                            str(start_date) > str(end_date):
                        st.write(color(
                            "Can't end the job before you start it, no?",
                            "red"
                            )
                        )
                    # notify user if changes have not been saved
                    if st.session_state.get("change_history")[idx] is True \
                       and st.session_state.get("deleted")[idx] is False:
                        st.write(color(
                            "Changes noted but not saved yet",
                            "green"
                            )
                        )
                    # notify user if experience has been scheduled for deletion
                    elif st.session_state.get("deleted")[idx] is True:
                        st.write(color(
                            "Scheduled for deletion but not saved yet.\
                            To revert this change, scroll to the bottom\
                            and click **Clear Changes**", "red"
                            )
                        )
        # empty form to add new work history
        with st.container():
            with st.form("Add New Work History"):
                st.subheader(bold("Add Work History"))
                company = st.text_input(bold("Company"))
                position = st.text_input(bold("Position"))
                description = st.text_area(bold("Description"))
                start_date = st.date_input(bold("Start Date"))
                end_date = st.date_input(bold("End Date"))
                add = st.form_submit_button("Add")
                if add and str(start_date) <= str(end_date):
                    new_history = {
                        "company": company,
                        "position": position,
                        "description": description,
                        "start_date": str(start_date),
                        "end_date": str(end_date)
                    }
                    temp_user["work_history"].append(new_history)

                    if temp_user["work_history"][-1] == new_history:
                        st.session_state["change_history"] = True
                    else:
                        st.session_state["change_history"] = False
                elif add and len(str(start_date)) > 0 and \
                        len(str(end_date)) > 0 and \
                        str(start_date) > str(end_date):
                    st.write(color(
                        "Can't end the job before you start it, no?",
                        "red"
                        )
                    )
                if st.session_state.get("change_history") is True:
                    st.write(color("Changes noted but not saved yet", "green"))

    # preferences section: same form logic as with other
    # sections, so no need for 1,000 comments
    st.divider()
    st.subheader(bold("Preferences"))
    st.info("You can add or remove your **preferences** here.")

    # no previous preferences
    if len(temp_user["preferences"]) < 1:
        with st.form("Add Preferences"):
            # show data fields with tips
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
                if user["preferences"] != temp_user["preferences"]:
                    st.session_state["change_preferences"] = True
                else:
                    st.session_state["change_preferences"] = False
            if st.session_state.get("change_preferences") is True:
                st.write(color("Changes noted but not saved yet", "green"))

    # previous preferences exist
    else:
        with st.form("Preferences"):
            # show data fields with existing data
            st.subheader(bold("Edit Preferences"))
            location = st.text_input(
                bold("Location"),
                placeholder="Lagos, Kaduna, etc.",
                value=temp_user["preferences"]["location"])
            setting = st.selectbox(
                bold("Setting"),
                ["On-site", "Remote", "Hybrid"],
                placeholder=temp_user["preferences"]["setting"],
            )
            industry = st.text_input(
                bold("Industry"),
                placeholder="Technology, Finance, etc.",
                value=temp_user["preferences"]["industry"])
            job_role = st.text_input(
                bold("Job Role"),
                placeholder="Software Engineer, Data Scientist, etc.",
                value=temp_user["preferences"]["job_role"])

            add = st.form_submit_button("Modify")
            if add:
                temp_user["preferences"] = {
                    "location": location,
                    "setting": setting,
                    "industry": industry,
                    "job_role": job_role
                }
                if user["preferences"] != temp_user["preferences"]:
                    st.session_state["change_preferences"] = True
                else:
                    st.session_state["change_preferences"] = False
            if st.session_state.get("change_preferences") is True:
                st.write(color("Changes noted but not saved yet", "green"))

    # password change section
    st.divider()
    with st.form("Change Password"):
        st.subheader(bold("Change Password"))
        # `warning` prints in yellow, to give a sense of importance
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
            # validation and `temp_user` update
            if new_password == confirm_password:
                if hash_password(old_password) == user["password"]:
                    temp_user["password"] = hash_password(new_password)
                else:
                    st.write(color("Wrong current password", "red"))
            else:
                st.write(color("New Passwords do not match", "red"))

            if user["password"] == hash_password(confirm_password) and \
                    user["password"] == hash_password(new_password):
                st.session_state["change_password"] = False
                temp_user["password"] = user["password"]
                st.write(color(
                    "New password cannot be the same as the old",
                    "red"
                    )
                )
            # update session sate
            if user["password"] != temp_user["password"]:
                st.session_state["change_password"] = True
            else:
                st.session_state["change_password"] = False
        # notify user of changes (if any)
        if st.session_state.get("change_password") is True:
            st.write(color("Changes noted but not saved yet", "green"))

    # buttons to cancel or save changes
    cancel, save = st.columns([1, 1])
    # cancel button
    if cancel.button("Clear Changes"):
        st.session_state["temp_user"] = user
        refresh()

    # save button
    if save.button("Save Changes", type="primary"):
        try:
            # push updated information to the server
            user_id = user["user_id"]
            requests.put(f"{server}/users/update/{user_id}", json=temp_user)

            # pull updated information from the server
            # and update the session state
            updated_user = requests.get(
                f"{server}/users/fetch/{user_id}"
            ).json()
            st.session_state["user"] = updated_user
            st.session_state["temp_user"] = updated_user

            # clean section change states
            for key in ["change_general", "change_skills",
                        "change_history", "change_preferences",
                        "change_password"]:
                st.session_state[key] = False
            logger.info("User %s updated their profile", user.user_id)
            # show success message
            st.success("Changes Saved! 🙂")
            sleep(0.5)
            switch_page("Profile")
            refresh()
        except requests.RequestException as e:
            logger.error(
                "Unable to connect to the server: %s", e, exc_info=True
            )
            st.error(
                "Oops! We were unable to connect to the server.\n"
                "Please try again later."
            )

    # account deletion section
    st.divider()
    st.subheader(bold("Danger Zone! :skull:"))
    with st.form("Delete Account"):
        st.error("You can delete your **account** here.")
        # require password to delete account
        password = st.text_input(
            bold("Password"),
            type="password",
            placeholder="Enter your password to delete your account",
        )
        st.error("Warning: This action is **irreversible**.")
        delete = st.form_submit_button("Delete Account", type="primary")

        if delete:
            # delete user data from database
            # TODO: delete search and clicks metadata too
            if hash_password(password) == user["password"]:
                user_id = user["user_id"]
                try:
                    # delete user from server
                    requests.delete(f"{server}/users/delete/{user_id}")
                    logger.info("User %s deleted their account", user_id)
                    # clear session state and show success message
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    st.success("Account Deleted! 🙂")
                    sleep(0.5)
                    # go back to home page
                    switch_page("Home")
                    refresh()
                except requests.RequestException as e:
                    logger.error(
                        "Unable to connect to the server: %s", e, exc_info=True
                    )
                    st.error(
                        "Oops! We were unable to connect to the server.\
                            Please try again 😬"
                    )
