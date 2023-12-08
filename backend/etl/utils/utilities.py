"""
This module contains utility functions for database operations
via API routes.
"""

from etl.databases.cassandra.cassandra_conn import CassandraConn
from cassandra.query import ValueSequence
from uuid import UUID

# set up Cassandra connection
session = CassandraConn().session


def scrub_metadata(user_id: str, cuttoff: int = 10):
    """
    Deletes stale search and click metadata associated with the given user ID.

    Args:
    - user_id (str): The ID of the user whose metadata needs to be scrubbed.
    - cuttoff (int, optional): The cutoff point indicating the number of
      recent metadata entries to retain. Default is 10.

    This function retrieves the search and click metadata associated with the
    given user ID from the respective tables (`search_metadata` and
    `clicks_metadata`). It then identifies stale entries beyond the specified
    cutoff point and deletes them from the respective tables.

    Note:
    - Stale entries are determined based on their count compared to the
      cutoff value.
    """
    # Load Searches
    query = "SELECT search_id from search_metadata WHERE user_id = %s"
    search_id_set = session.execute(query, (user_id, ))

    # parse results
    search_ids = []
    for id in search_id_set:
        search_ids.append(id['search_id'])

    # delete stale searches
    if len(search_ids) > cuttoff:
        stale_searches = search_ids[cuttoff:]
        query = "DELETE FROM search_metadata WHERE search_id IN %s"
        session.execute(query, [ValueSequence(tuple(stale_searches))])

    # Load Clicks
    query = "SELECT click_id from clicks_metadata WHERE user_id = %s"
    click_id_set = session.execute(query, (user_id, ))

    # parse results
    click_ids = []
    for id in click_id_set:
        click_ids.append(id['click_id'])

    # delete stale clicks
    if len(click_ids) > cuttoff:
        stale_clicks = click_ids[cuttoff:]
        query = "DELETE FROM clicks_metadata WHERE click_id IN %s"
        session.execute(query, [ValueSequence(tuple(stale_clicks))])


def get_user_metadata(user_id: UUID, limit: int = 5, trunc: int = -1) -> str:
    """
    Retrieves and formats metadata associated with a user.

    Args:
    - user_id (UUID): The unique identifier of the user.
    - limit (int): The maximum number of records to retrieve for searches and
      job interactions. Default is 5.
    - trunc (int): The maximum character limit for job descriptions. Default
      is -1 (no truncation).

    Returns:
    - str: A formatted string containing user data, previous searches, and
      previous job interactions.

    This function fetches various types of metadata associated with a specific
    user ID. It retrieves previous search queries, previous job interactions
    (with optional truncation of job descriptions), and user-specific data
    (skills, work history, preferences) from different tables. It then
    combines this information into a single string, separated by commas,
    and returns it.
    """
    # Searches
    previous_searches = get_user_searches(str(user_id), limit)

    # Job interactions
    previous_jobs = get_previous_jobs(str(user_id), trunc, limit)

    # User data
    user_data = get_user_data(user_id)

    # combine user data
    user_metadata = f"{user_data}, {previous_searches}, {previous_jobs}"

    return user_metadata


def get_user_searches(user_id: str, limit: int) -> str:
    """
    Retrieves recent search queries associated with the given user ID.

    Args:
    - user_id (str): The ID of the user for whom search queries are retrieved.
    - limit (int): The maximum number of search queries to retrieve.

    Returns:
    - str: A string containing the recent search queries separated by commas.

    This function fetches the recent search queries from the `search_metadata`
    table associated with the provided user ID, limited by the specified count.
    It collects the search queries and returns them as a single string,
    where each query is separated by a comma.
    """
    # load previous searches
    query = "SELECT search_query\
             FROM search_metadata WHERE user_id = %s LIMIT %s"
    search_query_set = session.execute(query, (user_id, limit))

    # parse results
    search_query = []
    for query in search_query_set:
        search_query.append(query['search_query'])
    # flatten queries to single string
    flat_queries = ", ".join(search_query)

    return flat_queries


def get_previous_jobs(user_id: str, trunc: int, limit: int) -> str:
    """
    Retrieves truncated job descriptions associated with jobs the user clicked.

    Args:
    - user_id (str): The ID of the user for whom job descriptions
      are retrieved.
    - trunc (int): The length to truncate each job description.
    - limit (int): The maximum number of job descriptions to retrieve.

    Returns:
    - str: A string containing truncated job descriptions separated by commas.

    This function retrieves job IDs from `clicks_metadata` associated with
    the provided user ID, then fetches corresponding job descriptions from
    `job_listings`. It truncates each job description to the specified
    length (`trunc`) and returns them as a single string, where each truncated
    job description is separated by a comma.
    """
    # Job Clicks
    # load job ids of jobs the user has clicked
    query = "SELECT job_id\
             FROM clicks_metadata WHERE user_id = %s LIMIT %s"
    job_clicks_set = session.execute(query, (user_id, limit))
    # parse results
    job_ids = []
    for job in job_clicks_set:
        job_ids.append(UUID(job['job_id']))

    # Job descriptions
    # load job descriptions of jobs the user has clicked
    query = "SELECT job_desc FROM job_listings WHERE uuid IN %s"
    job_desc_set = session.execute(query, [ValueSequence(tuple(job_ids))])
    # parse results
    job_descs = []
    for job in job_desc_set:
        # truncate job descriptions to `trunc` characters
        job_descs.append(job['job_desc'][:trunc])

    # flatten job descriptions into single string
    flat_job_descs = ", ".join(job_descs)

    return flat_job_descs


def get_user_data(user_id: UUID) -> str:
    """
    Retrieves and formats user data from the `users` table.

    Args:
    - user_id (UUID): The unique identifier of the user.

    Returns:
    - str: A formatted string containing user skills, work history,
      and preferences.

    This function retrieves specific data (skills, work history, and
    preferences) associated with a given user ID from the 'users' table.
    It formats the retrieved data into a single string, separated by commas,
    and returns it. If any of the user data is not set or unavailable,
    the function handles it by providing an empty string for that particular
    section (skills, work history, or preferences) in the returned string.
    """
    # fetch user data
    query = "SELECT skills, work_history, preferences\
             FROM users WHERE user_id = %s"

    user_data = session.execute(query, (user_id, ))[0]

    # parse user data
    skills = user_data['skills']
    work_history = user_data['work_history']
    preferences = user_data['preferences']

    # flatten skills
    try:
        flat_skills = ", ".join(skills)
    except TypeError:
        # if skills are not set
        flat_skills = ""

    # flatten work history
    try:
        flat_work_history = ", ".join(
            value for experience in
            work_history for value in experience.values()
        )
    except TypeError:
        # if work history is not set
        flat_work_history = ""

    # flatten preferences
    try:
        flat_preferences = ", ".join(preferences.values())
    except AttributeError:
        # if preferences are not set
        flat_preferences = ""

    # combine user data
    data_string = f"{flat_skills}, {flat_work_history}, {flat_preferences}"

    return data_string
