import logging
from contextlib import asynccontextmanager

import nest_asyncio
import uvicorn
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.config as config
from app.database import create_db_and_tables
from app.modules.chat import chat_router
from app.modules.indices import indices_router
from app.modules.projects import project_router
from app.modules.questions import generate_router
from app.shared.settings import init_settings

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
app.include_router(router=indices_router)
app.include_router(router=chat_router)
app.include_router(router=generate_router)


@app.get("/")
def heartbeat():
	return {"status": "ok"}


def server():
	_host = config.HOST
	_port = config.PORT
	_env = config.ENVIRONMENT

	print(f"host: {_host}")
	print(f"port: {_port}")
	print(f"env: {_env}")
	uvicorn.run(
		"main:app",
		host=_host,
		port=_port,
		loop="asyncio",
		log_level="info",
		reload=_env == "dev",
	)


if __name__ == "__main__":
	server()
