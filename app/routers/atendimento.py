from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.animal import Animal
from app.models.atendimento import Atendimento, AtendimentoServico
from app.models.servico import Servico
from app.models.tutor import Tutor
from app.models.veterinario import Veterinario
from app.schemas.atendimento import (
    AtendimentoAtualizacao,
    AtendimentoEntrada,
    AtendimentoSaida,
    AtendimentoServicoSaida,
)

router = APIRouter(tags=["Atendimentos"])

@router.post("/atendimentos", response_model=AtendimentoSaida, status_code=status.HTTP_201_CREATED)
def criar_atendimento(dados: AtendimentoEntrada, db: Session = Depends(get_db)):
    animal = db.scalar(select(Animal).where(Animal.id == dados.animal_id))
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )
    if hasattr(animal, "ativo") and not animal.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido agendar atendimento para animal inativo."
        )

    tutor = db.scalar(select(Tutor).where(Tutor.id == dados.tutor_id_epoca))
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tutor não encontrado"
        )
    if hasattr(tutor, "ativo") and not tutor.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido agendar atendimento para tutor inativo."
        )

    vet = db.scalar(select(Veterinario).where(Veterinario.id == dados.veterinario_id))
    if not vet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Veterinário não encontrado"
        )
    if hasattr(vet, "ativo") and not vet.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido agendar atendimento para veterinário inativo."
        )

    novo_atendimento = Atendimento(
        situacao=dados.situacao,
        orientacoes=dados.orientacoes,
        animal_id=dados.animal_id,
        veterinario_id=dados.veterinario_id,
        tutor_id_epoca=dados.tutor_id_epoca,
    )
    db.add(novo_atendimento)
    db.flush() 

    for item in dados.servicos:
        servico = db.scalar(select(Servico).where(Servico.id == item.servico_id))
        if not servico:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Serviço com ID {item.servico_id} não encontrado"
            )
        if not servico.ativo:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Serviço com ID {item.servico_id} está inativo"
            )
        assoc = AtendimentoServico(
            atendimento_id=novo_atendimento.id,
            servico_id=item.servico_id,
            quantidade=item.quantidade,
            valor_cobrado=item.valor_cobrado,
        )
        db.add(assoc)
    db.commit()
    db.refresh(novo_atendimento)
    return novo_atendimento

@router.get("/atendimentos", response_model=list[AtendimentoSaida])
def listar_atendimentos(
    data_inicio: Optional[datetime] = Query(None, description="Data/hora inicial"),
    data_fim: Optional[datetime] = Query(None, description="Data/hora final"),
    animal_id: Optional[int] = Query(None),
    veterinario_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = select(Atendimento).options(selectinload(Atendimento.servicos))

    if data_inicio:
        query = query.where(Atendimento.data_hora >= data_inicio)
    if data_fim:
        query = query.where(Atendimento.data_hora <= data_fim)
    if animal_id:
        query = query.where(Atendimento.animal_id == animal_id)
    if veterinario_id:
        query = query.where(Atendimento.veterinario_id == veterinario_id)
    if veterinario_id:
        query = query.where(Atendimento.tutor_id_epoca == veterinario_id)

    return db.scalars(query).all()

@router.get("/atendimentos/{atendimento_id}", response_model=AtendimentoSaida)
def obter_atendimento(atendimento_id: int, db: Session = Depends(get_db)):
    atendimento = db.scalar(
        select(Atendimento).options(selectinload(Atendimento.servicos)).where(Atendimento.id == atendimento_id)
    )
    if not atendimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Atendimento não encontrado"
        )
    return atendimento

@router.patch("/atendimentos/{atendimento_id}", response_model=AtendimentoSaida)
def atualizar_atendimento(
    atendimento_id: int,
    dados: AtendimentoAtualizacao,
    db: Session = Depends(get_db),
):
    atendimento = db.scalar(select(Atendimento).where(Atendimento.id == atendimento_id))
    if not atendimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Atendimento não encontrado"
        )

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(atendimento, campo, valor)

    db.commit()
    db.refresh(atendimento)
    return atendimento

@router.delete("/atendimentos/{atendimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_atedimento(atendimento_id: int, db: Session = Depends(get_db)):
    atendimento = db.scalar(select(Atendimento).where(Atendimento.id == atendimento_id))
    if not atendimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Atendimento não encontrado"
        )

    db.delete(atendimento)
    db.commit()

@router.get("/atendimentos/{atendimento_id}/servicos", response_model=list[AtendimentoSaida])
def listar_atendimentos_do_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.scalar(select(Animal).where(Animal.id == animal_id))
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado"
        )
    query = (
        select(Atendimento)
        .options(selectinload(Atendimento.servicos))
        .where(Atendimento.animal_id == animal.id)
        .order_by(Atendimento.data_hora.desc())
    )
    return db.scalars(query).all()

@router.get("/atendimentos/{atendimento_id}/servicos", response_model=list[AtendimentoServicoSaida])
def listar_servicos_do_atendimento(atendimento_id: int, db: Session = Depends(get_db)):
    atendimento = db.scalar(select(Atendimento).where(Atendimento.id == atendimento_id))
    if not atendimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Atendimento não encontrado"
        )
    query = (
        select(AtendimentoServico)
        .where(AtendimentoServico.atendimento_id == atendimento.id)
    )
    return db.scalars(query).all()

@router.get("/veterinarios/{veterinario_id}/atendimentos", response_model=list[AtendimentoSaida])
def listar_atendimentos_do_veterinario(veterinario_id: int, db: Session = Depends(get_db)):
    vet = db.scalar(select(Veterinario).where(Veterinario.id == veterinario_id))
    if not vet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Veterinário não encontrado"
        )
    query = (
        select(Atendimento)
        .options(selectinload(Atendimento.servicos))
        .where(Atendimento.veterinario_id == vet.id)
        .order_by(Atendimento.data_hora.desc())
    )
    return db.scalars(query).all()