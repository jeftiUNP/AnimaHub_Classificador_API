# Fluxo de sincronização e apresentação

## Fontes

O sistema terá duas fontes com o mesmo contrato:

- `real`: cliente da API em `concursosPublicosAPI`;
- `fake`: fixture local para demonstrações e testes.

O contrato conceitual é:

```python
class ConcursoSource:
    def list_concursos(self, state: str) -> list[dict]: ...
    def get_details(self, url: str) -> dict: ...
```

## Sincronização manual

Não haverá rotina automática no MVP. A execução será iniciada por comando ou pela tela:

```text
POST /sincronizacao?fonte=real
POST /sincronizacao?fonte=fake
```

O serviço deve:

1. Ler os estados do perfil único.
2. Consultar a listagem de cada estado.
3. Unificar os resultados e remover duplicados pela URL original.
4. Comparar os links com os concursos já persistidos.
5. Buscar detalhes somente para concursos novos ou alterados.
6. Enviar conteúdo novo para a IA.
7. Salvar a análise estruturada.
8. Calcular e persistir as avaliações de correspondência.
9. Registrar o resultado da execução.

## Controle de custo

O processamento deve usar:

```text
input_hash = hash(perfil + análise_do_concurso + versão_do_prompt)
```

Se o mesmo hash já tiver uma avaliação salva, a IA não deve ser chamada novamente.

A listagem por estado não deve disparar análise de todos os concursos. Ela apenas identifica o que é novo ou mudou.

## Fonte fake

Os dados fake devem ficar em `tests/fixtures/` ou em uma pasta equivalente de dados de demonstração e possuir o mesmo formato normalizado da fonte real.

A apresentação poderá executar:

```text
Carregar dados de demonstração
→ sincronizar fonte fake
→ processar concursos novos
→ exibir correspondências explicadas
```

O objetivo é que a demonstração use o mesmo fluxo de produção, alterando apenas o adaptador da fonte.

## Exibição da aplicação

### Perfil

A tela permite editar:

- nome;
- formação;
- experiência;
- conhecimentos;
- interesses;
- estados de interesse;
- descrição livre do usuário.

### Concursos

A tela exibe:

- título e órgão;
- estado;
- situação;
- data de publicação;
- prazo de inscrição, quando disponível;
- compatibilidade;
- resumo da justificativa;
- paginação e filtros.

Ao abrir um concurso, o usuário deve visualizar:

- por que o concurso combina;
- quais pontos do perfil foram aproveitados;
- quais lacunas foram identificadas;
- quais estudos ou ações são recomendados;
- link para a fonte original.

## Fora do MVP

- login e autenticação;
- múltiplos usuários;
- sincronização automática;
- múltiplas fontes reais;
- classificação definitiva de concursos ausentes da listagem;
- filas distribuídas, Redis e Celery;
- banco vetorial.
