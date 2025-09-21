from .chat import router as chat_router
from .students import router as students_router
from .analytics import router as analytics_router

__all__ = ["chat_router", "students_router", "analytics_router"]