from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
async def inicio(request: Request):
    base_url = str(request.base_url)
    return {
        "description":'La url de la documentación es la siguiente',
        "url": f"{base_url}docs"
        }

# Registrar las rutas de todos los microservicios
from users.routers import users  # Importa directamente el router de usuarios
app.include_router(users.router, prefix="/users")  # Agrega las rutas bajo el prefijo "/users"

# from orders.routers import orders  # Importa directamente el router de orders
# app.include_router(orders.router, prefix="/orders")  # Agrega las rutas bajo el prefijo "/orders"

# from subscriptions.routers import subscriptions  # Importa directamente el router de orders
# app.include_router(subscriptions.router, prefix="/subscriptions")  # Agrega las rutas bajo el prefijo "/orders"

# from catalog.routers import catalog  # Importa directamente el router de orders
# app.include_router(catalog.router, prefix="/catalog")  # Agrega las rutas bajo el prefijo "/orders"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)