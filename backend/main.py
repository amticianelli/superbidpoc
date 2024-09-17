from fastapi import FastAPI
from routers import openaiInteraction
from fastapi.middleware import Middleware

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