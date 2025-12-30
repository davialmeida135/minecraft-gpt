from operator import add
from typing import Annotated, TypedDict, Literal, List, Dict, Any, Optional
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from langchain.messages import AnyMessage


class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class ToolCall(TypedDict):
    name: str
    args: Dict[str, Any]
    result: Any


class PlayerContext(TypedDict, total=False):
    player_id: str  # UUID ou nick normalizado
    player_name: Optional[str]
    location: Dict[str, float]  # {x, y, z}, se você tiver isso da mcpq
    dimension: str  # overworld, nether, end


class AgentState(TypedDict):
    query: str  # pergunta original do jogador
    messages: Annotated[list[AnyMessage], add_messages]  
    player: PlayerContext  # contexto de quem falou
    tool_calls: Annotated[List[ToolCall], add]  # chamadas recentes de tools
    intent: Optional[str]  # ex: "wiki_search", "navigate"
    target_task_done: bool  # para encerrar o loop rápido
    rag_context: Optional[str]  # contexto retornado do RAG
    wiki_context: Optional[str]  # contexto retornado do Minecraft Wiki
    waypoints: List[Dict[str, Any]]  # últimos waypoints relevantes
    response: Optional[str]  # resposta final gerada pelo agente