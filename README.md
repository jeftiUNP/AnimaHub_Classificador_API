# AnimaHub Classificador API

API REST do projeto AnimaHub Classificador, voltada à classificação e à recomendação de concursos públicos.

## Stack

- Python 3.12+
- FastAPI
- Uvicorn
- Pytest e HTTPX para testes

O plano da API prevê a evolução da aplicação com SQLAlchemy, Pydantic, CRUD de perfis, consulta de concursos e recomendações.

## Estrutura

```text
app/
├── api/
│   └── routes/
├── main.py
tests/
requirements.txt
requirements-dev.txt
```

## Configuração local

Recomenda-se usar um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Executar a API

```bash
python -m uvicorn app.main:app --reload
```

Depois, acesse:

- API: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

## Executar os testes

```bash
python -m pytest
```

## Commits

Este projeto usa Commits Semânticos, por exemplo:

- `feat:` para novas funcionalidades;
- `fix:` para correções;
- `test:` para testes;
- `docs:` para documentação;
- `chore:` para manutenção e configuração;
- `ci:` para automações do GitHub Actions.
