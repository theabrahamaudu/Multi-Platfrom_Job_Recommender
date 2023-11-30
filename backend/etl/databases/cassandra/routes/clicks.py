from fastapi import APIRouter
from etl.databases.cassandra.data_models import Click
from etl.databases.cassandra.table_models import ClicksMetadata


clicks = APIRouter()


@clicks.get("/clicks/read_all", tags=["Clicks"])
async def read_all_clicks():
    return list(ClicksMetadata.objects.all())


@clicks.get("/clicks/fetch/{user_id}",
            response_model=list[Click],
            tags=["Clicks"])
async def read_clicks(user_id: str):
    return list(
        ClicksMetadata.objects(
            ClicksMetadata.user_id == user_id
        )
    )


@clicks.post("/clicks/new", tags=["Clicks"])
async def write_click(click: Click):
    return ClicksMetadata.objects.create(
        user_id=str(click.user_id),
        job_id=str(click.job_id)
    )


@clicks.put("/clicks/update/{click_id}",
            response_model=Click,
            tags=["Clicks"])
async def update_click(click_id: str, click: Click):
    old_click = ClicksMetadata.get(ClicksMetadata.click_id == click_id)
    ClicksMetadata.objects(
        click_id=old_click.click_id,
        click_timestamp=old_click.click_timestamp
    ).if_exists().update(
        job_id=str(click.job_id)
    )
    return ClicksMetadata.get(ClicksMetadata.click_id == click_id)


@clicks.delete("/clicks/delete/{click_id}", tags=["Clicks"])
async def delete_click(click_id: str):
    click = ClicksMetadata.get(ClicksMetadata.click_id == click_id)
    return ClicksMetadata.objects(
        click_id=click.click_id,
        click_timestamp=click.click_timestamp
    ).if_exists().delete()
