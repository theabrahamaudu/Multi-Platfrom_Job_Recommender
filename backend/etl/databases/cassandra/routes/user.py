from fastapi import APIRouter
from backend.etl.databases.cassandra.data_models import User
from backend.etl.databases.cassandra.table_models import Users

user = APIRouter()


@user.get("/users", response_model=list[User], tags=["User"])
async def read_all_users():
    return list(Users.objects.all())


@user.get("/users/{user_id}", response_model=User, tags=["User"])
async def read_user(user_id: str):
    return Users.get(Users.user_id == user_id)


@user.post("/users", tags=["User"])
async def create_user(user: User):
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


@user.put("/users/{user_id}", response_model=User, tags=["User"])
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


@user.delete("/user/{user_id}", tags=["User"])
async def delete_user(user_id: str):
    user = Users.get(Users.user_id == user_id)
    return Users.objects(user_id=user.user_id,
                         username=user.username).if_exists().delete()
