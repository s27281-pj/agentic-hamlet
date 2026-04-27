from langgraph.graph import StateGraph, START, END

from agents.characters import run_character_agent, run_narrator_agent
from graph.state import HamletState


SCENES = [
    {
        "title": "Scene I — The Ghost reveals the wound",
        "objective": "The Ghost tells Hamlet that Denmark is poisoned by murder and betrayal.",
        "speakers": ["ghost", "hamlet"],
    },
    {
        "title": "Scene II — Hamlet tests the King",
        "objective": "Hamlet speaks with Claudius, hiding accusation beneath wit and grief.",
        "speakers": ["hamlet", "claudius"],
    },
    {
        "title": "Scene III — The pressure rises",
        "objective": "Hamlet resolves to turn suspicion into a theatrical trap.",
        "speakers": ["hamlet"],
    },
]


def prepare_scene(state: HamletState) -> HamletState:
    scene = SCENES[state["scene_index"]]

    return {
        **state,
        "current_scene": scene["title"],
        "dialogues": [
            *state["dialogues"],
            f"\n## {scene['title']}\n\n_Objective: {scene['objective']}_\n",
        ],
    }


def run_scene_dialogue(state: HamletState) -> HamletState:
    scene = SCENES[state["scene_index"]]
    new_dialogues = list(state["dialogues"])

    for speaker in scene["speakers"]:
        response = run_character_agent(
            model_name=state["model_name"],
            character=speaker,
            memory=state["memory"],
            objective=scene["objective"],
        )

        new_dialogues.append(f"**{speaker.title()}**:\n\n{response}\n")

    return {
        **state,
        "dialogues": new_dialogues,
    }


def summarize_scene(state: HamletState) -> HamletState:
    scene = SCENES[state["scene_index"]]
    scene_dialogue = "\n".join(state["dialogues"])

    summary = run_narrator_agent(
        model_name=state["model_name"],
        scene=scene["title"],
        memory=state["memory"],
        dialogues=scene_dialogue,
    )

    updated_memory = f"{state['memory']}\n\nAfter {scene['title']}:\n{summary}"

    return {
        **state,
        "memory": updated_memory,
        "summaries": [
            *state["summaries"],
            f"\n### Narrator summary after {scene['title']}\n\n{summary}\n",
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