from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from agents.prompts import (
    HAMLET_PROMPT,
    GHOST_PROMPT,
    CLAUDIUS_PROMPT,
    NARRATOR_PROMPT,
)


def build_llm(model_name: str, temperature: float = 0.7) -> ChatOllama:
    return ChatOllama(
        model=model_name,
        temperature=temperature,
    )


def run_character_agent(
    *,
    model_name: str,
    character: str,
    memory: str,
    objective: str,
) -> str:
    prompts = {
        "hamlet": HAMLET_PROMPT,
        "ghost": GHOST_PROMPT,
        "claudius": CLAUDIUS_PROMPT,
    }

    temperatures = {
        "hamlet": 0.85,
        "ghost": 0.45,
        "claudius": 0.65,
    }

    key = character.lower()

    if key not in prompts:
        raise ValueError(f"Unknown character agent: {character}")

    prompt = ChatPromptTemplate.from_template(prompts[key])
    llm = build_llm(model_name, temperatures[key])

    chain = prompt | llm
    response = chain.invoke(
        {
            "memory": memory,
            "objective": objective,
        }
    )

    return response.content.strip()


def run_narrator_agent(
    *,
    model_name: str,
    scene: str,
    memory: str,
    dialogues: str,
) -> str:
    prompt = ChatPromptTemplate.from_template(NARRATOR_PROMPT)
    llm = build_llm(model_name, 0.35)

    chain = prompt | llm
    response = chain.invoke(
        {
            "scene": scene,
            "memory": memory,
            "dialogues": dialogues,
        }
    )

    return response.content.strip()