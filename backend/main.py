from fastapi import FastAPI

app = FastAPI()


# Enabling Cors (if needed)

#origins = [
#    "*"
#]

app.add_middleware(
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=120
)

# Adding routers
