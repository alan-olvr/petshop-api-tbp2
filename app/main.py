from fastapi import FastAPI

from app.errors import register_error_handlers
from app.routers import (
    animal,
    atendimento,
    microchip,
    relatorios,
    servico,
    tutor,
    vacina,
    veterinario,
)

app = FastAPI(title="PetShop API")
register_error_handlers(app)


app.include_router(tutor.router)
app.include_router(animal.router)
app.include_router(microchip.router)
app.include_router(veterinario.router)


app.include_router(servico.router)
app.include_router(vacina.router)
app.include_router(atendimento.router)
app.include_router(relatorios.router)


@app.get("/", tags=["Saúde"])
def raiz():
    return {"mensagem": "API Pet Shop no ar"}