# Phase 1: Structured ReAct Agent Implementation — Merged Plan

**Goal**: Build a lightweight, type-safe, and modular ReAct-style agent system in Python that can reason over structured input, call tools, manage memory, and deliver final conclusions. It must be extensible, inspectable, and integrable into a TypeScript-driven backend via future API exposure.

---

## Overview

This plan merges the **initial quick prototype** approach with the **improved structured architecture** to produce a minimal but powerful and sustainable foundation. It emphasizes a dual-phase execution strategy:

1. **Phase 0**: Run an unstructured prototype inside Jupyter to test prompt logic and LLM/tool interaction quickly.
2. **Phase 1**: Refactor into a structured codebase using proper interfaces, type definitions, and modular architecture as outlined in the improved plan.

---

## Phase 0: Jupyter-Based Exploration (Optional, but Recommended)

### Goal
Quickly validate LLM → Tool → Observation → Final Answer loop without building full architecture.

### Files
- `notebook.ipynb`
- `llm_interface.py` (OpenAI wrapper)
- `simple_tool.py` (e.g., `summarize_wallet`)
- `prompt_template.txt`

### Steps
1. Load static prompt from `prompt_template.txt`.
2. Feed sample input from JSON or dict.
3. Call OpenAI or Claude using raw prompt.
4. Parse the output manually.
5. If “Action: tool_name[input]” → call function, append observation.
6. If “Final Answer: ...” → end loop.

### Why
You can experiment with:
- Prompt formatting
- Step parsing
- Tool call semantics
- Output validation

Do this in a notebook to reduce iteration friction.

---

## Phase 1: Structured, Modular Agent Core (Production Scaffold)

### Directory Layout

```
/react_agent
│
├── notebook.ipynb            # Interactive testbed
├── prompt_template.txt       # Editable prompt skeleton
├── config.py                 # API key, model config
├── main.py                   # (optional CLI/test harness)
│
├── core/
│   ├── base_types.py         # StepType, AgentStep (Enum, dataclass)
│   ├── tools.py              # Tool interface + registry
│   ├── prompts.py            # PromptTemplate class
│   ├── llm.py                # LLMInterface (OpenAI wrapper)
│   └── agent.py              # ReActAgent class
│
├── tools/
│   ├── calculator.py         # Example tool
│   └── search.py             # Example tool
│
└── examples/
    └── sample_input.json     # Test payload
```

---

## Implementation Components

### ✅ Step Abstractions (`base_types.py`)
- `StepType`: `Enum` for THOUGHT, ACTION, OBSERVATION, FINAL
- `AgentStep`: `dataclass` for content + type + metadata
- Purpose: make reasoning steps traceable and typed

### ✅ Tool Interface (`tools.py`)
- Define `Tool` as a `Protocol` (callable, name, description)
- `ToolRegistry` stores and retrieves tools by name
- Ensures clear decoupling from agent logic

### ✅ Prompt Management (`prompts.py`)
- `PromptTemplate` loads a base prompt from file
- `.format(**kwargs)` supports dynamic variable injection
- Externalizes prompt engineering

### ✅ LLM Abstraction (`llm.py`)
- Define abstract `LLMInterface`
- Implement `OpenAILLM` (async)
- Can be replaced by Claude, Ollama, or local models later

### ✅ Agent Logic (`agent.py`)
- `ReActAgent` processes steps based on memory
- Builds context from past steps
- Sends full trace to LLM
- Parses result and acts if necessary
- Supports multi-step chaining and termination on FINAL

---

## Execution Strategy

### Step 1: Run Raw Loop in Notebook (Phase 0)
- Test one prompt → one tool → one answer
- Confirm LLM interprets format correctly
- Validate tool input/output mapping
- Decide step parsing rules

### Step 2: Build Structured Files (Phase 1 Start)
- Create `base_types.py`, `llm.py`, and `tools.py`
- Implement tool registry with one tool
- Implement `ReActAgent` core class and minimal logic
- Use dummy input to run and inspect agent loop

### Step 3: Integrate Prompt File
- Move raw prompt into `prompt_template.txt`
- Inject tool descriptions from registry
- Generate dynamic final prompt

### Step 4: Add More Tools
- Add `calculator`, `search`, or `wallet_summarizer`
- Register tools via `ToolRegistry`

### Step 5: Test Input Cases
- Use `sample_input.json` for realism
- Validate response trace (Thought → Action → Observation → Final Answer)

### Step 6: Optional — Convert to CLI or API
- Add `main.py` runner (CLI or test script)
- Or wrap in `FastAPI` for REST endpoint (later)

---

## Future Considerations

| Feature               | Importance | Notes |
|----------------------|------------|-------|
| Retry logic          | Medium     | For malformed tool calls or failed LLM |
| Streaming output     | Medium     | Supports real-time trace |
| Vector memory        | Low        | For agent history or long-term context |
| Logging              | High       | Track token cost, tool use, error |
| Structured output    | Medium     | JSON schema per step |
| Tool input schema    | Medium     | Auto-validation of tool inputs |
| LLM fallbacks        | Medium     | Claude/OpenAI/Local tiering |
| Multi-agent planner  | Future     | Coordinated agents with task splitting |

---

## Summary

- **Use Phase 0** for exploratory development inside Jupyter.
- **Build Phase 1** as a modular, production-ready skeleton.
- **Stick to the improved architecture**: type-safety, tool abstraction, swappable LLMs.
- **Avoid overengineering**: move only when friction appears.
- **Plan for TS integration**: by exposing output through `run_agent()` or an API later.

---