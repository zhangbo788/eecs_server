from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from server.routers import api
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import os
from djadmin.djadmin.wsgi import application as djadmin_app
from server.auth import login_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载django所需的全局变量
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(base_dir, "djadmin/static/")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 挂载django wsgi
app.mount('/django', WSGIMiddleware(djadmin_app))
app.include_router(login_router, prefix="/auth", tags=["auth"])
app.include_router(api.router, prefix="/api", tags=["api"])


@app.get("/ping")
async def server_heart_beat():
    """
    服务器心跳机制，请求/ping,会返回pong
    :param
    :return: "pong"
    """
    return "pong"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, debug=True, reload=True, lifespan="on")
