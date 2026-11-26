# Pet Shop / Clínica Veterinária — API

**Disciplina:** QXD0099 – Desenvolvimento de Software para Persistência (UFC Quixadá)  
**Trabalho:** TP2 – Persistência Relacional · **Tema 13:** Sistema de Pet Shop / Clínica Veterinária  
**Integrantes:** Daniel Fernandes Ferreira e José Alan de Oliveira Silva

## Objetivo

API RESTful para gerenciamento completo de um Pet Shop e Clínica Veterinária utilizando banco de dados relacional, contemplando cadastro de tutores, animais (com microchip e histórico de tutela), profissionais, catálogo de serviços, atendimentos clínicos, controle de vacinação e relatórios gerenciais.

## Tecnologias

Python · FastAPI · Pydantic · SQLAlchemy 2.x (síncrono) · Alembic · psycopg 3 · Uvicorn · pytest · PostgreSQL (principal) · SQLite (alternativo)

## Instalação

Pré-requisitos: Python 3.10+ (testado com 3.12) e PostgreSQL instalado. O SQLite já acompanha o Python.

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

A troca entre os dois bancos é feita apenas alterando `DATABASE_URL`; models, routers e rotas não mudam. Se o `.env` não existir, a aplicação usa SQLite por padrão. Para o SQLite, o `PRAGMA foreign_keys=ON` é ativado automaticamente em cada conexão (`app/database.py`), garantindo que as chaves estrangeiras sejam respeitadas como no PostgreSQL. As migrações usam `batch_alter_table`, o que as torna compatíveis com os dois bancos.

## Migrações e povoamento

```bash
alembic upgrade head
python seed.py
```

O histórico de migrações (`migrations/versions/`) é composto por:

| Revisão | Descrição |
|---|---|
| `f7f48720bb6e` | Migração inicial: `tutores`, `veterinarios`, `animais`, `historico_tutela` e `microchips`. |
| `4fc6ba1aa698` | Evolução (F14): adiciona a coluna `peso_kg` em `animais`. |
| `fa3221c90c2d` | Cria as tabelas `servicos`, `vacinas`, `aplicacoes_vacinas`, `atendimentos` e `atendimentos_servicos`. |
| `42c06d3c2c21` | Evolução: adiciona a coluna `dose` em `aplicacoes_vacinas` e a restrição única (`animal_id`, `vacina_id`, `dose`). |

As alterações são aplicadas sobre o banco existente, sem necessidade de excluí-lo ou recriá-lo.

Para criar uma nova migração: `alembic revision --autogenerate -m "descrição"`, revisar o script gerado e rodar `alembic upgrade head`.  
Para reverter a última migração: `alembic downgrade -1`. Para ver a versão atual do banco: `alembic current`.

O `seed.py` (F16) insere os dados iniciais respeitando as chaves estrangeiras e só atua se o banco estiver vazio, então executá-lo novamente não duplica registros. Ele cria:

| Tabela | Registros |
|---|---|
| `tutores` | 8 (1 inativo) |
| `veterinarios` | 5 (1 inativo) |
| `animais` | 14 (1 inativo) |
| `microchips` | 10 |
| `historico_tutela` | 17 (inclui 3 transferências) |
| `servicos` | 8 (1 inativo) |
| `vacinas` | 4 |
| `aplicacoes_vacinas` | 23 (aplicadas e previstas) |
| `atendimentos` | 17 |
| `atendimentos_servicos` | 28 |

Execute o seed sempre **depois** das migrações.

## Executar

```bash
uvicorn app.main:app --reload
```

Docs interativas: http://localhost:8000/docs

