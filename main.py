from typing import Optional
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get('/')
async def home() -> dict[str, str]:
    return {'data': 'message'}

@app.get('/contacts')
async def contacts() -> int:
    return 256

posts = [
    {
        'id': 1,
        'title': 'News 1',
        'body': 'Text 1',
    },
    {
        'id': 2,
        'title': 'News 2',
        'body': 'Text 2',
    },
    {
        'id': 3,
        'title': 'News 3',
        'body': 'Text 3',
    }
]

@app.get('/items')
async def items() -> list[dict[str, str | int]]:
    return posts

@app.get('/items/{post_id}')
async def items(post_id: int) -> dict[str, str | int]:
    post = await found_post_by_id(post_id)
    if not post is None:
        return post
    raise HTTPException(status_code=404)

@app.get('/search')
async def search(post_id: Optional[int] = None) -> dict:
    if post_id:
        post = await found_post_by_id(post_id)
        if not post is None:
            return post
        else:
            raise HTTPException(status_code=404)
    else:
        return {'data': 'No post id provided'}
    
async def found_post_by_id(identifier) -> dict | None:
    post = list(filter(lambda x: x['id'] == identifier, posts))
    if len(post) == 1:
        return post[0]