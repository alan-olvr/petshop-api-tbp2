from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import RegraNegocioError
from app.models import Microchip
from app.routers.animal import obter_animal
from app.schemas.microchip import MicrochipEntrada, MicrochipSaida

router = APIRouter(tags=["Microchips"])


@router.post("/animais/{animal_id}/microchip", response_model=MicrochipSaida, status_code=201)
def registrar_microchip(animal_id: int, data: MicrochipEntrada, db: Session = Depends(get_db)):
    animal = obter_animal(db, animal_id)

    if not animal.ativo:
        raise RegraNegocioError("Animal inativo não pode receber microchip")
    if animal.microchip is not None:
        raise RegraNegocioError("Este animal já possui microchip registrado")
    if db.scalar(select(Microchip.id).where(Microchip.numero == data.numero)) is not None:
        raise RegraNegocioError("Este número de microchip já está registrado em outro animal")

    chip = Microchip(animal_id=animal.id, **data.model_dump())
    db.add(chip)
    db.commit()
    db.refresh(chip)
    return chip


@router.get("/animais/{animal_id}/microchip", response_model=MicrochipSaida)
def consultar_microchip(animal_id: int, db: Session = Depends(get_db)):
    animal = obter_animal(db, animal_id)
    if animal.microchip is None:
        raise HTTPException(status_code=404, detail="Animal sem microchip registrado")
    return animal.microchip


@router.delete("/animais/{animal_id}/microchip", status_code=204)
def remover_microchip(animal_id: int, db: Session = Depends(get_db)):
    animal = obter_animal(db, animal_id)
    if animal.microchip is None:
        raise HTTPException(status_code=404, detail="Animal sem microchip registrado")
    db.delete(animal.microchip)
    db.commit()
    return Response(status_code=204)


@router.get("/microchips/{numero}", response_model=MicrochipSaida)
def buscar_por_numero(numero: str, db: Session = Depends(get_db)):
    chip = db.scalar(select(Microchip).where(Microchip.numero == numero))
    if chip is None:
        raise HTTPException(status_code=404, detail="Microchip não encontrado")
    return chip