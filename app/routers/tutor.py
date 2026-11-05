from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tutor
from app.schemas.comum import Pagina
from app.schemas.tutor import TutorAtualizacao, TutorEntrada, TutorSaida
from app.errors import RegraNegocioError

router = APIRouter(prefix="/tutor", tags=["Tutores"])

def obter_tutor_ou_404(db: Session, tutor_id: int) -> Tutor:
    tutor = db.get(Tutor, tutor_id)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    return tutor

def garantir_email_livre(db: Session, email: str | None, ignorar_id: int | None = None):
    if not email:
        return
    stmt = select(Tutor.id).where(Tutor.email == email)
    if ignorar_id is not None:
        stmt = stmt.where(Tutor.id != ignorar_id)
    if db.scalar(stmt) is not None:
        raise HTTPException(status_code=409, detail="Já existe um tutor com este e-mail")

@router.post("", response_model=TutorSaida, status_code=201)
def criar_tutor(data: TutorEntrada, db: Session = Depends(get_db)):
    garantir_email_livre(db, data.email)
    tutor = Tutor(**data.model_dump())
    db.add(tutor)
    db.commit()
    db.refresh(tutor)
    return tutor

@router.get("", response_model=Pagina[TutorSaida])
def listar_tutores(
    nome: str | None = Query(None, description="Busca parcial pelo nome"),
    ativo: bool | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filtros = []
    if nome:
        filtros.append(Tutor.nome.ilike(f"%{nome}%"))
    if ativo is not None:
        filtros.append(Tutor.ativo == ativo)

    total = db.scalar(select(func.count()).select_from(Tutor).where(*filtros))
    itens = db.scalars(
        select(Tutor)
        .where(*filtros)
        .order_by(Tutor.nome, Tutor.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return {"total": total, "offset": offset, "limit": limit, "itens": itens}

@router.get("/{tutor_id}", response_model=TutorSaida)
def buscar_tutor(tutor_id: int, db: Session = Depends(get_db)):
    return obter_tutor_ou_404(db, tutor_id)

@router.patch("/{tutor_id}", response_model=TutorSaida)
def atualizar_tutor(tutor_id: int, data: TutorAtualizacao, db: Session = Depends(get_db)):
    alteracoes = data.model_dump(exclude_unset=True)
    if not alteracoes:
        raise HTTPException(status_code=422, detail="Informe pelo menos 1 campo para atualizar")

    tutor = obter_tutor_ou_404(db, tutor_id)
    garantir_email_livre(db, alteracoes.get("email"), ignorar_id=tutor_id)
    for campo, valor in alteracoes.items():
        setattr(tutor, campo, valor)
    db.commit()
    db.refresh(tutor)
    return tutor

@router.delete("/{tutor_id}", status_code=204)
def excluir_tutor(tutor_id: int, db: Session = Depends(get_db)):
    tutor = obter_tutor_ou_404(db, tutor_id)
    if tutor.animais or tutor.vinculos:
        raise RegraNegocioError(
            "Tutor possui animais ou histórico de tutela. Desative-o (ativo=false) em vez de excluir."
        )
    db.delete(tutor)
    db.commit()
    return Response(status_code=204)
