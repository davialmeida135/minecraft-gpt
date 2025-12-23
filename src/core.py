from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy
from langgraph.graph import StateGraph, START, END
from src.entrypoint import draft_response, send_reply, MinecraftState
# Create the graph
workflow = StateGraph(MinecraftState)

workflow.add_node("draft_response", draft_response)
workflow.add_node("send_reply", send_reply)

workflow.add_edge(START, "draft_response")
workflow.add_edge("send_reply", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)