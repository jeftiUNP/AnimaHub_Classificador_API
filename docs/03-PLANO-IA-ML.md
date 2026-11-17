# IA do MVP

## Arquitetura

O projeto usa duas etapas simples:

```text
Concurso bruto
    ↓
OpenRouter ou normalizador fake
    ↓
Concurso padronizado
    ↓
TF-IDF + LogisticRegression treinados com exemplos
    ↓
Compatibilidade e confiança
```

O OpenRouter limpa e estrutura o texto irregular da publicação. O modelo treinado é responsável pela classificação principal. O frontend não conversa diretamente com a LLM.

## Modelo treinável

O classificador segue o padrão do código de referência do professor:

- `TfidfVectorizer` transforma texto em características numéricas;
- `LogisticRegression` aprende os rótulos;
- `Pipeline` junta preparação e classificação;
- `predict` retorna `alta`, `media` ou `baixa`;
- `predict_proba` retorna a confiança.

O texto de treinamento é formado por perfil e concurso padronizados. Também são criados tokens de relação, como área do perfil com área do concurso, para o modelo aprender compatibilidade e não apenas palavras isoladas.

## OpenRouter

O cliente está em `app/ai/normalizer.py` e usa:

```text
OPENROUTER_API_KEY
OPENROUTER_MODEL
OPENROUTER_BASE_URL
```

Sem essas variáveis, a aplicação pode usar `FakeCompetitionNormalizer`, que funciona offline e não consome chamadas externas.

## Treinar e avaliar

```powershell
python -m app.ai.train
```

O comando divide os exemplos sintéticos, imprime `precision`, `recall`, `f1-score` e `accuracy`, treina o modelo final com todos os dados e salva o artefato em `artifacts/compatibility_model.joblib`.

## Dados sintéticos

Os exemplos estão em `app/ai/dataset.py` e cobrem:

- compatibilidade alta;
- compatibilidade média;
- incompatibilidade;
- formação, área e atividade;
- estado compatível e incompatível.

Os rótulos são definidos nos dados de treinamento, não inventados pela LLM.

## Testes

```powershell
python -m pytest
```

Os testes validam o treinamento, a predição, a confiança, o normalizador fake e o formato da chamada ao OpenRouter usando transporte HTTP simulado.
