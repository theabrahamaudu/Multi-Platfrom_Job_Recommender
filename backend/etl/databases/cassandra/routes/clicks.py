"""
This module contains CRUD routes for the `clicks_metadata` table in Cassandra.
"""
from fastapi import APIRouter
from etl.databases.cassandra.data_models import Click
from etl.databases.cassandra.table_models import ClicksMetadata
from src.utils.backend_log_config import backend as logger

# create router for clicks
clicks = APIRouter()


@clicks.get("/clicks/read_all", tags=["Clicks"])
async def read_all_clicks():
    """
    Retrieve all click entries from the `clicks_metadata` table.

    Returns:
    - List[ClicksMetadata]: A list containing all click entries in the
      `clicks_metadata` table.
    """
    # read all clicks for all users
    all_clicks = list(ClicksMetadata.objects.all())
    logger.info(f"Read {len(all_clicks)} clicks from `clicks_metadata` table")
    return all_clicks


@clicks.get("/clicks/fetch/{user_id}",
            response_model=list[Click],
            tags=["Clicks"])
async def read_clicks(user_id: str):
    """
    Retrieve all click entries for a specific user from the
    `clicks_metadata` table.

    Args:
    - user_id (str): The ID of the user whose click entries need
      to be retrieved.

    Returns:
    - List[Click]: A list containing all click entries for the specified user
      in the `clicks_metadata` table.
    """
    # read all clicks for a user
    user_clicks = list(
        ClicksMetadata.objects(
            ClicksMetadata.user_id == user_id
        )
    )
    logger.info(f"Read clicks for user {user_id}")
    return user_clicks


@clicks.post("/clicks/new", tags=["Clicks"])
async def write_click(click: Click):
    """
    Write a new click entry into the `clicks_metadata` table.

    Args:
    - click (Click): The Click object representing the new click entry.

    Returns:
    - Click: The created Click object representing the newly added click entry.
    """
    # write a new click
    user_click = ClicksMetadata.objects.create(
        user_id=str(click.user_id),
        job_id=str(click.job_id)
    )
    logger.info(f"Write click for user {click.user_id} and job {click.job_id}")
    return user_click


@clicks.put("/clicks/update/{click_id}",
            response_model=Click,
            tags=["Clicks"])
async def update_click(click_id: str, click: Click):
    """
    Update an existing click entry identified by the provided 'click_id'
    with new job information.

    Args:
    - click_id (str): The unique identifier for the click entry to be updated.
    - click (Click): The updated Click object with new job information.

    Returns:
    - Click: The updated Click object representing the modified click entry.
    """
    # load existing click to ensure it exists
    old_click = ClicksMetadata.get(ClicksMetadata.click_id == click_id)
    # update click
    ClicksMetadata.objects(
        click_id=old_click.click_id,
        click_timestamp=old_click.click_timestamp
    ).if_exists().update(
        job_id=str(click.job_id)
    )
    logger.info(
        f"Updated click for user {click.user_id} and job {click.job_id}"
    )
    return ClicksMetadata.get(ClicksMetadata.click_id == click_id)


@clicks.delete("/clicks/delete/{click_id}", tags=["Clicks"])
async def delete_click(click_id: str):
    """
    Delete a specific click entry identified by its unique 'click_id'.

    Args:
    - click_id (str): The unique identifier for the click entry to be deleted.

    Returns:
    - None: If the deletion is successful, no return value is provided.
    """
    # load existing click to ensure it exists
    click = ClicksMetadata.get(ClicksMetadata.click_id == click_id)

    # delete click
    deleted_click = ClicksMetadata.objects(
        click_id=click.click_id,
        click_timestamp=click.click_timestamp
    ).if_exists().delete()

    logger.info(
        f"Delete click for user {click.user_id} and job {click.job_id}"
    )
    return deleted_click
