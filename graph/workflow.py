from langgraph.graph import StateGraph, START, END

from agents.characters import run_character_agent, run_narrator_agent
from graph.state import HamletState


SCENES = [
    {
        "title": "Scena I — Duch na murach Elsynoru",
        "objective": (
            "Duch sugeruje Hamletowi, że śmierć starego króla nie była naturalna. "
            "Hamlet nie dostaje wygodnego raportu — dostaje ranę, podejrzenie i obowiązek."
        ),
        "speakers": ["ghost", "hamlet", "ghost", "hamlet"],
    },
    {
        "title": "Scena II — Hamlet bada Klaudiusza",
        "objective": (
            "Hamlet rozmawia z Klaudiuszem na dworze. "
            "Nie oskarża go wprost, lecz sprawdza reakcje przez ironię, aluzje i dwuznaczności. "
            "Klaudiusz próbuje zachować spokój i kontrolę."
        ),
        "speakers": ["hamlet", "claudius", "hamlet", "claudius", "hamlet"],
    },
    {
        "title": "Scena III — Plan teatralnej pułapki",
        "objective": (
            "Hamlet jest sam. W krótkim monologu musi wspomnieć aktorów, scenę albo przedstawienie. "
            "Postanawia przygotować sztukę podobną do śmierci króla, aby obserwować reakcję Klaudiusza. "
            "Nie mówi wprost o zemście. Nie mówi do Klaudiusza."
        ),
        "speakers": ["hamlet"],
    },
]


def prepare_scene(state: HamletState) -> HamletState:
    scene = SCENES[state["scene_index"]]
    print(f"[scene] Preparing: {scene['title']}")

    return {
        **state,
        "current_scene": scene["title"],
        "dialogues": [
            *state["dialogues"],
            f"\n## {scene['title']}\n\n_Cel sceny: {scene['objective']}_\n",
        ],
    }


def get_recent_dialogue_context(
    scene_dialogue_context: list[str],
    limit: int = 2,
) -> str:
    recent = scene_dialogue_context[-limit:]

    if not recent:
        return "To początek sceny. Nie padły jeszcze żadne kwestie."

    return "\n\n".join(recent)


def append_dialogue(dialogues: list[str], response: str) -> list[str]:
    """
    Na razie NIE usuwamy duplikatów.
    Chcemy zobaczyć realny output modelu, a nie przypadkiem wycinać treść.
    """
    cleaned = response.strip()

    if not cleaned:
        cleaned = "(Brak odpowiedzi modelu.)"

    return [*dialogues, f"\n{cleaned}\n"]


def run_scene_dialogue(state: HamletState) -> HamletState:
    scene = SCENES[state["scene_index"]]
    new_dialogues = list(state["dialogues"])
    scene_dialogue_context: list[str] = []

    for speaker in scene["speakers"]:
        print(f"[agent] Running: {speaker}")

        dialogue_context = get_recent_dialogue_context(scene_dialogue_context)

        response = run_character_agent(
            model_name=state["model_name"],
            character=speaker,
            memory=state["memory"],
            objective=scene["objective"],
            dialogue_context=dialogue_context,
        )

        print(f"[agent] Done: {speaker}")

        new_dialogues = append_dialogue(new_dialogues, response)
        scene_dialogue_context.append(response)

    return {
        **state,
        "dialogues": new_dialogues,
    }


def summarize_scene(state: HamletState) -> HamletState:
    scene = SCENES[state["scene_index"]]
    print(f"[narrator] Summarizing: {scene['title']}")

    current_scene_marker = f"## {scene['title']}"
    all_dialogues = "\n".join(state["dialogues"])

    if current_scene_marker in all_dialogues:
        current_scene_dialogue = all_dialogues.split(current_scene_marker, maxsplit=1)[-1]
    else:
        current_scene_dialogue = all_dialogues

    summary = run_narrator_agent(
        model_name=state["model_name"],
        scene=scene["title"],
        memory=state["memory"],
        dialogues=current_scene_dialogue,
    )

    updated_memory = f"{state['memory']}\n\nPo {scene['title']}:\n{summary}"

    return {
        **state,
        "memory": updated_memory,
        "summaries": [
            *state["summaries"],
            f"\n### Podsumowanie narratora po: {scene['title']}\n\n{summary}\n",
        ],
    }


def advance_or_finish(state: HamletState) -> str:
    next_index = state["scene_index"] + 1

    if next_index >= len(SCENES):
        return "finish"

    return "continue"


def advance_scene(state: HamletState) -> HamletState:
    return {
        **state,
        "scene_index": state["scene_index"] + 1,
    }


def finish(state: HamletState) -> HamletState:
    return state


def build_graph():
    graph = StateGraph(HamletState)

    graph.add_node("prepare_scene", prepare_scene)
    graph.add_node("run_scene_dialogue", run_scene_dialogue)
    graph.add_node("summarize_scene", summarize_scene)
    graph.add_node("advance_scene", advance_scene)
    graph.add_node("finish", finish)

    graph.add_edge(START, "prepare_scene")
    graph.add_edge("prepare_scene", "run_scene_dialogue")
    graph.add_edge("run_scene_dialogue", "summarize_scene")

    graph.add_conditional_edges(
        "summarize_scene",
        advance_or_finish,
        {
            "continue": "advance_scene",
            "finish": "finish",
        },
    )

    graph.add_edge("advance_scene", "prepare_scene")
    graph.add_edge("finish", END)

    return graph.compile()