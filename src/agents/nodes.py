from pathlib import Path
from typing import List, Literal

from langchain.messages import HumanMessage, SystemMessage, AnyMessage, AIMessage
from langgraph.types import Command
from pydantic import BaseModel, Field

from src.config import llm
from src.agents.tools import minecraft_internet_search
from langgraph.graph import END
from src.agents.state import AgentState, Message, PlayerContext, ToolCall

from langgraph.runtime import Runtime

SUPERVISOR_PROMPT_PATH = Path(__file__).parent / "prompts" / "supervisor.md"
SUPERVISOR_PROMPT = (
    SUPERVISOR_PROMPT_PATH.read_text(encoding="utf-8") if SUPERVISOR_PROMPT_PATH.exists() else ""
)

RESPONSE_PROMPT_PATH = Path(__file__).parent / "prompts" / "response.md"
RESPONSE_PROMPT = (
    RESPONSE_PROMPT_PATH.read_text(encoding="utf-8") if RESPONSE_PROMPT_PATH.exists() else ""
)

wiki_llm = llm.bind_tools([minecraft_internet_search])

def _build_node_prompt(state: AgentState, system_prompt: str = None, context: PlayerContext = None) -> list[AnyMessage]:
    """Build a prompt segment from the message history."""

    context_prompt = ""
    if context:
        context_prompt += (
            f"Player Name: {context.get('player_name', 'Unknown')}\n"
            f"Location: {context.get('location', {})}\n"
            f"Dimension: {context.get('dimension', 'overworld')}\n"
        )

    if system_prompt:
        context_prompt += f"\nSystem Prompt:\n{system_prompt}\n"

    context_prompt += "\nConversation History:\n"

    full_prompt = [SystemMessage(content=context_prompt)] if context_prompt else []
    full_prompt += state.get("messages", [])

    return full_prompt

class SupervisorIntent(BaseModel):  
    """Grade documents using a binary score for relevance check."""

    route: Literal["wiki_agent", "final_response"] = Field(
        description="Route: 'wiki_agent' if more context is necessary, or 'final_response' if ready to respond."
    )

def supervisor_agent(
    state: AgentState,
    runtime: Runtime[PlayerContext]
) -> Command[Literal["wiki_agent", "final_response"]]:

    prompt = _build_node_prompt(state=state, system_prompt=SUPERVISOR_PROMPT, context=runtime.context)

    response = llm.with_structured_output(SupervisorIntent).invoke(prompt)

    goto = response.route
    intent = "wiki_search" if goto == "wiki_agent" else "final_response"

    return Command(update={"intent": intent, "messages": [AIMessage(content=response.route)]}, goto=goto)


def wiki_agent(state: AgentState) -> Command[Literal["supervisor"]]:
    wiki_prompt = "You are a Minecraft wiki assistant. Use the minecraft_internet_search tool to find information."

    prompt = _build_node_prompt(state=state, system_prompt=wiki_prompt)
    
    response = wiki_llm.invoke(prompt)

    # Process tool calls from the response
    tool_calls = []
    wiki_result = ""
    
    if response.tool_calls:
        for tool_call in response.tool_calls:
            # Execute the tool
            result = minecraft_internet_search.invoke(tool_call["args"])
            tool_calls.append({
                "name": tool_call["name"],
                "args": tool_call["args"],
                "result": result,
            })
            wiki_result += result + "\n"
    
    return Command(
        update={
            "wiki_context": wiki_result.strip(),
            "messages": [AIMessage(content=wiki_result.strip())],
            "tool_calls": tool_calls,
            "intent": "wiki_search",
        },
        goto="supervisor",
    )

def response_agent(state: AgentState, runtime: Runtime[PlayerContext]) -> dict:
    """Generate final response to the user."""
    prompt = _build_node_prompt(
        state=state,
        system_prompt=RESPONSE_PROMPT,
        context=runtime.context
    )
    
    response = llm.invoke(prompt).content.strip()
    
    # Return a dict to update state (required by LangGraph)
    return Command(update={
        "response": response,
        "messages": [AIMessage(content=response)],
        },
        goto=END
    )

if __name__ == "__main__":
    from langchain_core.messages import convert_to_messages
    input = {
        "messages":
            [
                HumanMessage(content="What does a stone pickaxe do?")
            ]
    }
    state: AgentState = AgentState(**input)
    output = supervisor_agent(state)
    print(output)