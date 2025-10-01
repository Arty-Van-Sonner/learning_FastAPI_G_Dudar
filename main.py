from typing import Annotated, Optional
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    age: int

class UserCreate(BaseModel):
    name: Annotated[
        str,
        Field(..., title='User name', min_length=2, max_length=64)
    ]
    age: Annotated[
        int,
        Field(..., title='User age', ge=1, le=120)
    ]

class Post(BaseModel):
    id: int
    title: str
    body: str
    author: User

class PostCreate(BaseModel):
    title: str
    body: str
    author_id: int

class PostEdit(BaseModel):
    title: str | None
    body: str | None
    author_id: int | None

class PostDelete(BaseModel):
    post_id: int
    detail: str = 'deleted'

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
async def items(post_id: Annotated[int, Path(..., title='This is post id', ge=1, lt=100)]) -> Post:
    return get_post_by_id(post_id)

@app.get('/search')
async def search(post_id: 
                 Annotated[
                     int | None,
                     Query() 
                    ]
                 ) -> Post | dict[str, str]:
    if post_id:
        return get_post_by_id(post_id)
    else:
        return {'data': 'No post id provided'}
    
def get_post_by_id(post_id) -> dict | None:
    post = list(filter(lambda x: x['id'] == post_id, posts))
    if len(post) == 1:
        return post[0]
    else:
        raise HTTPException(status_code=404, detail='Post not found')
    
def get_author_by_id(author_id) -> dict | None:
    authors = list(filter(lambda x: x['id'] == author_id, users))
    if len(authors) == 1:
        return authors[0]
    else:
        raise HTTPException(status_code=404, detail='User not found')
    
@app.post('/items/add')
async def add_item(post: Annotated[PostCreate, Body()]) -> Post:  
    author = get_author_by_id(post.author_id)
    new_post = {
        'id': max(map(lambda p: p['id'], posts)) + 1,
        'title': post.title,
        'body': post.body,
        'author': author,
    }
    posts.append(new_post)
    return Post(**new_post)

@app.post('/user/add')
async def add_user(user: Annotated[
    UserCreate,
    Body(..., example={
        'name': 'Username',
        'age': 18,
    })
]) -> User:  
    new_user = {
        'id': max(map(lambda p: p['id'], users)) + 1,
        'name': user.name,
        'age': user.age,
    }
    users.append(new_user)
    return User(**new_user)

@app.put('/items/{post_id}/edit')
async def edit_post(post_id: Annotated[int, Path()], post: PostEdit = Body()):
    dict_post = post.model_dump()
    changes_present = False
    for post_value in dict_post.values():
        if not post_value is None:
            changes_present = True
    if not changes_present:
        raise HTTPException(status_code=400, detail='No changes')
    
    edited_post = get_post_by_id(post_id)
    for post_key in dict_post:
        if not dict_post[post_key] is None:
            if post_key == 'author_id':
                author = get_author_by_id(dict_post[post_key])
                edited_post['author'] = author
            else:
                edited_post[post_key] = dict_post[post_key]

    return Post(**edited_post)

@app.delete('/items/{post_id}/delete')
async def post_delete(post_id: Annotated[int, Path()]) -> PostDelete:
    post = get_post_by_id(post_id)
    posts.remove(post)
    return PostDelete(post_id=post_id, detail='deleted')
