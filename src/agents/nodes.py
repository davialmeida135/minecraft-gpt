from pathlib import Path
from typing import List, Literal

from langchain.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from pydantic import BaseModel, Field

from src.config import llm
from src.agents.tools import minecraft_internet_search
from src.agents.state import AgentState, Message
from langgraph.graph import END, START, StateGraph

PROMPT_PATH = Path(__file__).with_name("prompt.md")
SUPERVISOR_PROMPT = (
    PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""
)

wiki_llm = llm.bind_tools([minecraft_internet_search])


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

    route: Literal["wiki_agent", "final_response"] = Field(
        description="Route: 'wiki_agent' if more context is necessary, or 'final_response' if ready to respond."
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
    intent = "wiki_search" if goto == "wiki_agent" else "final_response"

    return Command(update={"intent": intent}, goto=goto)


def wiki_agent(state: AgentState) -> Command[Literal["supervisor"]]:
    query = _latest_user_content(state.get("messages", []))
    
    # Let the LLM decide to call the tool
    response = wiki_llm.invoke([
        SystemMessage(content="You are a Minecraft wiki assistant. Use the minecraft_internet_search tool to find information."),
        HumanMessage(content=query),
    ])
    
    # Process tool calls from the response
    updated_calls = list(state.get("tool_calls", []))
    wiki_result = ""
    
    if response.tool_calls:
        for tool_call in response.tool_calls:
            # Execute the tool
            result = minecraft_internet_search.invoke(tool_call["args"])
            updated_calls.append({
                "name": tool_call["name"],
                "args": tool_call["args"],
                "result": result,
            })
            wiki_result += result + "\n"
    
    return Command(
        update={
            "wiki_context": wiki_result.strip(),
            "tool_calls": updated_calls,
            "intent": "wiki_search",
        },
        goto="supervisor",
    )

def response_agent(state: AgentState) -> dict:
    """Generate final response to the user."""
    prompt = """
Use the following context to respond to the user's query in a helpful and concise manner.
    """
    
    wiki_context = state.get("wiki_context", "")
    if wiki_context:
        prompt += f"\n\nWiki Context:\n{wiki_context}\n\n"
    
    prompt += "Conversation:\n" + _format_messages(state.get("messages", []))
    
    response = llm.invoke([
        SystemMessage(content="Use the following context to respond to the user's query in a helpful and concise manner."),
        HumanMessage(content=prompt),
    ]).content.strip()
    
    # Return a dict to update state (required by LangGraph)
    return Command(update={
        "response": response,
        "messages": state.get("messages", []) + [{"role": "assistant", "content": response}],
        },
        goto=END
    )

if __name__ == "__main__":
    from langchain_core.messages import convert_to_messages
    input = {
        "messages":
            [
                {
                    "role": "user",
                    "content": "How do i craft a stone pickaxe?",
                },
            ]
    }
    state: AgentState = AgentState(**input)
    output = supervisor_agent(state)
    print(output)