import os
from pathlib import Path

from dotenv import load_dotenv

from graph.workflow import build_graph


def main() -> None:
    load_dotenv()

    model_name = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
    output_file = Path(os.getenv("OUTPUT_FILE", "output/hamlet_demo.md"))

    output_file.parent.mkdir(parents=True, exist_ok=True)

    app = build_graph()

    initial_state = {
        "model_name": model_name,
        "scene_index": 0,
        "current_scene": "",
        "memory": (
            "Old King Hamlet is dead. Claudius has taken the throne and married Gertrude. "
            "Hamlet is grieving, suspicious, and alienated from the court. "
            "The Ghost may reveal hidden truth, but its nature is uncertain."
        ),
        "dialogues": [],
        "summaries": [],
    }

    result = app.invoke(initial_state)

    content = "# Agentic Hamlet Demo\n\n"
    content += "## Generated Dramatic Scenes\n\n"
    content += "\n".join(result["dialogues"])
    content += "\n\n---\n\n"
    content += "## Narrator / State Updates\n\n"
    content += "\n".join(result["summaries"])
    content += "\n\n---\n\n"
    content += "## Final Memory State\n\n"
    content += result["memory"]

    output_file.write_text(content, encoding="utf-8")

    print(f"Generated: {output_file}")


if __name__ == "__main__":
    main()