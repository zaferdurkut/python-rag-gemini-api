from app.app import app
from app.core.config import settings


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=2000, reload=settings.DEBUG)
