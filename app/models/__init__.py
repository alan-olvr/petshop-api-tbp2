# Importe aqui TODOS os models para o Alembic (autogenerate) enxergá-los.
from app.models.base import Base  

# Membro A
from app.models.tutor import Tutor  
from app.models.animal import Animal 
from app.models.microchip import Microchip  
from app.models.historico_tutela import HistoricoTutela  
from app.models.veterinario import Veterinario  

__all__ = ["Base", "Tutor", "Animal", "Microchip", "HistoricoTutela", "Veterinario"]

# Membro B
# from app.models.servico import Servico  # noqa: F401
# from app.models.atendimento import Atendimento, AtendimentoServico  # noqa: F401
# from app.models.vacina import Vacina, AplicacaoVacina  # noqa: F401