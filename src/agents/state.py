from typing import TypedDict, Literal, List, Dict, Any, Optional


class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class ToolCall(TypedDict):
    name: str
    args: Dict[str, Any]
    result: Any


class PlayerContext(TypedDict, total=False):
    player_id: str  # UUID ou nick normalizado
    location: Dict[str, float]  # {x, y, z}, se você tiver isso da mcpq
    dimension: str  # overworld, nether, end


class AgentState(TypedDict):
    messages: List[Message]  # histórico curto de chat
    player: PlayerContext  # contexto de quem falou
    tool_calls: List[ToolCall]  # chamadas recentes de tools
    intent: Optional[str]  # ex: "wiki_search", "navigate"
    target_task_done: bool  # para encerrar o loop rápido
    rag_context: Optional[str]  # contexto retornado do RAG
    wiki_context: Optional[str]  # contexto retornado do Minecraft Wiki
    waypoints: List[Dict[str, Any]]  # últimos waypoints relevantes
    response: Optional[str]  # resposta final gerada pelo agente
