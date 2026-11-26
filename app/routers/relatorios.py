from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.animal import Animal
from app.models.atendimento import Atendimento, AtendimentoServico
from app.models.servico import Servico
from app.models.vacina import AplicacaoVacina, Vacina
from app.models.veterinario import Veterinario

router = APIRouter(tags=["Histórico, Relatórios e Estatísticas"])

@router.get("/animais/{animal_id}/historico")
def obter_historico_completo_animal(
    animal_id: int,
    db: Session = Depends(get_db),
):
    animal = db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    atendimentos = db.scalars(
        select(Atendimento)
        .options(
            selectinload(Atendimento.servicos).selectinload(AtendimentoServico.servico),
            selectinload(Atendimento.veterinario),
        )
        .where(Atendimento.animal_id == animal_id)
        .order_by(Atendimento.data_hora.desc())
    ).all()

    aplicacoes = db.execute(
        select(AplicacaoVacina, Vacina.nome, Veterinario.nome)
        .join(Vacina, AplicacaoVacina.vacina_id == Vacina.id)
        .outerjoin(Veterinario, AplicacaoVacina.veterinario_id == Veterinario.id)
        .where(AplicacaoVacina.animal_id == animal_id)
        .order_by(AplicacaoVacina.data_prevista.desc())
    ).all()

    historico_atendimentos = []
    for at in atendimentos:
        itens = [
            {
                "servico_id": item.servico_id,
                "servico": item.servico.nome,
                "quantidade": item.quantidade,
                "valor_cobrado": float(item.valor_cobrado),
                "subtotal": float(item.quantidade * item.valor_cobrado),
            }
            for item in at.servicos
        ]
        historico_atendimentos.append(
            {
                "atendimento_id": at.id,
                "data_hora": at.data_hora,
                "situacao": at.situacao,
                "orientacoes": at.orientacoes,
                "veterinario": {"id": at.veterinario_id, "nome": at.veterinario.nome},
                "tutor_id_epoca": at.tutor_id_epoca,
                "servicos": itens,
                "total": sum(i["subtotal"] for i in itens),
            }
        )

    aplicadas, previstas = [], []
    for ap, vacina_nome, vet_nome in aplicacoes:
        registro = {
            "aplicacao_id": ap.id,
            "vacina_id": ap.vacina_id,
            "vacina": vacina_nome,
            "dose": ap.dose,
            "data_prevista": ap.data_prevista,
            "data_aplicacao": ap.data_aplicacao,
            "veterinario": vet_nome,
        }
        (aplicadas if ap.status == "aplicada" else previstas).append(registro)

    return {
        "animal": {
            "id": animal.id,
            "nome": animal.nome,
            "especie": animal.especie,
            "raca": animal.raca,
        },
        "total_atendimentos": len(historico_atendimentos),
        "atendimentos": historico_atendimentos,
        "vacinacao": {
            "total_aplicadas": len(aplicadas),
            "total_previstas": len(previstas),
            "aplicadas": aplicadas,
            "previstas": previstas,
        },
    }


@router.get("/relatorios/animais-atendidos")
def relatorio_animais_atendidos_periodo(
    data_inicio: datetime = Query(..., description="Ex: 2026-11-01T00:00:00"),
    data_fim: datetime = Query(..., description="Ex: 2026-11-30T23:59:59"),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Animal.id,
            Animal.nome,
            Animal.especie,
            func.count(Atendimento.id).label("qtd_atendimentos"),
        )
        .join(Atendimento, Animal.id == Atendimento.animal_id)
        .where(Atendimento.data_hora.between(data_inicio, data_fim))
        .group_by(Animal.id, Animal.nome, Animal.especie)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "animal_id": r.id,
            "nome": r.nome,
            "especie": r.especie,
            "qtd_atendimentos_no_periodo": r.qtd_atendimentos,
        }
        for r in rows
    ]

@router.get("/relatorios/servicos-periodo")
def relatorio_servicos_por_periodo(
    data_inicio: datetime = Query(..., description="Ex: 2026-11-01T00:00:00"),
    data_fim: datetime = Query(..., description="Ex: 2026-11-30T23:59:59"),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Servico.id,
            Servico.nome,
            func.sum(AtendimentoServico.quantidade).label("total_realizado"),
            func.sum(AtendimentoServico.quantidade * AtendimentoServico.valor_cobrado).label("faturamento_total"),
        )
        .join(AtendimentoServico, Servico.id == AtendimentoServico.servico_id)
        .join(Atendimento, Atendimento.id == AtendimentoServico.atendimento_id)
        .where(Atendimento.data_hora.between(data_inicio, data_fim))
        .group_by(Servico.id, Servico.nome)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "servico_id": r.id,
            "servico": r.nome,
            "quantidade_realizada": int(r.total_realizado or 0),
            "faturamento_periodo": float(r.faturamento_total or 0),
        }
        for r in rows
    ]

@router.get("/relatorios/animais-sem-vacina")
def relatorio_animais_sem_vacina_aplicada(db: Session = Depends(get_db)):
    stmt = (
        select(Animal.id, Animal.nome, Animal.especie)
        .outerjoin(
            AplicacaoVacina,
            and_(
                Animal.id == AplicacaoVacina.animal_id,
                AplicacaoVacina.status == "aplicada",
            ),
        )
        .where(AplicacaoVacina.id.is_(None))
    )
    rows = db.execute(stmt).all()
    return [
        {"animal_id": r.id, "nome": r.nome, "especie": r.especie}
        for r in rows
    ]

@router.get("/estatisticas")
def obter_estatisticas(db: Session = Depends(get_db)):
    
    atend_vet = db.execute(
        select(Veterinario.nome, func.count(Atendimento.id).label("total"))
        .join(Atendimento, Veterinario.id == Atendimento.veterinario_id)
        .group_by(Veterinario.id, Veterinario.nome)
    ).all()

  
    atend_especie = db.execute(
        select(Animal.especie, func.count(Atendimento.id).label("total"))
        .join(Atendimento, Animal.id == Atendimento.animal_id)
        .group_by(Animal.especie)
    ).all()

   
    fat_servico = db.execute(
        select(
            Servico.nome,
            func.sum(AtendimentoServico.quantidade * AtendimentoServico.valor_cobrado).label("faturamento"),
        )
        .join(AtendimentoServico, Servico.id == AtendimentoServico.servico_id)
        .group_by(Servico.id, Servico.nome)
    ).all()

    
    vacinas_status = db.execute(
        select(AplicacaoVacina.status, func.count(AplicacaoVacina.id).label("total"))
        .group_by(AplicacaoVacina.status)
    ).all()

    return {
        "atendimentos_por_veterinario": [
            {"veterinario": r.nome, "total_atendimentos": r.total} for r in atend_vet
        ],
        "atendimentos_por_especie": [
            {"especie": r.especie, "total_atendimentos": r.total} for r in atend_especie
        ],
        "faturamento_por_servico": [
            {"servico": r.nome, "faturamento_total": float(r.faturamento or 0)} for r in fat_servico
        ],
        "vacinas_por_status": [
            {"status": r.status, "total": r.total} for r in vacinas_status
        ],
    }