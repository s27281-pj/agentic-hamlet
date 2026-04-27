# 🎭 Agentic Hamlet

**Multi-agent dramatic simulation of *Hamlet* using LLMs.**

This project demonstrates how multiple AI agents can interact in a structured narrative flow, each with its own role, memory, and behavioral constraints.

---

## 🧠 Concept

Instead of a single model generating text, this system uses **multiple agents**:

- **Hamlet** — indirect, suspicious, ironic  
- **Ghost** — fragmented, emotional, disturbing  
- **Claudius** — controlled, political, defensive  
- **Narrator** — tracks state and updates memory  

Agents interact through a **LangGraph workflow**, maintaining continuity between scenes.

---

## ⚙️ Tech Stack

- **Language:** Python  
- **Orchestration:** LangChain & LangGraph  
- **Local LLM Runtime:** Ollama  
- **Model:** `gemma4:e2b`  

---

## 🚀 How It Works

1. **Scene Configuration**  
   Each scene defines an objective and a list of active speakers.

2. **Agent Logic**  
   For each speaker, the agent receives:
   - global memory state  
   - scene objective  
   - recent dialogue context  

3. **Generation**  
   The agent generates a response aligned with its persona.

4. **Narrator Summary**  
   After each scene, the Narrator updates:
   - state changes  
   - relationship shifts  
   - suspicion and tension  

5. **State Persistence**  
   Memory is updated and passed to the next step in the graph.

---

## ▶️ Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt

```
### 2. Start Ollama

Make sure Ollama is running and the model is available:

```bash
ollama pull gemma4:e2b

```

### 3. Run the simulation
```
python main.py
```


### 4. Check results

The generated drama is saved to:
output/hamlet_demo.md

## 📄 Example Output
Hamlet:
Cóż za ładne słowa, Królu. Harmonia, powiadasz? ...

Klaudiusz:
Wszelkie sprawy w zamku muszą być uregulowane...

Narrator:
- Scene summary
- Relationship changes
- Suspicion tracking

## ⚠️ Limitations

Local models

may repeat phrases
may leak dialogue between agents
may ignore constraints

Prompting

still experimental
sensitive to small changes

Quality

depends heavily on model capabilities

## 🧪 Purpose

This is a conceptual prototype demonstrating:

multi-agent orchestration
role-based prompting
stateful narrative systems
LLM-driven simulation

## 🔮 Possible Extensions
 Add more characters (Gertrude, Polonius)
 Introduce long-term memory weighting
 Add evaluation / scoring of scenes
 Add voice or real-time streaming
 Integrate with E2E testing agents (Playwright)

## 🧱 Status

v0.1 — working prototype

✅ stable execution
✅ basic agent roles
✅ narrative continuity
✅ markdown output

## 🧑‍💻 Author

Cyprian Czerwiński

Built as an experiment in agent-based systems and LLM orchestration.
