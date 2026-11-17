# AnimaHub Classificador API

Backend do AnimaHub Classificador, um sistema que analisa a formação, a experiência e os interesses de um usuário para encontrar concursos públicos compatíveis.

## Status do projeto

O projeto já possui a fundação do MVP, os adaptadores de extração, a persistência inicial e o classificador treinável. A API FastAPI possui o endpoint `GET /health`, testes automatizados e validação contínua no GitHub Actions. A IA está documentada em [`docs/03-PLANO-IA-ML.md`](docs/03-PLANO-IA-ML.md).

## Escopo do MVP

O MVP será exclusivo para um único usuário e um único perfil. Não haverá login, senha, sessão ou suporte a múltiplos usuários nesta fase.

O sistema deverá permitir:

- cadastrar a formação, a experiência, os conhecimentos e os interesses do perfil;
- selecionar os estados onde o usuário deseja fazer concurso;
- sincronizar concursos manualmente a partir da fonte real;
- carregar uma fonte fake para demonstrações e testes;
- processar somente concursos novos ou alterados;
- usar IA para interpretar o perfil e o conteúdo dos concursos;
- gerar correspondências explicadas, com pontuação, pontos fortes e lacunas;
- listar concursos com filtros, paginação e ordenação por proximidade do prazo.

Autenticação, múltiplos usuários, rotina automática de sincronização e tratamento completo de concursos expirados estão fora do MVP.

## Stack

- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- Pytest e HTTPX
- GitHub Actions para CI

O projeto será desenvolvido com orçamento zero: a IA usará o OpenRouter com um modelo gratuito configurado por variável de ambiente. Para testes e apresentação, haverá também um provedor fake determinístico que não consome chamadas externas.

O banco de produção será definido na implementação da persistência. SQLite pode ser utilizado no desenvolvimento inicial e PostgreSQL é a opção prevista para produção.

## Fonte de concursos

A fonte primária é a API local existente em `C:\Estudos\A3 concursos\concursosPublicosAPI`.

Ela oferece:

```text
GET /concursos/{uf}
GET /concursos/detalhes?url={url_do_concurso}
```

O AnimaHub não deve refazer o scraping HTML dessa fonte. Seu papel será consumir a listagem por estado, identificar concursos novos, buscar os detalhes necessários e persistir os dados normalizados.

A fonte fake deve implementar o mesmo contrato da fonte real para que a apresentação percorra exatamente o mesmo fluxo.

## Executar localmente

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Inicie a API:

```powershell
python -m uvicorn app.main:app --reload
```

Acesse:

- API: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

Execute os testes:

```powershell
python -m pytest
```

## Organização prevista

```text
app/
├── api/routes/       # endpoints HTTP
├── ai/               # normalização, treinamento e classificação
├── core/             # configurações e exceções
├── db/               # conexão e sessões do banco
├── models/           # modelos SQLAlchemy
├── repositories/     # acesso a dados
├── scraper/          # sincronização (próxima etapa)
├── sources/          # contrato, fonte real, fonte fake e normalização
└── services/         # regras de negócio

tests/
├── fixtures/         # respostas e concursos fake
└── ...
```

## Próxima implementação

1. Criar configuração e conexão com o banco.
2. Criar o modelo single-user do perfil e estados.
3. Criar modelos de concursos, análises e correspondências.
4. Implementar a sincronização incremental usando `app.sources`.
5. Integrar o classificador à sincronização e persistir as análises.
6. Expor perfil, concursos, sincronização e recomendações.

## Commits

Este projeto usa Commits Semânticos:

- `feat:` novas funcionalidades;
- `fix:` correções;
- `test:` testes;
- `docs:` documentação;
- `chore:` configuração e manutenção;
- `ci:` automações do GitHub Actions.
