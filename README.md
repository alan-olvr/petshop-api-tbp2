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
```
 
## Banco de dados
 
- **PostgreSQL:** crie o banco (`CREATE DATABASE petshop;`) e configure no `.env`:  
  `DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/petshop`
- **SQLite:** `DATABASE_URL=sqlite:///./database.db`
A troca entre os dois bancos é feita apenas alterando `DATABASE_URL`; models, routers e rotas não mudam.
 
## Migrações e povoamento
 
```bash
alembic upgrade head
python seed.py
```
 
Para criar uma nova migração: `alembic revision --autogenerate -m "descrição"`, revisar o script gerado e rodar `alembic upgrade head`.
 
## Executar
 
```bash
uvicorn app.main:app --reload
```
 
Docs interativas: http://localhost:8000/docs
 
## Estrutura
 
```text
app/
  main.py        # cria o app e inclui os routers
  config.py      # Settings (DATABASE_URL via .env)
  database.py    # engine, SessionLocal, get_db
  errors.py      # tratamento global de erros (F18)
  models/        # SQLAlchemy (um arquivo por entidade)
  schemas/       # Pydantic: Entrada / Atualizacao / Saida
  routers/       # um APIRouter por recurso
migrations/      # Alembic
seed.py          # povoamento (F16)
tests/
docs/            # diagrama do modelo relacional
```
 
## Módulo Clínico, Vacinação e Relatórios
 
### Principais endpoints
 
- **Serviços** (`/servicos`): CRUD completo do catálogo de procedimentos e consultas clínicas.
- **Vacinas e vacinações** (`/vacinas` e `/vacinacoes`): cadastro do catálogo de imunizantes e controle de aplicações e doses futuras.
- **Atendimentos** (`/atendimentos`): registro de consultas e procedimentos vinculados (`AtendimentoServico`), preservando o `tutor_id_epoca`.
**Consultas por relacionamento (F10):**
 
- `GET /animais/{id}/atendimentos`
- `GET /atendimentos/{id}/servicos`
- `GET /veterinarios/{id}/atendimentos`
**Consultas complexas (F11) e estatísticas (F12):**
 
- `GET /relatorios/animais-atendidos`: animais atendidos dentro de um período (JOIN).
- `GET /relatorios/servicos-periodo`: quantidade e faturamento agrupados por serviço no período (JOIN + GROUP BY).
- `GET /relatorios/animais-sem-vacina`: animais sem nenhuma vacina aplicada (LEFT JOIN).
- `GET /estatisticas`: consolidado de atendimentos por veterinário e espécie, faturamento por serviço e vacinas por status.
### Funcionalidade específica do tema (F17)
 
- `GET /animais/{id}/historico`: recupera o histórico clínico completo do pet, consolidando atendimentos realizados, procedimentos cobrados e registros de vacinação (aplicadas e previstas).
- `GET /vacinacoes/pendentes`: lista todas as doses futuras com status `prevista`, ordenadas pela data prevista mais próxima.
### Filtros implementados (F9)
 
- **Serviços e vacinas:** busca parcial por nome (`ilike`) e status ativo.
- **Vacinações:** filtro por `status` (`prevista` ou `aplicada`) e `animal_id`.
- **Atendimentos:** filtro por período (`data_inicio` e `data_fim`), `animal_id` e `veterinario_id`.
### Regras de negócio clínicas (F13)
 
- **Integridade de cadastro:** bloqueio de atendimentos e vacinações para animais, tutores, veterinários ou serviços inativos.
- **Controle de datas:** proibição de registrar `data_aplicacao` de vacina no futuro.
- **Unicidade de dose:** impedimento de registrar a mesma dose da mesma vacina mais de uma vez para o mesmo animal (409 Conflict).
- **Intervalo de reforço:** exigência de aplicação prévia da dose anterior e respeito ao intervalo mínimo (`dias_reforco`) antes de registrar reforços.
## Modelo Relacional
 
```mermaid
erDiagram
    tutores ||--o{ animais : "tutor atual"
    animais ||--o| microchips : "possui (1:1)"
    animais ||--o{ historico_tutela : "vinculos de tutela"
    tutores ||--o{ historico_tutela : "tutor do vinculo"
    animais ||--o{ atendimentos : "recebe"
    veterinarios ||--o{ atendimentos : "realiza"
    tutores ||--o{ atendimentos : "tutor na epoca"
    atendimentos ||--|{ atendimentos_servicos : "itens"
    servicos ||--o{ atendimentos_servicos : "prestado em"
    animais ||--o{ aplicacoes_vacinas : "doses"
    vacinas ||--o{ aplicacoes_vacinas : "catalogo"
    veterinarios |o--o{ aplicacoes_vacinas : "aplica"
 
    tutores {
        int id PK
        varchar nome
        varchar telefone
        varchar email UK
        boolean ativo
    }
 
    animais {
        int id PK
        varchar nome
        varchar especie
        varchar raca
        varchar sexo "CHECK M ou F"
        date data_nasc_aprox
        float peso_kg "adicionado via migracao"
        boolean ativo
        int tutor_id FK "tutor atual"
    }
 
    microchips {
        int id PK
        varchar numero UK "15 digitos"
        date data_implantacao
        int animal_id FK, UK "1:1 com animais"
    }
 
    historico_tutela {
        int id PK
        date data_inicio
        date data_fim "NULL = vinculo vigente"
        varchar motivo "adocao ou transferencia"
        int animal_id FK
        int tutor_id FK
    }
 
    veterinarios {
        int id PK
        varchar nome
        varchar crmv UK
        varchar especialidade
        boolean ativo
    }
 
    servicos {
        int id PK
        varchar nome UK
        numeric valor_padrao
        boolean ativo
    }
 
    atendimentos {
        int id PK
        datetime data_hora
        varchar situacao
        text orientacoes
        int animal_id FK
        int veterinario_id FK
        int tutor_id_epoca FK "tutor no momento do atendimento"
    }
 
    atendimentos_servicos {
        int id PK
        int quantidade
        numeric valor_cobrado
        int atendimento_id FK "ON DELETE CASCADE"
        int servico_id FK
    }
 
    vacinas {
        int id PK
        varchar nome UK
        varchar fabricante
        int dias_reforco
        boolean ativo
    }
 
    aplicacoes_vacinas {
        int id PK
        int dose "UNIQUE animal, vacina, dose"
        date data_prevista
        date data_aplicacao "NULL = prevista"
        varchar status "prevista ou aplicada"
        int animal_id FK
        int vacina_id FK
        int veterinario_id FK "opcional"
    }
```
 