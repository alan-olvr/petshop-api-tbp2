from fastapi import FastAPI

from app.errors import register_error_handlers
from app.routers import tutor, animal

app = FastAPI(title="PetShop API")
register_error_handlers(app)
app.include_router(tutor.router)
app.include_router(animal.router)

# Registre os routers aqui conforme forem criados:
# from app.routers import tutor, animal
# app.include_router(tutor.router)
# app.include_router(animal.router)


@app.get("/", tags=["Saúde"])
def raiz():
    return {"mensagem": "API Pet Shop no ar"}