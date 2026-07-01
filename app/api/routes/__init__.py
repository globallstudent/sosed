from fastapi import APIRouter

from app.api.routes import auth, comments, feed, internal, likes, posts, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(comments.router)
api_router.include_router(likes.router)
api_router.include_router(feed.router)
api_router.include_router(internal.router)
