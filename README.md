# Pet Shop / Clínica Veterinária — API

**Disciplina:** QXD0099 – Desenvolvimento de Software para Persistência (UFC Quixadá)
**Trabalho:** TP2 – Persistência Relacional · **Tema 13**
**Integrantes:** (preencher)

> README completo (entidades, DER, endpoints, filtros, regras de negócio, funcionalidade do tema) será preenchido conforme o projeto avança.

## Tecnologias
Python · FastAPI · SQLAlchemy 2.x (síncrono) · Alembic · PostgreSQL (principal) · SQLite (alternativo)

## Instalação
```bash
python -m venv .venv
.venv\Scripts\activate           # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Linux/Mac: cp .env.example .env
```

## Banco de dados
- **PostgreSQL:** crie o banco (`CREATE DATABASE petshop;`) e use
  `DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/petshop`
- **SQLite:** `DATABASE_URL=sqlite:///./database.db`

## Migrações e povoamento
```bash
alembic upgrade head
python seed.py
```
Nova migração: `alembic revision --autogenerate -m "descrição"`, revisar o script e rodar `alembic upgrade head`.

## Executar
```bash
uvicorn app.main:app --reload
```
Docs interativas: http://localhost:8000/docs

## Testes
```bash
pytest
```

## Estrutura
```
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
```