from langgraph.graph import END, START, StateGraph
from src.agents.state import AgentState

from langgraph.graph.state import CompiledStateGraph

from src.agents.nodes import response_agent, supervisor_agent, wiki_agent
from langchain.messages import HumanMessage

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
        result = await app.ainvoke(
            {
                "messages": [HumanMessage(content="What does a stone pickaxe do?")],
                "player": {"player_id": "player123"},
                "tool_calls": [],
                "target_task_done": False,
                "waypoints": [],
            },
        )
        print(result["messages"][-1])

    asyncio.run(main())
