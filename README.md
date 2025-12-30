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

app/
├── api/            # Camada HTTP (FastAPI routers)
├── db/
│   ├── models/     # Modelos SQLAlchemy
│   ├── session.py  # Sessão async
├── repositories/   # Acesso a dados
├── services/       # Regras de negócio
├── exceptions/
│   └── domain/     # Erros de domínio
├── schemas/        # Schemas Pydantic (request/response)
├── deps.py         # Injeção de dependências
└── main.py         # Inicialização da aplicação

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
just dev-up-build
```

Ou manualmente:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build --force-recreate --detach
```

A aplicação vai ser servida em: http://localhost:8000

### Documentação de API

A documentação OpenAPI é gerada automaticamente pelo FastAPI e pode ser acessada em:

- Swagger: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json
