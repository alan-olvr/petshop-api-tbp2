"""Povoamento inicial (F16). Respeitar as chaves estrangeiras.
Uso: python seed.py
Mínimo: 10 registros em uma entidade + dados para filtros, paginação e consultas complexas."""
from app.database import SessionLocal

def main() -> None:
    db = SessionLocal()
    try:
        # TODO: inserir na ordem: Tutor, Veterinario, Servico, Vacina, Animal, Microchip,
        # HistoricoTutela, Atendimento (+AtendimentoServico), AplicacaoVacina
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()