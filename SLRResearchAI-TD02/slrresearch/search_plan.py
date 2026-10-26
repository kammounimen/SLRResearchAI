import re
from typing import Literal

from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field


class ResearchQuestion(BaseModel):
    """Contrat des données utilisables après le contrôle textuel."""

    identifier: str = Field(pattern=r"^RQ[0-9]+$")
    question: str = Field(min_length=15)


class WorkflowOutcome(BaseModel):
    """État observable du workflow après validation et repair éventuel."""

    status: Literal["accepted", "repaired", "human_required"]
    text: str
    questions: list[ResearchQuestion] = Field(default_factory=list)
    error: str | None = None
    repair_attempts: int = 0


RQ_PATTERN = re.compile(r"^(RQ[0-9]+)\.\s*(.{15,})$")
SEARCH_CONCEPTS = {
    "task": [
        "systematic review screening",
        "study selection",
        "title and abstract screening",
    ],
    "technology": ["large language models", "LLM", "generative AI"],
}


def extract_non_empty_lines(text: str) -> list[str]:
    lines = [
        line.strip()
        for line in text.strip().splitlines()
        if line.strip()
    ]
    if not lines:
        raise ValueError("Texte vide")
    return lines


def parse_rq_line(line: str) -> dict:
    match = RQ_PATTERN.fullmatch(line)
    if match is None:
        raise ValueError(f"Ligne non conforme : {line}")
    return {
        "identifier": match.group(1),
        "question": match.group(2).strip(),
    }
def validate_identifiers(records: list[dict]) -> None:
    identifiers = [record["identifier"] for record in records]
    expected = ["RQ1", "RQ2", "RQ3"]
    if identifiers != expected:
        raise ValueError(
            f"Identifiants invalides : {identifiers}, attendu {expected}"
        )

def validate_no_duplicates(records: list[dict]) -> None:
    questions = [record["question"] for record in records]
    unique_questions = set(questions)

    if len(questions) != len(unique_questions):
        raise ValueError("Les trois questions doivent être différentes")

def validate_free_text(text: str) -> list[dict]:
    lines = extract_non_empty_lines(text)
    records = [parse_rq_line(line) for line in lines]
    validate_identifiers(records)
    validate_no_duplicates(records)
    return records

def build_few_shot_prompt(topic: str) -> str:
    clean = topic.strip()
    if not clean:
        raise ValueError("Sujet vide")

    return f"""Propose exactement trois questions de recherche.
N'ajoute ni introduction, ni conclusion, ni JSON.

Exemple 1 - Sujet : IA et personnalisation pédagogique
RQ1. Comment l'IA influence-t-elle la personnalisation des parcours d'apprentissage ?
RQ2. Quels risques l'IA introduit-elle dans l'évaluation des étudiants ?
RQ3. Quel contrôle humain doit-il être conservé dans les décisions pédagogiques ?

Exemple 2 - Sujet : LLM et revue de littérature
RQ1. Comment les LLM aident-ils à extraire les données des articles scientifiques ?
RQ2. Quelles limites les LLM présentent-ils pour la sélection des études ?
RQ3. Quelles métriques permettent d'évaluer la qualité des résumés générés ?

Sujet courant : {clean}
Retourne exactement trois lignes RQ1., RQ2. et RQ3."""


def build_repair_prompt(text: str, error: str) -> str:
    return f"""Tu corriges la forme d'une sortie destinée à un programme.

[TÂCHE]
Corrige uniquement la forme du texte ci-dessous, sans rien inventer.
Préserve le sens exact de chaque question.

[ERREUR DÉTECTÉE]
{error}

[CONTRAT ATTENDU]
- Exactement trois lignes, une par question.
- Chaque ligne commence par RQ1., RQ2. puis RQ3. dans cet ordre.
- N'ajoute ni introduction, ni explication, ni Markdown, ni JSON.

[EXEMPLE CONFORME]
RQ1. Comment l'IA influence-t-elle la personnalisation pédagogique ?
RQ2. Quels risques l'IA introduit-elle dans l'évaluation ?
RQ3. Quel contrôle humain doit-il être conservé ?

[TEXTE À CORRIGER]
{text}

[SORTIE]
Retourne uniquement les trois lignes RQ1., RQ2. et RQ3. corrigées."""


def repair_with_llm(model, text: str, error: str) -> str:
    """Code fourni : un seul appel conditionnel de réparation."""
    response = model.invoke(build_repair_prompt(text, error))
    return str(response.content).strip()


def validate_questions(records: list[dict]) -> list[ResearchQuestion]:
    questions = []

    for record in records:
        question = ResearchQuestion.model_validate(record)
        questions.append(question)

    return questions


def build_queries(questions: list[ResearchQuestion]) -> dict[str, str]:
    if not questions:
        raise ValueError("Au moins une RQ validée est nécessaire")

    combinations = []
    for task in SEARCH_CONCEPTS["task"]:
        for technology in SEARCH_CONCEPTS["technology"]:
            expression = f'("{task}" AND "{technology}")'
            combinations.append(expression)

    base_query = " OR ".join(combinations)

    return {
        "scholar": base_query,
        "ieee": base_query,
        "acm": base_query,
    }

def build_question_pipeline():
    text_control = RunnableLambda(validate_free_text)
    data_contract = RunnableLambda(validate_questions)
    query_builder = RunnableLambda(build_queries)

    return text_control | data_contract | query_builder
def run_controlled_workflow(model, text: str) -> WorkflowOutcome:
    try:
        records = validate_free_text(text)
        questions = validate_questions(records)
        return WorkflowOutcome(
            status="accepted",
            text=text,
            questions=questions,
            repair_attempts=0,
            error=None,
        )

    except ValueError as first_error:
        repaired_text = repair_with_llm(
            model,
            text,
            str(first_error),
        )

        try:
            repaired_records = validate_free_text(repaired_text)
            repaired_questions = validate_questions(repaired_records)

            return WorkflowOutcome(
                status="repaired",
                text=repaired_text,
                questions=repaired_questions,
                repair_attempts=1,
                error=None,
            )

        except ValueError as second_error:
            return WorkflowOutcome(
                status="human_required",
                text=repaired_text,
                questions=[],
                repair_attempts=1,
                error=str(second_error),
            )