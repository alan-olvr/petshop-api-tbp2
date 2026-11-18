# Pet Shop / Clínica Veterinária — API

**Disciplina:** QXD0099 – Desenvolvimento de Software para Persistência (UFC Quixadá)  
**Trabalho:** TP2 – Persistência Relacional · **Tema 13**  
**Integrantes:** Daniel Fernandes Ferreira e José Alan de Oliveira Silva

## Objetivo
API RESTful para gerenciamento completo de um Pet Shop e Clínica Veterinária utilizando banco de dados relacional, contemplando cadastro de tutores, animais (com microchip e histórico de tutela), profissionais, catálogo de serviços, atendimentos clínicos, controle de vacinação e relatórios gerenciais.

## Tecnologias
Python · FastAPI · SQLAlchemy 2.x (síncrono) · Alembic · PostgreSQL (principal) · SQLite (alternativo)

## Instalação
```bash
python -m venv .venv
.venv\Scripts\activate           # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Linux/Mac: cp .env.example .env
Banco de dados
PostgreSQL: crie o banco (CREATE DATABASE petshop;) e use
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/petshop

SQLite: DATABASE_URL=sqlite:///./database.db

Migrações e povoamento
Bash
alembic upgrade head
python seed.py
Nova migração: alembic revision --autogenerate -m "descrição", revisar o script e rodar alembic upgrade head.

Executar
Bash
uvicorn app.main:app --reload
Docs interativas: http://localhost:8000/docs

Testes
Bash
pytest
Estrutura
app/
  main.py        # cria o app e inclui os routers
  config.py      # Settings (DATABASE_URL via .env)
  database.py    # engine, SessionLocal, get_db
  errors.py      # tratamento global de erros (F18)
  models/        # SQLAlchemy (um arquivo por entidade)
  schemas/       # Pydantic: Entrada / Atualizacao / Saida
  crud/          # acesso a dados e regras de negócio
  routers/       # um APIRouter por recurso
migrations/      # Alembic
seed.py          # povoamento (F16)
tests/
docs/            # DER e anotações
Módulo Clínico, Vacinação e Relatórios
Principais Endpoints
Serviços (/servicos): CRUD completo do catálogo de procedimentos e consultas clínicas.

Vacinas e Vacinações (/vacinas e /vacinacoes): Cadastro do catálogo de imunizantes e controle de aplicações e doses futuras.

Atendimentos (/atendimentos): Registro de consultas e procedimentos vinculados (AtendimentoServico), preservando o tutor_id_epoca.

Consultas por Relacionamento (F10):

GET /animais/{id}/atendimentos

GET /atendimentos/{id}/servicos

GET /veterinarios/{id}/atendimentos

Consultas Complexas (F11) e Estatísticas (F12):

GET /relatorios/animais-atendidos: Animais atendidos dentro de um período (JOIN).

GET /relatorios/servicos-periodo: Quantidade e faturamento agrupados por serviço no período (JOIN + GROUP BY).

GET /relatorios/animais-sem-vacina: Animais sem nenhuma vacina aplicada (LEFT JOIN).

GET /estatisticas: Consolidado de atendimentos por veterinário e espécie, faturamento por serviço e vacinas por status.

Funcionalidade Específica do Tema (F17)
GET /animais/{id}/historico: Recupera o histórico clínico completo do pet, consolidando atendimentos realizados, procedimentos cobrados e registros de vacinação (aplicadas e previstas).

GET /vacinacoes/pendentes: Lista todas as doses futuras com status Prevista, ordenadas pela data prevista mais próxima.

Filtros Implementados (F9)
Serviços e Vacinas: Busca parcial por nome (ilike) e status ativo.

Vacinações: Filtro por status (Prevista ou Aplicada) e animal_id.

Atendimentos: Filtro por período (data_inicio e data_fim), animal_id e veterinario_id.

Regras de Negócio Clínicas (F13)
Integridade de Cadastro: Bloqueio de atendimentos e vacinações para animais, tutores, veterinários ou serviços inativos.

Controle de Datas: Proibição de registrar data_aplicacao de vacina no futuro.

Unicidade de Dose: Impedimento de registrar a mesma dose da mesma vacina mais de uma vez para o mesmo animal (409 Conflict).

Intervalo de Reforço: Exigência de aplicação prévia da dose anterior e respeito ao intervalo mínimo (dias_reforco) antes de registrar reforços.