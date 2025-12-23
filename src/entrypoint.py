from typing import Literal, TypedDict
from typing_extensions import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-5-nano")

class MinecraftState(TypedDict):
    messages: list[str]
    response: str


def send_reply(state: MinecraftState) -> dict:
    """Send the email response"""
    # Integrate with email service
    print(f"Sending reply: {state['response']}...")
    return state

def draft_response(state: MinecraftState) -> Command[Literal["send_reply"]]:
    """Generate response using context and route based on quality"""

    # Build the prompt with formatted context
    draft_prompt = f"""
    Escreva uma resposta amigável e útil para a seguinte mensagem do jogador no Minecraft:
    {state['messages']}
    Lembre-se de manter a resposta curta e direta ao ponto, não queremos poluir o chat do jogo.
    """

    response = llm.invoke(draft_prompt)

    return Command(
        update={"response": response.content},
        goto="send_reply"
    )
