# Guia da fonte de extracao

Esta documentacao explica a API de extracao usada pelo AnimaHub. O projeto original fica em `concursosPublicosAPI` e possui remote proprio; o backend AnimaHub consome suas rotas por HTTP.

## Onde a API de extracao inicia

No projeto `concursosPublicosAPI`:

- `app.py`: inicia o Flask.
- `api/__init__.py`: cria a aplicacao e registra erros.
- `api/routing.py`: registra as rotas.

## Funcao que busca a listagem

Arquivo:

```text
concursosPublicosAPI/api/scraper/listing.py
```

Funcao principal:

```python
fetch_listing(category)
```

Ela monta a URL da categoria, chama o cliente HTTP e usa `parse_listing(html)` para transformar a tabela HTML em objetos JSON.

## Funcao que busca os detalhes

Arquivo:

```text
concursosPublicosAPI/api/scraper/details.py
```

Funcoes principais:

```python
fetch_details(url)
parse_details(html, url)
```

`fetch_details` baixa a pagina individual. `parse_details` usa BeautifulSoup para extrair titulo, resumo, datas, introducao, secoes, conteudo e links.

## Cliente HTTP

Arquivo:

```text
concursosPublicosAPI/api/scraper/client.py
```

Funcao:

```python
fetch_page(url)
```

Esse cliente centraliza timeout, redirecionamento, resposta HTTP e tratamento de erros.

## Rotas disponiveis

```text
GET /concursos/{uf}
GET /concursos/detalhes?url={url_do_concurso}
```

Exemplo:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/concursos/pe
```

## Onde as informacoes sao salvas

A API de extracao nao salva os concursos no banco do AnimaHub. Ela retorna JSON. A persistencia acontece no backend principal:

```text
AnimaHub_Classificador_API/app/repositories/competition.py
```

O fluxo completo e:

```text
site externo
    -> scraper Flask
    -> JSON da API de extracao
    -> ApiConcursoSource do AnimaHub
    -> normalizacao
    -> CompetitionRepository
    -> SQLite
```
