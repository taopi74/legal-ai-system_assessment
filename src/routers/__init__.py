from fastapi import APIRouter

from src.routers.documents import router as documents_router
from src.routers.drafts import router as drafts_router
from src.routers.feedback import router as feedback_router
from src.routers.system import router as system_router

router = APIRouter()
router.include_router(system_router)
router.include_router(drafts_router)
router.include_router(feedback_router)
router.include_router(documents_router)

__all__ = ["router"]
