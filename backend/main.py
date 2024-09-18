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


# Pushing the image
# az login
# az acr login --name ailabsms
# az acr update -n ailabsms --admin-enabled true
# docker tag test:test ailabsms.azurecr.io/superbidpoc/mainapp
# docker push ailabsms.azurecr.io/superbidpoc/mainapp


# installs fnm (Fast Node Manager)
#curl -fsSL https://fnm.vercel.app/install | bash

# activate fnm
#source ~/.bashrc

# download and install Node.js
#fnm use --install-if-missing 20

# verifies the right Node.js version is in the environment
#node -v # should print `v20.17.0`

# verifies the right npm version is in the environment
#npm -v # should print `10.8.2`
