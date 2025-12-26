from pathlib import Path
from typing import List, Literal

from langchain.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from pydantic import BaseModel, Field

from src.config import llm
from src.agents.tools import minecraft_internet_search
from src.agents.state import AgentState, Message

PROMPT_PATH = Path(__file__).with_name("prompt.md")
SUPERVISOR_PROMPT = (
    PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""
)


def _format_messages(messages: List[Message]) -> str:
    lines = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _latest_user_content(messages: List[Message]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return messages[-1].get("content", "") if messages else ""

class SupervisorIntent(BaseModel):  
    """Grade documents using a binary score for relevance check."""

    route: str = Field(
        description="Route: 'wiki_agent' if more context is necessary, or 'final_response' if not ready to respond."
    )

def supervisor_agent(
    state: AgentState,
) -> Command[Literal["wiki_agent", "final_response"]]:
    rendered_history = _format_messages(state.get("messages", []))
    prompt = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(
            content=(
                "Player Chat Context:\n"
                f"{rendered_history}\n\n"
            )
        ),
    ]

    decision = llm.with_structured_output(SupervisorIntent).invoke(prompt).route


    goto = decision
    intent = "wiki_search" if goto == "wiki_agent" else "respond"

    return Command(update={"intent": intent}, goto=goto)


def wiki_agent(state: AgentState) -> Command[Literal["draft_response"]]:
    query = _latest_user_content(state.get("messages", []))
    wiki_result = minecraft_internet_search(query)

    tool_call = {
        "name": "minecraft_internet_search",
        "args": {"query": query},
        "result": wiki_result,
    }

    updated_calls = list(state.get("tool_calls", []))
    updated_calls.append(tool_call)

    return Command(
        update={
            "wiki_context": wiki_result,
            "tool_calls": updated_calls,
            "intent": "wiki_search",
        },
        goto="draft_response",
    )

def response_agent(state: AgentState) -> Command[Literal["send_reply"]]:
    prompt = """
Use the following context to respond to the user's query in a helpful and concise manner.
    """
    prompt = prompt + _format_messages(state.get("messages", []))
    response = llm.invoke(prompt).content.strip().lower()
    return response

if __name__ == "__main__":
    from langchain_core.messages import convert_to_messages
    input = {
        "messages":
            [
                {
                    "role": "user",
                    "content": "Como faço para craftar uma picareta de pedra?",
                },
            ]
    }
    state: AgentState = AgentState(**input)
    output = supervisor_agent(state)
    print(output)