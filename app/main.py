from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routers.auth import router as auth_router
from app.routers.shop import router as shop_router
from app.routers.account import router as account_router

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="쇼핑몰 API", version="0.5.0")
app.include_router(auth_router)
app.include_router(shop_router)
app.include_router(account_router)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(ROOT / "templates" / "index.html")
