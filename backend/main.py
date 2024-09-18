from fastapi import FastAPI
from routers import openaiInteraction
from fastapi.middleware import Middleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()


# Enabling Cors (if needed)

#origins = [
#    "*"
#]

#app.add_middleware(
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#    max_age=120
#)

# Adding routers
# To start 
# python -m uvicorn main:app --reload --port 80
app.include_router(openaiInteraction.router)

# Mounting frontend

if os.path.isdir("static/build"):
    app.mount("/", StaticFiles(directory="static/build", html=True), name="static")

elif os.path.isdir("../frontend/build"):
    app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
else:
    raise Exception("No frontend build found")



