from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.entrypoint import MinecraftState, draft_response, send_reply
from src.agents.nodes import supervisor_agent, wiki_agent

workflow = StateGraph(MinecraftState)

workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("wiki_agent", wiki_agent)
workflow.add_node("draft_response", draft_response)
workflow.add_node("send_reply", send_reply)

workflow.add_edge(START, "supervisor")
workflow.add_edge("supervisor", "wiki_agent")
workflow.add_edge("supervisor", "draft_response")
workflow.add_edge("wiki_agent", "draft_response")
workflow.add_edge("draft_response", "send_reply")
workflow.add_edge("send_reply", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
