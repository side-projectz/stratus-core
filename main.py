import logging
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models import create_db_and_tables
from engines.settings import init_settings
import nest_asyncio
import uvicorn
import app.config as config

from app.modules.projects import project_router

nest_asyncio.apply()

logger = logging.getLogger("uvicorn")
logger.setLevel(4)

load_dotenv(find_dotenv())
init_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("[Startup]======================")
    create_db_and_tables()
    yield
    logger.debug("[Shutdown]=====================")


app = FastAPI(title="Stratus-Core", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=project_router)
# app.include_router(router=directory_router)
# app.include_router(router=index_router)
# app.include_router(router=query_router)


@app.get("/")
def heartbeat():
    return {"status": "ok"}


if __name__ == "__main__":
    _host = config.HOST
    _port = config.PORT
    _env = config.ENVIRONMENT

    print(f"host: {_host}")
    print(f"port: {_port}")
    print(f"env: {_env}")
    uvicorn.run("main:app", host=_host, port=_port, loop="asyncio", log_level="info", reload= True if _env == "dev" else False)
