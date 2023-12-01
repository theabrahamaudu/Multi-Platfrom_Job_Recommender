from fastapi import APIRouter
from fastapi.responses import JSONResponse
from etl.databases.cassandra.data_models import User
from etl.databases.cassandra.table_models import Users
from etl.utils.utilities import scrub_metadata

user = APIRouter()


@user.get("/users/read_all", response_model=list[User], tags=["User"])
async def read_all_users():
    return list(Users.objects.all())


@user.get("/users/fetch/{user_id}", response_model=User, tags=["User"])
async def read_user(user_id: str):
    return Users.get(Users.user_id == user_id)


@user.get("/users/login/{username}", response_model=User, tags=["User"])
async def login_user(username: str):
    try:
        return Users.objects(
            username=username
        ).allow_filtering().first()
    except Exception as e:
        e = str(e)
        return JSONResponse(status_code=404, content={"message": e})


@user.post("/users/clean/{user_id}", tags=["User"])
async def scrub_user_metadata(user_id: str):
    scrub_metadata(user_id)
    return "Metadata scrubbed"


@user.post("/users/new", tags=["User"])
async def create_user(user: User):
    try:
        existing_user = Users.objects(
            username=user.username
        ).allow_filtering().first()
        assert user.email == existing_user.email
        return JSONResponse(
            status_code=409,
            content={"message": "User with this username or email address\
                     already exists!"}
        )
    except Exception as e:
        e = str(e)
        return Users.objects.if_not_exists().create(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password=user.password,
                skills=user.skills,
                work_history=user.work_history,
                preferences=user.preferences
            )


@user.put("/users/update/{user_id}", response_model=User, tags=["User"])
async def update_user(user_id: str, user: User):
    Users.objects(user_id=user_id, username=user.username).if_exists().update(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
        skills=user.skills,
        work_history=user.work_history,
        preferences=user.preferences
    )
    return Users.get(Users.user_id == user_id)


@user.delete("/users/delete/{user_id}", tags=["User"])
async def delete_user(user_id: str):
    user = Users.get(Users.user_id == user_id)
    return Users.objects(user_id=user.user_id,
                         username=user.username).if_exists().delete()
