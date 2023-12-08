"""
This module contains the CRUD routes for the `users` table in Cassandra.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from etl.databases.cassandra.data_models import User
from etl.databases.cassandra.table_models import Users
from etl.utils.utilities import scrub_metadata
from src.utils.backend_log_config import backend as logger

# create router
user = APIRouter()


@user.get("/users/read_all", response_model=list[User], tags=["User"])
async def read_all_users():
    """
    Retrieves all users from the `users` table.

    Returns:
    - List[User]: List containing all user details.
    """
    all_users = list(Users.objects.all())
    logger.info(f"Read {len(all_users)} users from `users` table")
    return all_users


@user.get("/users/fetch/{user_id}", response_model=User, tags=["User"])
async def read_user(user_id: str):
    """
    Retrieves a specific user by their user ID from the `users` table.

    Args:
    - user_id (str): The unique identifier for the user.

    Returns:
    - User: Details of the specified user.
    """
    user = Users.get(Users.user_id == user_id)
    logger.info(f"Read user {user_id} from `users` table")
    return user


@user.get("/users/login/{username}", response_model=User, tags=["User"])
async def login_user(username: str):
    """
    Attempts to retrieve user details by their username from the `users` table.

    Args:
    - username (str): The username of the user to be retrieved.

    Returns:
    - User: Details of the user if found.

    Raises:
    - JSONResponse: Returns a 404 status code with an error message
    if the user is not found.
    """
    try:
        # attempt to retrieve user by username
        user = Users.objects(
            username=username
        ).allow_filtering().first()
        logger.info(f"Read user {username} from `users` table")
        return user
    except Exception as e:
        logger.error(f"Error reading user {username} from `users` table: {e}")
        e = str(e)
        return JSONResponse(status_code=404, content={"message": e})


@user.post("/users/clean/{user_id}", tags=["User"])
async def scrub_user_metadata(user_id: str):
    """
    Deletes older search and click metadata for a specific user.

    Args:
    - user_id (str): The ID of the user whose metadata is to be scrubbed.

    Returns:
    - JSONResponse: A message confirming the successful scrubbing of metadata.
    """
    # delete older search and clicks metadata
    scrub_metadata(user_id)
    logger.info(f"Scrubbed metadata for user {user_id}")
    return JSONResponse(
        status_code=200,
        content={"message": f"Metadata scrubbed -- {user_id}"}
    )


@user.post("/users/new", tags=["User"])
async def create_user(user: User):
    """
    Creates a new user if they don't already exist in the database.

    Args:
    - user (User): The user object containing details to be added.

    Returns:
    - JSONResponse or User: If the user already exists, returns a conflict
      response (status code 409) with a message. If a new user is created,
      returns the user object created in the `users` table.
    """
    try:
        # check if user already exists
        existing_user = Users.objects(
            username=user.username
        ).allow_filtering().first()
        assert user.email == existing_user.email
        logger.info(
            f"User {user.username} already exists in `users` table"
            f" with ID {existing_user.user_id}"
        )
        return JSONResponse(
            status_code=409,
            content={"message": "User with this username or email address\
                     already exists!"}
        )
    except Exception as e:
        # create new user
        user = Users.objects.if_not_exists().create(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password=user.password,
                skills=user.skills,
                work_history=user.work_history,
                preferences=user.preferences
            )
        logger.info(
            f"Created new user {user.username} in `users` table"
            f" with ID {user.user_id}. Check message: {e}"
        )
        return user


@user.put("/users/update/{user_id}", response_model=User, tags=["User"])
async def update_user(user_id: str, user: User):
    """
    Updates the details of an existing user in the database.

    Args:
    - user_id (str): The unique identifier for the user to be updated.
    - user (User): The updated user object containing the new details.

    Returns:
    - User: The updated user object fetched from the `users`
      table after the update.
    """
    Users.objects(user_id=user_id, username=user.username).if_exists().update(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
        skills=user.skills,
        work_history=user.work_history,
        preferences=user.preferences
    )
    logger.info(
        f"Updated user {user.username} in `users` table with ID {user_id}"
    )
    return Users.get(Users.user_id == user_id)


@user.delete("/users/delete/{user_id}", tags=["User"])
async def delete_user(user_id: str):
    """
    Deletes a user from the database.

    Args:
    - user_id (str): The unique identifier for the user to be deleted.

    Returns:
    - None: If the deletion is successful, no return value is provided.
    """
    # fetch user to ensure it exists
    user = Users.get(Users.user_id == user_id)
    # delete user
    deleted_user = Users.objects(
        user_id=user.user_id,
        username=user.username
    ).if_exists().delete()
    logger.info(
        f"Deleted user {user.username} from `users` table with ID {user_id}"
    )
    return deleted_user
