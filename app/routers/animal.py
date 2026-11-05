from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.errors import RegraNegocioError
from app.models import Animal, HistoricoTutela, Tutor
from app.schemas.animal import AnimalAtualizacao, AnimalEntrada, AnimalSaida
from app.schemas.comum import Pagina

router = APIRouter(prefix="/animais", tags=["Animais"])

_CARREGAR = (joinedload(Animal.tutor), joinedload(Animal.microchip))

def obter_animal(db: Session, animal_id: int) -> Animal:
    animal = db.scalar(
        select(Animal)
        .options(*_CARREGAR)
        .where(Animal.id == animal_id)
        .execution_options(populate_existing=True)
    )
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal

def obter_tutor(db: Session, tutor_id: int) -> Tutor:
    tutor = db.get(Tutor, tutor_id)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor informado não existe")
    if not tutor.ativo:
        raise RegraNegocioError("Não é possível vincular o animal a um tutor inativo.")
    return tutor

@router.post("", response_model=AnimalSaida, status_code=201)
def criar_animal(data: AnimalEntrada, db: Session = Depends(get_db)):
    obter_tutor(db, data.tutor_id)

    animal = Animal(**data.model_dump())
    animal.historico_tutela.append(
        HistoricoTutela(tutor_id=data.tutor_id, data_inicio=date.today(), motivo="adocao")
    )
    db.add(animal)
    db.commit()
    return obter_animal(db, animal.id)

@router.get("", response_model=Pagina[AnimalSaida])
def listar_animais(
    nome: str | None = Query(None, description="Busca parcial pelo nome"),
    especie: str | None = Query(None, description="Espécie (sem diferenciar maiúsculas)"),
    tutor_id: int | None = None,
    ativo: bool | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):

    filtros = []
    if nome:
        filtros.append(Animal.nome.ilike(f"%{nome}%"))
    if especie:
        filtros.append(func.lower(Animal.especie) == especie.lower())
    if tutor_id is not None:
        filtros.append(Animal.tutor_id == tutor_id)
    if ativo is not None:
        filtros.append(Animal.ativo == ativo)

    total = db.scalar(select(func.count()).select_from(Animal).where(*filtros))
    itens = db.scalars(
        select(Animal)
        .options(*_CARREGAR)
        .where(*filtros)
        .order_by(Animal.nome, Animal.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return {"total": total, "offset": offset, "limit": limit, "itens": itens}

@router.get("/{animal_id}", response_model=AnimalSaida)
def buscar_animal(animal_id: int, db: Session = Depends(get_db)):
    return obter_animal(db, animal_id)

@router.patch("/{animal_id}", response_model=AnimalSaida)
def atualizar_animal(animal_id: int, data: AnimalAtualizacao, db: Session = Depends(get_db)):
    alteracoes = data.model_dump(exclude_unset=True)
    if not alteracoes:
        raise HTTPException(status_code=422, detail="Informe pelo menos 1 campo para atualizar")

    animal = obter_animal(db, animal_id)
    for campo, valor in alteracoes.items():
        setattr(animal, campo, valor)
    db.commit()
    return obter_animal(db, animal_id)

@router.delete("/{animal_id}", status_code=204)
def desativar_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = obter_animal(db, animal_id)
    animal.ativo = False
    db.commit()
    return Response(status_code=204)
