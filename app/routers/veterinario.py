from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import RegraNegocioError
from app.models import Veterinario
from app.schemas.comum import Pagina
from app.schemas.veterinario import VeterinarioAtualizacao, VeterinarioEntrada, VeterinarioSaida

router = APIRouter(prefix="/veterinarios", tags=["Veterinários"])

def obter_veterinario_ou_404(db: Session, veterinario_id: int) -> Veterinario:
    vet = db.get(Veterinario, veterinario_id)
    if vet is None:
        raise HTTPException(status_code=404, detail="Veterinário não encontrado")
    return vet

def garantir_crmv_livre(db: Session, crmv: str, ignorar_id: int | None = None):
    stmt = select(Veterinario.id).where(Veterinario.crmv == crmv)
    if ignorar_id is not None:
        stmt = stmt.where(Veterinario.id != ignorar_id)
    if db.scalar(stmt) is not None:
        raise RegraNegocioError("Já existe um veterinário com este CRMV")

@router.post("", response_model=VeterinarioSaida, status_code=201)
def criar_veterinario(data: VeterinarioEntrada, db: Session = Depends(get_db)):
    garantir_crmv_livre(db, data.crmv)
    vet = Veterinario(**data.model_dump())
    db.add(vet)
    db.commit()
    db.refresh(vet)
    return vet

@router.get("", response_model=Pagina[VeterinarioSaida])
def listar_veterinarios(
    nome: str | None = Query(None, description="Busca parcial pelo nome"),
    especialidade: str | None = Query(None, description="Busca parcial pela especialidade"),
    ativo: bool | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filtros = []
    if nome:
        filtros.append(Veterinario.nome.ilike(f"%{nome}%"))
    if especialidade:
        filtros.append(Veterinario.especialidade.ilike(f"%{especialidade}%"))
    if ativo is not None:
        filtros.append(Veterinario.ativo == ativo)

    total = db.scalar(select(func.count()).select_from(Veterinario).where(*filtros))
    itens = db.scalars(
        select(Veterinario).where(*filtros).order_by(Veterinario.nome, Veterinario.id)
        .offset(offset).limit(limit)
    ).all()
    return {"total": total, "offset": offset, "limit": limit, "itens": itens}

@router.get("/{veterinario_id}", response_model=VeterinarioSaida)
def buscar_veterinario(veterinario_id: int, db: Session = Depends(get_db)):
    return obter_veterinario_ou_404(db, veterinario_id)

@router.patch("/{veterinario_id}", response_model=VeterinarioSaida)
def atualizar_veterinario(
    veterinario_id: int, data: VeterinarioAtualizacao, db: Session = Depends(get_db)
):
    alteracoes = data.model_dump(exclude_unset=True)
    if not alteracoes:
        raise HTTPException(status_code=422, detail="Informe pelo menos 1 campo para atualizar")

    vet = obter_veterinario_ou_404(db, veterinario_id)
    if "crmv" in alteracoes:
        garantir_crmv_livre(db, alteracoes["crmv"], ignorar_id=veterinario_id)
    for campo, valor in alteracoes.items():
        setattr(vet, campo, valor)
    db.commit()
    db.refresh(vet)
    return vet

@router.delete("/{veterinario_id}", status_code=204)
def desativar_veterinario(veterinario_id: int, db: Session = Depends(get_db)):
    # Desativação: o veterinário será referenciado por atendimentos e vacinas (Membro B).
    vet = obter_veterinario_ou_404(db, veterinario_id)
    vet.ativo = False
    db.commit()
    return Response(status_code=204)