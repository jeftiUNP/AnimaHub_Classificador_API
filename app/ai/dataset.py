"""Dados sintéticos estruturados e rotulados para o classificador."""

from app.ai.contracts import CompetitionFeatures, ProfileFeatures
from app.ai.model import TrainingExample, build_input_text


def example(profile: ProfileFeatures, competition: CompetitionFeatures, label: str) -> TrainingExample:
    """Cria um exemplo no mesmo formato usado na predição real."""
    return build_input_text(profile, competition), label


def profile(education: str, areas: list[str], skills: list[str], states: list[str] | None = None) -> ProfileFeatures:
    return ProfileFeatures(education=education, areas=areas, skills=skills, states=states or ["CE"])


def competition(
    title: str,
    state: str,
    education: str,
    areas: list[str],
    activities: list[str],
) -> CompetitionFeatures:
    return CompetitionFeatures(
        title=title,
        state=state,
        education_required=education,
        areas=areas,
        activities=activities,
    )


TRAINING_DATA: list[TrainingExample] = [
    example(profile("superior", ["tecnologia"], ["programacao"]), competition("Analista TI", "CE", "superior", ["tecnologia"], ["programacao"]), "alta"),
    example(profile("superior", ["tecnologia"], ["banco_dados"]), competition("Analista Sistemas", "CE", "superior", ["tecnologia"], ["banco_dados"]), "alta"),
    example(profile("superior", ["gestao"], ["processos"]), competition("Analista Processos", "CE", "superior", ["gestao"], ["processos"]), "alta"),
    example(profile("superior", ["direito"], ["legislacao"]), competition("Procurador", "CE", "superior", ["direito"], ["legislacao"]), "alta"),
    example(profile("superior", ["educacao"], ["docencia"]), competition("Professor", "CE", "superior", ["educacao"], ["docencia"]), "alta"),
    example(profile("superior", ["saude"], ["enfermagem"]), competition("Enfermeiro", "CE", "superior", ["saude"], ["enfermagem"]), "alta"),
    example(profile("superior", ["tecnologia"], ["programacao"]), competition("Tecnico TI", "CE", "medio", ["tecnologia"], ["suporte"]), "alta"),
    example(profile("medio", ["gestao"], ["administracao"]), competition("Tecnico Administrativo", "CE", "medio", ["gestao"], ["administracao"]), "media"),
    example(profile("superior", ["contabilidade"], ["financas"]), competition("Analista Administrativo", "CE", "superior", ["gestao"], ["processos"]), "media"),
    example(profile("superior", ["tecnologia"], ["sistemas"]), competition("Analista Administrativo", "CE", "superior", ["gestao"], ["processos"]), "media"),
    example(profile("superior", ["direito"], ["legislacao"]), competition("Tecnico Administrativo", "CE", "medio", ["gestao"], ["administracao"]), "media"),
    example(profile("medio", ["educacao"], ["pedagogia"]), competition("Tecnico Administrativo", "CE", "medio", ["gestao"], ["administracao"]), "media"),
    example(profile("superior", ["engenharia"], ["projetos"]), competition("Analista Planejamento", "CE", "superior", ["gestao"], ["planejamento"]), "media"),
    example(profile("superior", ["tecnologia"], ["programacao"]), competition("Procurador", "CE", "superior", ["direito"], ["legislacao"]), "baixa"),
    example(profile("superior", ["pedagogia"], ["docencia"]), competition("Analista TI", "CE", "superior", ["tecnologia"], ["programacao"]), "baixa"),
    example(profile("superior", ["saude"], ["enfermagem"]), competition("Engenheiro Civil", "CE", "superior", ["engenharia"], ["obras"]), "baixa"),
    example(profile("superior", ["direito"], ["legislacao"]), competition("Desenvolvedor", "CE", "superior", ["tecnologia"], ["programacao"]), "baixa"),
    example(profile("superior", ["historia"], ["pesquisa"]), competition("Auditor Fiscal", "CE", "superior", ["contabilidade"], ["financas"]), "baixa"),
    example(profile("superior", ["artes"], ["criacao"]), competition("Enfermeiro", "CE", "superior", ["saude"], ["enfermagem"]), "baixa"),
    example(profile("superior", ["engenharia"], ["obras"]), competition("Professor", "CE", "superior", ["educacao"], ["docencia"]), "baixa"),
    example(profile("superior", ["medicina"], ["clinica"]), competition("Analista Sistemas", "CE", "superior", ["tecnologia"], ["sistemas"]), "baixa"),
    example(profile("medio", ["administracao"], ["atendimento"]), competition("Analista TI", "CE", "superior", ["tecnologia"], ["programacao"]), "baixa"),
    example(profile("superior", ["tecnologia"], ["programacao"], ["PE"]), competition("Analista TI", "CE", "superior", ["tecnologia"], ["programacao"]), "baixa"),
]

