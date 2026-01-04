from langgraph.graph import END, START, StateGraph
from src.agents.state import AgentState, PlayerContext

from langgraph.graph.state import CompiledStateGraph

from src.agents.nodes import response_agent, supervisor_agent, wiki_agent
from langchain.messages import HumanMessage
from src.config import store

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("wiki_agent", wiki_agent)
workflow.add_node("final_response", response_agent)

workflow.add_edge(START, "supervisor")

async def get_app() -> CompiledStateGraph[AgentState, None, AgentState, AgentState]:
    return workflow.compile()

if __name__ == "__main__":
    import asyncio

    async def main():
        app = await get_app()

        message = "How do i craft a beacon?"

        initial_state = AgentState(
            query=message,
            messages=[HumanMessage(content=message)],
            tool_calls=[],
            intent=None,
            target_task_done=False,
            rag_context=None,
            wiki_context=None,
            waypoints=[],
        )
        context = PlayerContext(
            player_id="example_player_name",
            player_name="example_player_name",
            location={
                "x": 123,
                "y": 64,
                "z": 100,
            },
            dimension="overworld",
        )
        store.put_message(
            writer="example_player_name",
            writer_type="human",
            message=message,
            player_id="example_player_name",
        )
        result = await app.ainvoke(
            {**initial_state},
            config={"recursion_limit": 6},
            context=context,
        )
        print(result["messages"][-1])

    asyncio.run(main())
