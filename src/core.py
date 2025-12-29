from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from src.agents.state import AgentState

from src.agents.nodes import response_agent, supervisor_agent, wiki_agent

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("wiki_agent", wiki_agent)
workflow.add_node("final_response", response_agent)

workflow.add_edge(START, "supervisor")


#memory = MemorySaver()
app = workflow.compile()

if __name__ == "__main__":
    result = app.invoke(
        {
            "messages": [
                {"role": "user", "content": "What does a stone pickaxe do?"},
            ],
            "player": {"player_id": "player123"},
            "tool_calls": [],
            "target_task_done": False,
            "waypoints": [],
        },
    )
    print(result["messages"][-1]["content"])