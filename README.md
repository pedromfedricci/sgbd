# Um Sistema de Gerenciamento de Biblioteca (SGBD)

Este projeto implementa uma API para gerenciamento de usuários, livros e empréstimos,
utilizando Python, FastAPI, PostgreSQL, SQLAlchemy (async) e Alembic.

## Funcionalidades

### Usuários

- Cadastrar usuário
- Listar usuários (com paginação)
- Buscar usuário por ID
- Listar empréstimos associados a um usuário
- Regra: E-mail deve ser único

### Livros

- Cadastrar livro
- Listar livros (com paginação)
- Buscar livro por ID
- Buscar livro por título

### Emprestimo

- Realizar empréstimo de livro
- Processar devolução de livro
- Listar empréstimos: ativos, atrasados, histórico por usuário
- Regra: prazo padrão de empréstimo: 14 dias
- Regra: multa: R$ 2,00 por dia de atraso (armazenada em centavos)
- Regra: usuário pode ter no máximo 3 empréstimos ativos
- Regra: um livro não pode ser emprestado se já estiver ativo

## Organização

```text
app/
├── api/            # Camada HTTP (FastAPI routers)
├── dependencies/   # Injeção de dependências
├── db/
│   ├── models/     # Modelos SQLAlchemy
│   ├── session.py  # Sessão async
├── repositories/   # Acesso a dados
├── services/       # Regras de negócio
├── exceptions/
│   └── domain/     # Erros de domínio
├── middleware/     # Middlewares HTTP
│   └── logging.py  # Logging de requisições e correlation ID
├── schemas/        # Schemas Pydantic (request/response)
├── tracing.py      # Configuração OpenTelemetry
├── logging.py      # Configuração Structlog
└── main.py         # Inicialização da aplicação
```

## Arquitetura

### Arquitetura

```text
HTTP Request
     ↓
┌─────────────────────────────────────┐
│  API Layer (app/api/v1/)            │  Validação, serialização, roteamento
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Service Layer (app/services/)      │  Regras de negócio, orquestração
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Repository Layer (app/repositories)│  Queries SQL, abstração do banco
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Database Layer (app/db/)           │  Modelos ORM, sessão async
└─────────────────────────────────────┘
```

### Fluxo de Requisição

Exemplo: `POST /loans` (criar empréstimo)

1. **Router** valida request body com Pydantic
2. **Dependency Injection** injeta `LoanService` com repositórios
3. **Service** aplica regras: usuário existe? livro existe? < 3 empréstimos ativos?
4. **Repository** persiste no banco
5. **Response** serializada e retornada

## Requisitos Não Funcionais Implementados

### Básico

- [x] Paginação em todas as listagens
- [x] Documentação automática com Swagger/OpenAPI
- [x] Validação robusta com Pydantic
- [x] Logging estruturado de operações

### Avançado

- [x] Observabilidade (OpenTelemetry + Jaeger)

## Ambiente de desenvolvimento

### Ferramentas necessárias

- Python
- Uv
- Docker e Compose
- Just (recomendado)
- Direnv (recomendado)

### Preparação de ambiente

Com direnv, basta apenas executar uma única vez:

```bash
direnv allow
```

Ou manualmente:

```bash
source .env.dev
uv sync
```

### Executar a aplicação local

Usando just:

```bash
just dev-up
```

Ou manualmente:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build  -d
```

A aplicação vai ser servida em: http://localhost:8000

### Documentação de API

A documentação OpenAPI é gerada automaticamente pelo FastAPI e pode ser acessada em:

- Swagger: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

### Exemplos de Uso

#### Criar usuário

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@email.com"}'
```

#### Criar livro

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Dom Casmurro", "author": "Machado de Assis"}'
```

#### Realizar empréstimo

```bash
curl -X POST http://localhost:8000/loans \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1}'
```

#### Devolver livro

```bash
curl -X POST http://localhost:8000/loans/1/return
```

#### Listar empréstimos ativos

```bash
curl http://localhost:8000/loans/active
```

#### Listar empréstimos atrasados

```bash
curl http://localhost:8000/loans/overdue
```

## Observabilidade

### Logging

A aplicação utiliza `structlog` para logging estruturado em formato JSON.
Todas as requisições são automaticamente logadas com:

- `request_id`: ID de correlação (gerado ou extraído do header `X-Request-ID`)
- `method`: Método HTTP
- `path`: Caminho da requisição
- `status_code`: Código de resposta
- `duration_ms`: Tempo de processamento

### Tracing

A aplicação utiliza `OpenTelemetry` para rastreamento:

- Instrumentação automática de requisições HTTP (FastAPI)
- Instrumentação automática de queries SQL (SQLAlchemy)
- Spans manuais para operações de negócio nos serviços

#### Jaeger

O ambiente de desenvolvimento inclui `Jaeger` para visualização de traces:

```bash
just dev-up
```

Acesse a UI do Jaeger em: http://localhost:16686

