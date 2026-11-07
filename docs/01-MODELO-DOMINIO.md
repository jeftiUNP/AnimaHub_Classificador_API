# Modelo de domínio do MVP

## Objetivo

O MVP deve demonstrar que uma IA consegue interpretar a formação, a experiência e os interesses de um usuário e explicar por que determinados concursos são mais ou menos compatíveis.

O sistema será single-user: haverá um único perfil persistido e não haverá autenticação nesta fase.

## Entidades

### Perfil

Representa o usuário único da aplicação.

Campos previstos:

```text
id
name
education
experience
knowledge_areas
interests
natural_description
created_at
updated_at
```

Os estados de interesse devem ser controlados por uma lista de UFs e relacionados ao perfil por uma tabela intermediária:

```text
states
profile_states
```

Exemplo de dados do perfil:

```json
{
  "name": "João",
  "education": {
    "level": "superior",
    "courses": ["Sistemas de Informação"]
  },
  "experience": ["desenvolvimento de sistemas", "análise de processos"],
  "knowledge_areas": ["tecnologia", "gestão", "dados"],
  "interests": ["órgãos públicos", "estabilidade"],
  "states": ["CE", "PE", "RN"],
  "natural_description": "Sou formado em Sistemas de Informação..."
}
```

### Concurso

Representa a publicação obtida da fonte real ou fake.

Campos previstos:

```text
id
source
source_url
title
organization
state
source_status
normalized_status
published_at
registration_start
registration_end
exam_date
raw_content
content_hash
first_seen_at
last_seen_at
created_at
updated_at
```

`source_status` preserva o valor recebido da fonte, como `open` ou `expected`. `normalized_status` representa a interpretação do sistema, como `PREVISTO`, `INSCRICOES_ABERTAS` ou `DESCONHECIDO`.

A ausência de um concurso na última listagem não deve excluí-lo nem marcá-lo automaticamente como expirado.

### Análise do concurso

Guarda o resultado estruturado da IA sem perder o conteúdo original.

```text
competition_analyses
├── competition_id
├── content_hash
├── model
├── prompt_version
├── extracted_data
├── processing_status
└── processed_at
```

### Avaliação de correspondência

A correspondência não liga diretamente uma pessoa a uma vaga. Ela representa uma avaliação semântica entre o perfil e um concurso.

```text
match_evaluations
├── profile_id
├── competition_id
├── score
├── fit_level
├── summary
├── strengths
├── gaps
├── recommendation
├── evidence
├── model
├── prompt_version
├── input_hash
└── timestamps
```

Um perfil pode combinar com muitos concursos, e um concurso pode ser avaliado para vários perfis no futuro.

## Lógica de combinação

O processo deve usar duas etapas:

1. Filtros objetivos: estado selecionado, disponibilidade mínima do concurso e dados necessários para análise.
2. Análise semântica: a IA compara a formação, a experiência, os conhecimentos e os interesses com os requisitos e as atividades descritas no concurso.

A saída esperada é estruturada:

```json
{
  "score": 84,
  "fit_level": "alto",
  "summary": "A formação combina com as atividades do concurso.",
  "strengths": ["Formação superior compatível"],
  "gaps": ["Pouca evidência de experiência em administração pública"],
  "recommendation": "Vale a pena acompanhar o concurso e estudar legislação administrativa.",
  "evidence": []
}
```

O resultado deve ser salvo. A IA só deve ser chamada novamente quando o perfil, a análise do concurso ou a versão do prompt mudar.
