from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    age: int

class Post(BaseModel):
    id: int
    title: str
    body: str
    author: User

@app.get('/')
async def home() -> dict[str, str]:
    return {'data': 'message'}

@app.get('/contacts')
async def contacts() -> int:
    return 256

users = [
    {
        'id': 1,
        'name': 'John',
        'age': 34,
    },
    {
        'id': 2,
        'name': 'Alex',
        'age': 12,
    },
    {
        'id': 3,
        'name': 'Bob',
        'age': 45,
    }
]

posts = [
    {
        'id': 1,
        'title': 'News 1',
        'body': 'Text 1',
        'author': users[1],
    },
    {
        'id': 2,
        'title': 'News 2',
        'body': 'Text 2',
        'author': users[0],
    },
    {
        'id': 3,
        'title': 'News 3',
        'body': 'Text 3',
        'author': users[2],
    }
]

@app.get('/items')
async def items() -> list[Post]:
    post_objects = list(map(lambda post: Post(**post), posts))
    return post_objects

@app.get('/items/{post_id}')
async def items(post_id: int) -> Post:
    return await found_post_by_id(post_id)

@app.get('/search')
async def search(post_id: Optional[int] = None) -> Post | dict[str, str]:
    if post_id:
        return await found_post_by_id(post_id)
    else:
        return {'data': 'No post id provided'}
    
async def found_post_by_id(identifier) -> dict | None:
    post = list(filter(lambda x: x['id'] == identifier, posts))
    if len(post) == 1:
        return post[0]
    else:
        raise HTTPException(status_code=404)