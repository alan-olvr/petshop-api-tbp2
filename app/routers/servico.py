from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.servico import Servico
from app.schemas.servico import ServicoEntrada, ServicoAtualizacao, ServicoSaida

router = APIRouter(prefix="/servicos", tags=["Serviços"])

@router.post("/", response_model=ServicoSaida, status_code=status.HTTP_201_CREATED)
def criar_servico(servico: ServicoEntrada, db: Session = Depends(get_db)):

    novo_servico = Servico(**servico.model_dump())
    db.add(novo_servico)
    db.commit()
    db.refresh(novo_servico)
    return novo_servico

@router.get("/", response_model=list[ServicoSaida])
def listar_servicos(
    nome: Optional[str] = Query(default=None, description="Filtrar por parte do nome do serviço"),
    ativo: Optional[bool] = Query(default=None, description="Filtrar por status ativo/inativo"),
    db: Session = Depends(get_db),
):
    query = select(Servico)

    if nome:
        query = query.where(Servico.nome.ilike(f"%{nome}%"))

    if ativo is not None:
        query = query.where(Servico.ativo == ativo)

    return db.execute(query).scalars().all()


@router.get("/{servico_id}", response_model=ServicoSaida)
def obter_servico(servico_id: int, db: Session = Depends(get_db)):
    servico = db.scalar(select(Servico).where(Servico.id == servico_id))
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Serviço não encontrado"
        )
    return servico

@router.patch("/{servico_id}", response_model=ServicoSaida)
def atualizar_servico(
    servico_id: int, 
    servico_atualizacao: ServicoAtualizacao, 
    db: Session = Depends(get_db)
    ):
    servico = db.scalar(select(Servico).where(Servico.id == servico_id))
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Serviço não encontrado"
        )

    campos_atualizados = servico_atualizacao.model_dump(exclude_unset=True)
    for campo, valor in campos_atualizados.items():
        setattr(servico, campo, valor)

   
    db.commit()
    db.refresh(servico)
    return servico

@router.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_servico(servico_id: int, db: Session = Depends(get_db)):
    servico = db.scalar(select(Servico).where(Servico.id == servico_id))
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Serviço não encontrado"
        )
    try:
        db.delete(servico)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir um serviço que já possui atendimentos vinculados. Desative-o (ativo=False)."
        )