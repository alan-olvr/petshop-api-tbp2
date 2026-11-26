from datetime import date, timedelta
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.veterinario import Veterinario
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

router = APIRouter(tags=["Vacinas e Vacinações"])


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
    query = select(AplicacaoVacina).where(AplicacaoVacina.status == "prevista")

    if animal_id:
        query = query.where(AplicacaoVacina.animal_id == animal_id)

    query = query.order_by(AplicacaoVacina.data_prevista.asc())
    return db.scalars(query).all()


@router.get("/vacinacoes", response_model=list[AplicacaoVacinaSaida])
def listar_vacinacoes(
    status_vacina: Optional[Literal["prevista", "aplicada"]] = Query(
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



@router.post("/vacinacoes", response_model=AplicacaoVacinaSaida, status_code=status.HTTP_201_CREATED)
def registrar_aplicacao_vacina(dados: AplicacaoVacinaEntrada, db: Session = Depends(get_db)):
   
    animal = db.scalar(select(Animal).where(Animal.id == dados.animal_id))
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado.")
    if hasattr(animal, "ativo") and not animal.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido registrar vacinas para um animal inativo."
        )

    vacina = db.scalar(select(Vacina).where(Vacina.id == dados.vacina_id))
    if not vacina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacina não encontrada no catálogo.")
    if not vacina.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta vacina está inativa no catálogo."
        )

  
    if dados.data_aplicacao and dados.data_aplicacao > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data de aplicação não pode ser uma data futura."
        )

  
    dose_existente = db.scalar(
        select(AplicacaoVacina).where(
            AplicacaoVacina.animal_id == dados.animal_id,
            AplicacaoVacina.vacina_id == dados.vacina_id,
            AplicacaoVacina.dose == dados.dose,
        )
    )
    if dose_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A dose {dados.dose} da vacina '{vacina.nome}' já está registrada para este animal."
        )

    
    if dados.dose > 1 and vacina.dias_reforco:
        dose_anterior = db.scalar(
            select(AplicacaoVacina).where(
                AplicacaoVacina.animal_id == dados.animal_id,
                AplicacaoVacina.vacina_id == dados.vacina_id,
                AplicacaoVacina.dose == dados.dose - 1,
            )
        )
        if not dose_anterior or dose_anterior.status != "aplicada" or not dose_anterior.data_aplicacao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A dose {dados.dose - 1} precisa ter sido aplicada antes de registrar a dose {dados.dose}."
            )

        data_minima = dose_anterior.data_aplicacao + timedelta(days=vacina.dias_reforco)
        data_referencia = dados.data_aplicacao or dados.data_prevista

        if data_referencia < data_minima:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Intervalo mínimo de reforço ({vacina.dias_reforco} dias) não respeitado. Data mínima permitida: {data_minima}."
            )

    nova_aplicacao = AplicacaoVacina(**dados.model_dump())
    db.add(nova_aplicacao)
    db.commit()
    db.refresh(nova_aplicacao)
    return nova_aplicacao



@router.patch("/vacinacoes/{aplicacao_id}", response_model=AplicacaoVacinaSaida)
def atualizar_aplicacao_vacina(
    aplicacao_id: int,
    dados: AplicacaoVacinaAtualizacao,
    db: Session = Depends(get_db),
):
    aplicacao = db.scalar(select(AplicacaoVacina).where(AplicacaoVacina.id == aplicacao_id))
    if not aplicacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de vacinação não encontrado.")

    campos = dados.model_dump(exclude_unset=True)

    # Estado final do registro, misturando o que já existe com o que está sendo enviado
    status_final = campos.get("status", aplicacao.status)
    data_final = campos.get("data_aplicacao", aplicacao.data_aplicacao)

    if status_final == "aplicada" and data_final is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uma vacina aplicada precisa ter data_aplicacao."
        )
    if status_final == "prevista" and data_final is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uma vacina prevista não pode ter data_aplicacao."
        )
    if data_final is not None and data_final > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data de aplicação não pode ser no futuro."
        )

    vet_id = campos.get("veterinario_id")
    if vet_id is not None:
        vet = db.get(Veterinario, vet_id)
        if not vet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinário não encontrado.")
        if not vet.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Veterinário inativo não pode ser vinculado à vacinação."
            )

    for campo, valor in campos.items():
        setattr(aplicacao, campo, valor)

    db.commit()
    db.refresh(aplicacao)
    return aplicacao