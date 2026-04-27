import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from agents.prompts import (
    HAMLET_PROMPT,
    GHOST_PROMPT,
    CLAUDIUS_PROMPT,
    NARRATOR_PROMPT,
)


CHARACTER_LABELS = {
    "hamlet": "Hamlet",
    "ghost": "Duch",
    "claudius": "Klaudiusz",
}


def build_llm(
    model_name: str,
    temperature: float = 0.7,
    num_predict: int = 300,
) -> ChatOllama:
    return ChatOllama(
        model=model_name,
        temperature=temperature,
        num_predict=num_predict,
        top_p=0.9,
        reasoning=False,
        model_kwargs={
            "think": False,
        },
    )


def extract_content(response: Any) -> str:
    content = getattr(response, "content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()

    return str(content).strip()


def clean_character_response(response_text: str, character: str) -> str:
    label = CHARACTER_LABELS[character.lower()]
    text = response_text.strip()

    print(f"\n[raw {label}]\n{text}\n[/raw {label}]\n")

    text = text.replace("```", "").strip()

    # Usuń własną etykietę z początku, jeśli model ją dodał.
    text = re.sub(rf"^{label}:\s*", "", text, flags=re.IGNORECASE).strip()

    # Usuń dopisane kwestie innych postaci.
    for other_label in CHARACTER_LABELS.values():
        if other_label == label:
            continue

        text = re.split(
            rf"\n\s*{other_label}:\s*",
            text,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

    if not text:
        text = "(Brak treści z modelu.)"

    text = re.sub(r"\n{3,}", "\n\n", text)

    return f"{label}:\n{text.strip()}"


def run_character_agent(
    *,
    model_name: str,
    character: str,
    memory: str,
    objective: str,
    dialogue_context: str,
) -> str:
    prompts = {
        "hamlet": HAMLET_PROMPT,
        "ghost": GHOST_PROMPT,
        "claudius": CLAUDIUS_PROMPT,
    }

    temperatures = {
        "hamlet": 0.8,
        "ghost": 0.65,
        "claudius": 0.7,
    }

    token_limits = {
        "hamlet": 500,
        "ghost": 300,
        "claudius": 400,
    }

    key = character.lower()

    if key not in prompts:
        raise ValueError(f"Unknown character agent: {character}")

    prompt = ChatPromptTemplate.from_template(prompts[key])
    llm = build_llm(
        model_name=model_name,
        temperature=temperatures[key],
        num_predict=token_limits[key],
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "memory": memory,
            "objective": objective,
            "dialogue_context": dialogue_context,
        }
    )

    response_text = extract_content(response)

    print(f"\n[debug {CHARACTER_LABELS[key]} full response]\n{response}\n[/debug]\n")

    return clean_character_response(response_text, key)


def run_narrator_agent(
    *,
    model_name: str,
    scene: str,
    memory: str,
    dialogues: str,
) -> str:
    prompt = ChatPromptTemplate.from_template(NARRATOR_PROMPT)
    llm = build_llm(model_name, temperature=0.3, num_predict=500)

    chain = prompt | llm

    response = chain.invoke(
        {
            "scene": scene,
            "memory": memory,
            "dialogues": dialogues,
        }
    )

    response_text = extract_content(response)

    print(f"\n[debug narrator full response]\n{response}\n[/debug]\n")
    print(f"\n[raw narrator]\n{response_text}\n[/raw narrator]\n")

    return response_text or "Brak istotnej zmiany stanu."