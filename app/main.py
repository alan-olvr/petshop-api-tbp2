from fastapi import FastAPI

from app.errors import register_error_handlers

app = FastAPI(title="Pet Shop / Clínica Veterinária", version="0.1.0")
register_error_handlers(app)

# Registre os routers aqui conforme forem criados:
# from app.routers import tutor, animal
# app.include_router(tutor.router)
# app.include_router(animal.router)


@app.get("/", tags=["Saúde"])
def raiz():
    return {"mensagem": "API Pet Shop no ar"}