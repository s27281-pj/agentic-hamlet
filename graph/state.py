from typing import TypedDict


class HamletState(TypedDict):
    model_name: str
    scene_index: int
    current_scene: str
    memory: str
    dialogues: list[str]
    summaries: list[str]