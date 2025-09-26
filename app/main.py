from fastapi import FastAPI
from app.config.settings import get_settings
from app.presentation.api.routers import auth as auth_router
from app.presentation.api.routers import users as secure_router

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

app.include_router(auth_router.router)
app.include_router(secure_router.router)

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "env": settings.APP_ENV}
