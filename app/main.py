from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.line_handler import router

app = FastAPI()
app.include_router(router)


@app.get("/")
async def root():
    return JSONResponse(content={"message": "LINE FastAPI Bot is running!"})
