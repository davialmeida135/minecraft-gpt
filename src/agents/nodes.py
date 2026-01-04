from pathlib import Path
from typing import List, Literal

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import BaseModel, Field

from src.agents.state import AgentState, Message, PlayerContext, ToolCall
from src.agents.tools import minecraft_internet_search, minecraft_recipe_search
from src.config import (
    MESSAGE_HISTORY_LIMIT,
    RESPONSE_PROMPT,
    SUPERVISOR_PROMPT,
    WIKI_PROMPT,
    llm,
    store,
)

wiki_llm = llm.bind_tools([minecraft_internet_search, minecraft_recipe_search])


def _extract_tool_input(args):
    """Normalize tool arguments to a single value when possible."""
    if isinstance(args, dict):
        if "term" in args:
            return args["term"]
        if "query" in args:
            return args["query"]
        if len(args) == 1:
            return next(iter(args.values()))
    return args


def _build_node_prompt(
    state: AgentState, system_prompt: str = None, context: PlayerContext = None
) -> list[AnyMessage]:
    """Build a prompt segment from the message history."""

    retrieved_history = store.get_last_messages_for_player(
        player_id=context.get("player_id") if context else None,
        limit=MESSAGE_HISTORY_LIMIT,
    )
    message_history: List[AnyMessage] = []

    for msg in retrieved_history:
        if msg["writer_type"] == "human":
            message_history.insert(0, HumanMessage(content=msg["message"]))
        else:
            message_history.insert(0, AIMessage(content=msg["message"]))

    # Append in-flight conversation messages from state (e.g., current user query)
    # state_messages = state.get("messages") if state else None
    # if state_messages:
    #     message_history.extend(state_messages)

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
    full_prompt += message_history

    return full_prompt


class SupervisorIntent(BaseModel):
    """Grade documents using a binary score for relevance check."""

    route: Literal["wiki_agent", "final_response"] = Field(
        description="Route: 'wiki_agent' if more context is necessary, or 'final_response' if ready to respond."
    )


def supervisor_agent(
    state: AgentState, runtime: Runtime[PlayerContext]
) -> Command[Literal["wiki_agent", "final_response"]]:

    prompt = _build_node_prompt(
        state=state, system_prompt=SUPERVISOR_PROMPT, context=runtime.context
    )

    response = llm.with_structured_output(SupervisorIntent).invoke(prompt)

    goto = response.route
    intent = "wiki_search" if goto == "wiki_agent" else "final_response"

    store.put_message(
        writer="supervisor_agent",
        writer_type="AI",
        message=f"Routing to {goto}",
        player_id=runtime.context.get("player_id", "global"),
    )

    return Command(
        update={"intent": intent, "messages": [AIMessage(content=response.route)]},
        goto=goto,
    )


def wiki_agent(state: AgentState, runtime: Runtime[PlayerContext]) -> Command[Literal["supervisor"]]:

    prompt = _build_node_prompt(state=state, system_prompt=WIKI_PROMPT, context=runtime.context)

    response = wiki_llm.invoke(prompt)

    # Process tool calls from the response
    tool_calls = []
    wiki_result = ""

    if response.tool_calls:
        tool_registry = {
            "minecraft_internet_search": minecraft_internet_search,
            "minecraft_recipe_search": minecraft_recipe_search,
        }

        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool = tool_registry.get(tool_name)

            if not tool:
                continue

            try:
                result = tool.invoke(_extract_tool_input(tool_args))
            except Exception as exc:  # Keep agent alive on tool errors
                result = f"Error calling {tool_name}: {exc}"

            tool_calls.append(
                {
                    "name": tool_name,
                    "args": tool_args,
                    "result": result,
                }
            )
            wiki_result += result + "\n"

    store.put_message(
        writer="wiki_agent",
        writer_type="AI",
        message=wiki_result.strip(),
        player_id=runtime.context.get("player_id", "global"),
    )

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
        state=state, system_prompt=RESPONSE_PROMPT, context=runtime.context
    )

    response = llm.invoke(prompt).content.strip()

    store.put_message(
        writer="response_agent",
        writer_type="AI",
        message=response,
        player_id=runtime.context.get("player_id", "global"),
    )

    # Return a dict to update state (required by LangGraph)
    return Command(
        update={
            "response": response,
            "messages": [AIMessage(content=response)],
        },
        goto=END,
    )


if __name__ == "__main__":
    from langchain_core.messages import convert_to_messages

    input = {"messages": [HumanMessage(content="How to craft a piston?")]}
    state: AgentState = AgentState(**input)
    output = supervisor_agent(state)
    print(output)
