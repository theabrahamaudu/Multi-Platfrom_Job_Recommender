from etl.databases.cassandra.cassandra_conn import CassandraConn
from cassandra.query import ValueSequence
from uuid import UUID
session = CassandraConn().session


def scrub_metadata(user_id: str, cuttoff: int = 10):
    # Searches
    query = "SELECT search_id from search_metadata WHERE user_id = %s"
    search_id_set = session.execute(query, (user_id, ))
    search_ids = []
    for id in search_id_set:
        search_ids.append(id['search_id'])

    if len(search_ids) > cuttoff:
        stale_searches = search_ids[cuttoff:]
        query = "DELETE FROM search_metadata WHERE search_id IN %s"
        session.execute(query, [ValueSequence(tuple(stale_searches))])

    # Clicks
    query = "SELECT click_id from clicks_metadata WHERE user_id = %s"
    click_id_set = session.execute(query, (user_id, ))
    click_ids = []
    for id in click_id_set:
        click_ids.append(id['click_id'])

    if len(click_ids) > cuttoff:
        stale_clicks = click_ids[cuttoff:]
        query = "DELETE FROM clicks_metadata WHERE click_id IN %s"
        session.execute(query, [ValueSequence(tuple(stale_clicks))])


def get_user_metadata(user_id: UUID, limit: int = 5, trunc: int = -1) -> str:
    # Searches
    previous_searches = get_user_searches(str(user_id), limit)

    # Job interactions
    previous_jobs = get_previous_jobs(str(user_id), trunc, limit)

    # User data
    user_data = get_user_data(user_id)

    user_metadata = f"{user_data}, {previous_searches}, {previous_jobs}"

    return user_metadata


def get_user_searches(user_id: str, limit: int) -> str:
    query = "SELECT search_query\
             FROM search_metadata WHERE user_id = %s LIMIT %s"
    search_query_set = session.execute(query, (user_id, limit))
    search_query = []
    for query in search_query_set:
        search_query.append(query['search_query'])

    flat_queries = ", ".join(search_query)

    return flat_queries


def get_previous_jobs(user_id: str, trunc: int, limit: int) -> str:
    # Job Clicks
    query = "SELECT job_id\
             FROM clicks_metadata WHERE user_id = %s LIMIT %s"
    job_clicks_set = session.execute(query, (user_id, limit))
    job_ids = []
    for job in job_clicks_set:
        job_ids.append(UUID(job['job_id']))

    # Job descriptions
    query = "SELECT job_desc FROM job_listings WHERE uuid IN %s"
    job_desc_set = session.execute(query, [ValueSequence(tuple(job_ids))])
    job_descs = []
    for job in job_desc_set:
        job_descs.append(job['job_desc'][:trunc])

    flat_job_descs = ", ".join(job_descs)

    return flat_job_descs


def get_user_data(user_id: UUID) -> str:
    query = "SELECT skills, work_history, preferences\
             FROM users WHERE user_id = %s"

    user_data = session.execute(query, (user_id, ))[0]

    skills = user_data['skills']
    work_history = user_data['work_history']
    preferences = user_data['preferences']

    # flatten skills
    try:
        flat_skills = ", ".join(skills)
    except TypeError:
        flat_skills = ""

    # flatten work history
    try:
        flat_work_history = ", ".join(
            value for experience in work_history for value in experience.values()
        )
    except TypeError:
        flat_work_history = ""

    # flatten preferences
    try:
        flat_preferences = ", ".join(preferences.values())
    except AttributeError:
        flat_preferences = ""

    data_string = f"{flat_skills}, {flat_work_history}, {flat_preferences}"

    return data_string
