from fastapi import FastAPI

from app.api.routes import router as api_router


def get_application() -> FastAPI:
    app = FastAPI(root_path="/api", root_path_in_servers=True)
    app.include_router(api_router, prefix="/judge", tags=["Judge"])
    return app