import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from src.routes import contacts, auth, custom_tasks, users, api_service
from src.conf.config import config
from src.routes.auth import templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(custom_tasks.router)
app.include_router(auth.router, prefix="/rest_api")
app.include_router(contacts.router, prefix="/rest_api")  # Includes routers form src.routes
app.include_router(users.router, prefix="/rest_api")
app.include_router(api_service.router)

origins = ["*"]

""" Adds a CORS middleware to the FastAPI application,
 allowing cross-origin requests from specified origins,
  with credentials, and for all methods and headers"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    A function that is called when the application starts up.
    It initializes a connection to a Redis database using the
     provided configuration and initializes the FastAPI limiter.
    """
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/", response_class=HTMLResponse)
def localhost_page(request: Request) -> HTMLResponse:
    """
    This function handles the GET request to the root URL.
    It takes a Request object as a parameter and returns a TemplateResponse object.
    """
    return templates.TemplateResponse('start_page.html', context={'request': request})


if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8001, reload=True)  # Starts the Uvicorn server
