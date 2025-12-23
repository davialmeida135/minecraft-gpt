# AI Coding Guidelines for minecraft-gpt

- **Goal**: Small sandbox for connecting LangChain/LangGraph logic to a Minecraft server via mcpq; current code is minimal and partially stubbed.
- **Runtime**: Python ≥3.12. Dependencies declared in pyproject; project uses uv for dependency management (e.g., `uv add langchain-openai`, `uv run python src/triggers.py`).

## Project Layout
- Core Minecraft client setup in [src/config.py](src/config.py#L1-L3); update host/port there when targeting a different server.
- Chat handler and long-running loop in [src/triggers.py](src/triggers.py#L1-L17); registers a `ChatEvent` listener and keeps process alive with `time.sleep` loop.
- CLI stub in [src/main.py](src/main.py#L1-L6) printing a greeting; not wired to gameplay.
- README currently empty; do not assume user-facing docs exist.

## Workflows
- Local run for Minecraft listener: `uv run python src/triggers.py` (ensure Minecraft server is reachable at configured host/port).
- The chat listener posts colored text using `mcpq.text` helpers; message format composed manually—preserve color resets to avoid bleeding styles.
- Interruptible LangGraph flow is not yet wired to a graph executor; if expanding, plug functions from entrypoint into the graph created in core.

## Conventions & Pitfalls
- External dependency `mcpq` provides `Minecraft`, `ChatEvent`, and `text` formatting; treat network calls as side-effectful (no retries implemented).
- The infinite loop in triggers is manual; if adding more listeners, remember to stop them on shutdown to avoid lingering threads.
- No type definition for `EmailAgentState` exists; add or import before executing entrypoint to avoid NameErrors.
- OpenAI model name is hard-coded; make it configurable if adding environment-based deploys.
- Currently no tests; any new logic should include minimal integration checks or docstrings explaining side effects.

## Extending Safely
- When adding graph nodes, use `langgraph.types.Command` for routing and persist intermediate state in the returned `update` map.
- Keep Minecraft host/port in config rather than in handlers to simplify switching environments.
- Prefer uv for installs and execution to keep lockstep with pyproject dependencies.
