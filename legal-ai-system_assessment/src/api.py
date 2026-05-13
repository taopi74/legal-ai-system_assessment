from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.app_state import state
from src.middleware import register_security_and_logging_middleware
from src.routers import router

app = FastAPI(title="Legal AI System")

logger = logging.getLogger("legal-ai")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.setLevel(logging.INFO)

register_security_and_logging_middleware(app, logger)
app.mount("/web", StaticFiles(directory=str(state.paths.web_dir)), name="web")
app.include_router(router)
