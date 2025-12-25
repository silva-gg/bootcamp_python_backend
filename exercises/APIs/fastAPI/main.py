from fastapi import FastAPI
from datetime import datetime
#msvc - model, service, view, controller
app = FastAPI()

fake_db = [
    {"title": "Post 1 sobre Django", "date": datetime.now().isoformat(), "active": True},
    {"title": "Post 2 sobre FastAPI", "date": datetime.now().isoformat(), "active": True},
    {"title": "Post 3 sobre Flask", "date": datetime.now().isoformat(), "active": False},
    {"title": "Post 4 sobre Pyramid", "date": datetime.now().isoformat(), "active": True},
    ]

@app.get("/posts")
def read_posts(skip: int = 0, limit: int = len(fake_db), active: bool = True):
    return [post for post in fake_db[skip: skip + limit] if post["active"] == active]

@app.get("/posts/{framework}")
def read_root(framework: int):
    return {"posts": [{"title": f"Post 1 sobre {framework}", "date": datetime.now().isoformat()},
                      {"title": f"Post 2 sobre {framework}", "date": datetime.now().isoformat()}]}
