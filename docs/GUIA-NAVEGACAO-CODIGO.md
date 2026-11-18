# Guia de navegacao do backend e da IA

Este arquivo aponta os locais exatos para estudar e apresentar o backend do AnimaHub.

## Inicio da API

- [`app/main.py`](../app/main.py): cria o FastAPI, configura CORS e registra os routers.
- [`app/api/routes/health.py`](../app/api/routes/health.py): `GET /health`.

## Cadastro e consulta do usuario

- [`app/api/routes/profile.py`](../app/api/routes/profile.py): recebe `GET /perfil` e `PUT /perfil`.
- [`app/schemas/profile.py`](../app/schemas/profile.py): valida o payload do perfil e os estados.
- [`app/services/profile.py`](../app/services/profile.py): salva e serializa o perfil.
- [`app/models/profile.py`](../app/models/profile.py): representa a tabela `profiles`.

Para localizar os pontos principais:

```powershell
rg -n "get_profile|put_profile|save_profile|class Profile" app
```

## Concursos e persistencia

- [`app/models/competition.py`](../app/models/competition.py): tabela dos concursos.
- [`app/models/match.py`](../app/models/match.py): tabela das correspondencias da IA.
- [`app/repositories/competition.py`](../app/repositories/competition.py): salva listagens, detalhes e hash.
- [`app/db/database.py`](../app/db/database.py): cria o engine e as tabelas.
- [`app/db/runtime.py`](../app/db/runtime.py): fornece a sessao para as rotas.

Comandos para localizar:

```powershell
rg -n "save_listing|save_details|UniqueConstraint|create_engine|create_all" app
```

## Fonte real, fonte fake e sincronizacao

- [`app/sources/real.py`](../app/sources/real.py): chama a API de extracao na porta 5000.
- [`app/sources/fake.py`](../app/sources/fake.py): carrega dados sinteticos.
- [`app/sources/normalizer.py`](../app/sources/normalizer.py): converte respostas para os contratos internos.
- [`app/sources/contracts.py`](../app/sources/contracts.py): define `ConcursoListing` e `ConcursoDetails`.
- [`app/sources/fixtures/concursos_fake.json`](../app/sources/fixtures/concursos_fake.json): dados fake.
- [`app/api/routes/sync.py`](../app/api/routes/sync.py): rota `POST /sincronizacao`.
- [`app/services/sync.py`](../app/services/sync.py): executa a sincronizacao real e fake.

Funcao central:

```python
sync_competitions(session, source_name, states)
```

## Onde ficam os dados de treinamento

Arquivo: [`app/ai/dataset.py`](../app/ai/dataset.py)

Constante principal:

```python
TRAINING_DATA
```

Ela possui textos e rotulos:

```text
texto do perfil + concurso -> alta, media ou baixa
```

## Onde a IA e treinada

- [`app/ai/model.py`](../app/ai/model.py): cria o pipeline, treina e classifica.
- [`app/ai/train.py`](../app/ai/train.py): avalia e salva o modelo.
- [`app/ai/contracts.py`](../app/ai/contracts.py): define as caracteristicas do perfil e do concurso.

Funcoes principais:

```python
build_model()
train_model(examples)
classify(model, profile, competition)
build_input_text(profile, competition)
```

Comando:

```powershell
python -m app.ai.train
```

## Onde a IA normaliza o concurso

Arquivo: [`app/ai/normalizer.py`](../app/ai/normalizer.py)

Classes principais:

```python
FakeCompetitionNormalizer
OpenRouterCompetitionNormalizer
```

O OpenRouter pode organizar texto irregular em campos como areas, cargos, requisitos, escolaridade e salario. A classificacao principal continua no modelo TF-IDF + Logistic Regression.

## Onde perfil e concurso sao unidos

Arquivo: [`app/api/routes/recommendations.py`](../app/api/routes/recommendations.py)

Rota:

```text
GET /recomendacoes
```

Pontos para mostrar:

```python
profile_features = ProfileFeatures(...)
```

```python
for competition in session.scalars(select(Competition)).all():
```

```python
normalized = normalizer.normalize(details)
prediction = classify(model, profile_features, normalized)
```

Depois o resultado e salvo em `MatchEvaluation`.

Para localizar tudo:

```powershell
rg -n "ProfileFeatures|CompetitionFeatures|train_model|classify|MatchEvaluation|profile.states" app/api/routes/recommendations.py
```

## Fluxo completo

```text
perfil salvo
    -> estados do perfil
    -> listagem da fonte real e fake
    -> detalhes do concurso
    -> normalizacao
    -> ProfileFeatures + CompetitionFeatures
    -> train_model
    -> classify
    -> MatchEvaluation
    -> GET /recomendacoes
```
