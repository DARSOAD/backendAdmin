from fastapi import FastAPI
from users.routers import users
from content.routers import blog

app = FastAPI()

# Registrar microservicios
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(blog.router, prefix="/content", tags=["Blog"])

@app.get("/")
def root():
    return {"message": "API running!"}
