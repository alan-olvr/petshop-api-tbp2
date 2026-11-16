from datetime import date, timedelta
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.animal import Animal
from app.models.vacina import AplicacaoVacina, Vacina
from app.schemas.vacina import (
    AplicacaoVacinaAtualizacao,
    AplicacaoVacinaEntrada,
    AplicacaoVacinaSaida,
    VacinaAtualizacao,
    VacinaEntrada,
    VacinaSaida,
)

router = APIRouter(tags=["/Vacinas e Vacinações"])

@router.post("/vacinas", response_model=VacinaSaida, status_code=status.HTTP_201_CREATED)
def criar_vacina(dados: VacinaEntrada, db: Session = Depends(get_db)):
    nova_vacina = Vacina(**dados.model_dump())
    db.add(nova_vacina)
    db.commit()
    db.refresh(nova_vacina)
    return nova_vacina

@router.get("/vacinas", response_model=list[VacinaSaida])
def listar_vacinas(
    nome: Optional[str] = Query(None, description="Filtrar por parte do nome da vacina"),
    ativo: Optional[bool] = Query(default=None, description="Filtrar por status ativo/inativo"),
    db: Session = Depends(get_db),
):
    query = select(Vacina)

    if nome:
        query = query.where(Vacina.nome.ilike(f"%{nome}%"))

    if ativo is not None:
        query = query.where(Vacina.ativo == ativo)

    return db.scalars(query).all()


@router.patch("/vacinas/{vacina_id}", response_model=VacinaSaida)
def atualizar_vacina(
    vacina_id: int,
    dados: VacinaAtualizacao,
    db: Session = Depends(get_db),
):
    vacina = db.scalar(select(Vacina).where(Vacina.id == vacina_id))
    if not vacina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vacina não encontrada"
        )

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(vacina, campo, valor)

    db.commit()
    db.refresh(vacina)
    return vacina

@router.delete("/vacinas/{vacina_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_vacina(vacina_id: int, db: Session = Depends(get_db)):
    vacina = db.scalar(select(Vacina).where(Vacina.id == vacina_id))
    if not vacina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vacina não encontrada"
        )

    try:
        db.delete(vacina)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível deletar a vacina, pois existem aplicações associadas a ela.",
        )

@router.get("/vacinacoes/pendentes", response_model=list[AplicacaoVacinaSaida])
def listar_vacinacoes_pendentes(
    animal_id: Optional[int] = Query(None, description="Filtrar pendências de um animal específico"),
    db: Session = Depends(get_db),
):
    query = select(AplicacaoVacina).where(AplicacaoVacina.status == "pendente")

    if animal_id:
        query = query.where(AplicacaoVacina.animal_id == animal_id)

    query = query.order_by(AplicacaoVacina.data_prevista.asc())
    return db.scalars(query).all()

@router.get("/vacinacoes", response_model=list[AplicacaoVacinaSaida])
def listar_vacinacoes(
    status_vacina: Optional[Literal["Prevista", "Aplicada"]] = Query(
        None, alias="status"
    ),
    animal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = select(AplicacaoVacina)

    if status_vacina:
        query = query.where(AplicacaoVacina.status == status_vacina)

    if animal_id:
        query = query.where(AplicacaoVacina.animal_id == animal_id)

    return db.scalars(query).all()