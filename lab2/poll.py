
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union, Dict
from fastapi.responses import HTMLResponse

POLLS = {}
USERS = {}
max_poll_id = 0

app = FastAPI()


class User(BaseModel):
    username: str


class Poll(BaseModel):
    name: str
    description: Union[str, None] = None
    options: Dict[str, int]


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
        <html>
            <head>
            <title>Doodle</title>
            </head>
            
            <body>
            <div style="width: 80%; margin: auto; background-color: green; font-size: 200%;">Doodle</div>
        </html>
    """


@app.post("/polls")
async def create_poll(
        poll: Poll,
):
    POLLS[poll.name] = poll
    return poll


@app.post("/users")
async def create_user(
        user: User
):
    USERS[user.username] = user
    return user


@app.get("/polls/{pool_id}")
async def get_pool(pool_id: str):
    return POLLS[pool_id]


@app.put("/polls/{poll_id}")
async def update_pool(poll_id: str, option_name: str):
    POLLS[poll_id].options[option_name] += 1
    return POLLS[poll_id]


@app.delete("/polls/{poll_id}")
async def delete_pool(poll_id: str):
    del POLLS[poll_id]