Testes: `pytest`

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
.env.example     # modelo de configuração da DATABASE_URL
alembic.ini
requirements.txt
```

## Entidades

| Entidade | Descrição |
|---|---|
| `Tutor` | Responsável pelo animal: nome, telefone, e-mail (único) e situação (ativo/inativo). |
| `Animal` | Pet atendido: nome, espécie, raça, sexo (M/F), data aproximada de nascimento, peso, situação e tutor atual. |
| `Microchip` | Identificação única do animal: número de 15 dígitos (único) e data de implantação. |
| `HistoricoTutela` | Registro de cada vínculo animal–tutor, com período (início e fim) e motivo (adoção ou transferência). |
| `Veterinario` | Profissional responsável por atendimentos e vacinações: nome, CRMV (único), especialidade e situação. |
| `Servico` | Catálogo de serviços (consulta, exames, procedimentos) com valor padrão. |
| `Vacina` | Catálogo de imunizantes: nome (único), fabricante e intervalo de reforço (`dias_reforco`). |
| `Atendimento` | Consulta realizada: data/hora, situação apresentada, orientações, animal, veterinário e tutor da época. |
| `AtendimentoServico` | Tabela associativa entre atendimento e serviço: quantidade e valor cobrado. |
| `AplicacaoVacina` | Tabela associativa entre animal e vacina: dose, data prevista, data de aplicação, status e veterinário. |

## Relacionamentos

| Tipo | Relacionamento |
|---|---|
| 1:1 | `Animal` ↔ `Microchip` (cada animal possui no máximo um microchip, e cada microchip pertence a um único animal). |
| 1:N | `Tutor` → `Animal` (tutor atual). |
| 1:N | `Animal` → `HistoricoTutela` (vínculos de tutela ao longo do tempo). |
| 1:N | `Animal` → `Atendimento`. |
| 1:N | `Veterinario` → `Atendimento`. |
| N:N | `Atendimento` ↔ `Servico`, via `AtendimentoServico` (quantidade e valor cobrado). |
| N:N | `Animal` ↔ `Vacina`, via `AplicacaoVacina` (dose, datas, status e veterinário). |

**Tutela sem alterar o passado:** cada atendimento guarda o `tutor_id_epoca`, e o `HistoricoTutela` registra início e fim de cada vínculo. Assim, a troca de tutor não altera os atendimentos já realizados.  
**Prevista x aplicada:** `AplicacaoVacina` possui `status` (`prevista` ou `aplicada`) e `data_aplicacao` só é preenchida quando a vacina foi de fato aplicada.

## Módulo de Cadastros (Tutores, Animais e Profissionais)

### Principais endpoints

- **Tutores** (`/tutores`): CRUD de tutores. O `DELETE` só exclui tutores sem animais e sem histórico de tutela.
- **Animais** (`/animais`): CRUD de animais, com paginação e filtros. O `DELETE` desativa o animal (`ativo=false`) em vez de removê-lo.
- **Microchips:** `POST`, `GET` e `DELETE` em `/animais/{id}/microchip` e consulta pelo número em `GET /microchips/{numero}`.
- **Veterinários** (`/veterinarios`): CRUD de profissionais. O `DELETE` desativa o veterinário.
- **Tutela:**
  - `POST /animais/{id}/transferir-tutela`: encerra o vínculo vigente e abre um novo (adoção ou transferência).
  - `GET /animais/{id}/tutelas`: histórico de vínculos do animal.

**Consultas por relacionamento (F10):**

- `GET /tutores/{id}/animais`

### Paginação (F8)

As listagens de tutores, animais, veterinários e de animais por tutor são paginadas diretamente no banco (`OFFSET`/`LIMIT`):

- `GET /animais?offset=0&limit=10` (padrão: `offset=0` e `limit=10`; máximo de 100 por página)

A resposta traz o total de registros que atendem aos filtros e os itens da página:

```json
{ "total": 14, "offset": 0, "limit": 10, "itens": [ ... ] }
```

### Filtros implementados (F9)

Os filtros são aplicados na consulta ao banco e podem ser combinados.

- **Animais:** `nome` (busca parcial com `ilike`), `especie`, `tutor_id` e `ativo`.
- **Tutores:** `nome` (busca parcial) e `ativo`.
- **Veterinários:** `nome` (busca parcial), `especialidade` (busca parcial) e `ativo`.

### Regras de negócio de cadastro (F13)

- **Tutela vigente única:** cada animal possui apenas um vínculo com `data_fim` nula, garantido por índice único parcial no banco (`uq_historico_tutela_vigente`).
- **Vínculo inicial automático:** ao cadastrar um animal, o primeiro vínculo de tutela é aberto com o tutor informado.
- **Transferência de tutela:** o animal e o novo tutor precisam estar ativos, o novo tutor deve ser diferente do atual, e a data da transferência não pode ser futura nem anterior ao início do vínculo atual. O vínculo antigo é encerrado e o novo aberto sem alterar os atendimentos anteriores.
- **Tutor ativo:** não é possível vincular um animal a um tutor inativo.
- **Exclusão consistente:** não é permitido excluir tutor que possua animais ou histórico de tutela (409 Conflict); ele deve ser desativado.
- **Microchip:** um por animal, número único com 15 dígitos, data de implantação não futura e animal ativo.
- **Unicidade:** e-mail do tutor e CRMV do veterinário não podem se repetir.

## Módulo Clínico, Vacinação e Relatórios

### Principais endpoints

- **Serviços** (`/servicos/`): CRUD do catálogo de procedimentos e consultas clínicas. A exclusão é bloqueada (409) se o serviço já estiver vinculado a atendimentos.
- **Vacinas e vacinações** (`/vacinas` e `/vacinacoes`): cadastro do catálogo de imunizantes e controle de aplicações e doses futuras. A exclusão de vacina é bloqueada (409) se houver aplicações associadas, e o `PATCH /vacinacoes/{id}` dá baixa em uma dose prevista.
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

Os relatórios por período recebem `data_inicio` e `data_fim` (ex.: `2026-11-01T00:00:00`).

### Funcionalidade específica do tema (F17)

- `GET /animais/{id}/historico`: recupera o histórico clínico completo do pet, consolidando atendimentos realizados (com serviços e totais), procedimentos cobrados e registros de vacinação (aplicadas e previstas).
- `GET /vacinacoes/pendentes`: lista todas as doses futuras com status `prevista`, ordenadas pela data prevista mais próxima. Aceita o filtro opcional `animal_id`.

### Filtros implementados (F9)

- **Serviços e vacinas:** busca parcial por nome (`ilike`) e status ativo.
- **Vacinações:** filtro por `status` (`prevista` ou `aplicada`) e `animal_id`.
- **Atendimentos:** filtro por período (`data_inicio` e `data_fim`), `animal_id` e `veterinario_id`.

### Regras de negócio clínicas (F13)

- **Integridade de cadastro:** bloqueio de atendimentos e vacinações para animais, tutores, veterinários, serviços ou vacinas inativos (400 Bad Request).
- **Controle de datas:** proibição de registrar `data_aplicacao` de vacina no futuro.
- **Unicidade de dose:** impedimento de registrar a mesma dose da mesma vacina mais de uma vez para o mesmo animal (409 Conflict).
- **Intervalo de reforço:** exigência de aplicação prévia da dose anterior e respeito ao intervalo mínimo (`dias_reforco`) antes de registrar reforços.
- **Coerência de status:** uma vacina `aplicada` exige `data_aplicacao`, e uma vacina `prevista` não pode possuí-la.
- **Tutor da época:** ao registrar um atendimento, o tutor vigente do animal é gravado em `tutor_id_epoca`.

## Tratamento de erros (F18)

Os erros são tratados de forma global em `app/errors.py`. Mensagens internas do SGBD nunca são expostas ao usuário, apenas registradas em log.

| Código | Situação |
|---|---|
| `200` / `201` / `204` | Operação realizada com sucesso / recurso criado / sucesso sem conteúdo. |
| `400` | Violação de regra de negócio nos módulos de atendimento e vacinação (entidade inativa, data futura, intervalo de reforço). |
| `404` | Recurso ou entidade associada inexistente. |
| `409` | Conflito: duplicidade, violação de chave estrangeira, exclusão com dependências ou regra de negócio dos cadastros. |
| `422` | Identificador inválido, dados inválidos ou fora do formato esperado. |
| `500` | Falha de persistência ou erro interno inesperado (mensagem genérica). |
| `503` | Banco de dados indisponível (erro de conexão). |

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
        date data_fim "NULL = vinculo vigente (unico por animal)"
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