# Variações repetidas tornam os padrões de compatibilidade aprendíveis sem
# depender de uma palavra isolada ou de um único cargo.
for title in ("Analista TI", "Tecnico TI", "Desenvolvedor", "Especialista Sistemas", "Analista Dados"):
    TRAINING_DATA.append(
        example(
            profile("superior", ["tecnologia"], ["programacao", "sistemas"]),
            competition(title, "CE", "superior", ["tecnologia"], ["programacao", "sistemas"]),
            "alta",
        )
    )

for title in ("Analista Juridico", "Procurador", "Tecnico Direito", "Assessor Juridico", "Analista Legislacao"):
    TRAINING_DATA.append(
        example(
            profile("superior", ["direito"], ["legislacao"]),
            competition(title, "CE", "superior", ["direito"], ["legislacao"]),
            "alta",
        )
    )

for title in ("Analista TI", "Tecnico Tecnologia", "Desenvolvedor", "Analista Sistemas", "Especialista TI"):
    TRAINING_DATA.append(
        example(
            profile("superior", ["direito"], ["legislacao"]),
            competition(title, "CE", "superior", ["tecnologia"], ["programacao", "sistemas"]),
            "baixa",
        )
    )

for title in ("Engenheiro Civil", "Analista Obras", "Tecnico Engenharia", "Fiscal Obras", "Projetista"):
    TRAINING_DATA.append(
        example(
            profile("superior", ["pedagogia"], ["docencia"]),
            competition(title, "CE", "superior", ["engenharia"], ["obras", "calculo"]),
            "baixa",
        )
    )

for title in ("Tecnico Administrativo", "Assistente Administrativo", "Analista Processos", "Auxiliar Gestao", "Tecnico Gestao"):
    TRAINING_DATA.append(
        example(
            profile("superior", ["tecnologia"], ["sistemas"]),
            competition(title, "CE", "superior", ["gestao"], ["processos"]),
            "media",
        )
    )


# Base expandida e determinística para o MVP. Cada domínio gera exemplos
# positivos, parcialmente compatíveis e incompatíveis em várias UFs e com
# títulos diferentes. Os dados continuam sintéticos, mas reduzem a
# dependência de poucas frases repetidas no treinamento.
DOMAIN_CASES = [
    ("tecnologia", "programacao sistemas", "Analista de Tecnologia", "gestao", "processos", "superior"),
    ("direito", "legislacao juridico", "Analista Jurídico", "gestao", "contratos", "superior"),
    ("educacao", "pedagogia docencia", "Professor da Rede Pública", "gestao", "planejamento", "superior"),
    ("saude", "enfermagem atendimento", "Analista de Saúde", "gestao", "servicos", "superior"),
    ("engenharia", "projetos obras", "Engenheiro de Obras", "gestao", "planejamento", "superior"),
    ("contabilidade", "financas auditoria", "Analista Financeiro", "gestao", "controle", "superior"),
    ("gestao", "administracao processos", "Analista Administrativo", "contabilidade", "financas", "superior"),
    ("comunicacao", "jornalismo redacao", "Analista de Comunicação", "educacao", "instrucao", "superior"),
]

TRAINING_STATES = ("CE", "PE", "RN", "SP")

for area, skills, title, related_area, related_activity, education in DOMAIN_CASES:
    skill_list = skills.split()
    for state in TRAINING_STATES:
        TRAINING_DATA.append(
            example(
                profile(education, [area], skill_list, [state]),
                competition(title, state, education, [area], skill_list),
                "alta",
            )
        )
        TRAINING_DATA.append(
            example(
                profile(education, [area], skill_list, [state]),
                competition(
                    f"{title} - Área de {related_area}",
                    state,
                    education,
                    [related_area],
                    [related_activity],
                ),
                "media",
            )
        )
        TRAINING_DATA.append(
            example(
                profile(education, [area], skill_list, [state]),
                competition(
                    f"{title} - Área incompatível",
                    state,
                    "doutorado",
                    [related_area],
                    [related_activity],
                ),
                "baixa",
            )
        )
