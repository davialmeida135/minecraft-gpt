import uuid
from mcpq import ChatEvent, text

from src.config import mc, store
from src.core import get_app
from src.agents.state import AgentState, PlayerContext
from langchain.messages import HumanMessage
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)  # Tune as needed


async def async_call_agent(event: ChatEvent):
    if not event.message.startswith("@gpt"):
        return

    # Normalize user message by stripping the trigger token
    user_message = event.message.replace("@gpt", "", 1).strip()

    config = {"configurable": {"thread_id": asyncio.current_task().get_name()}}

    initial_state = AgentState(
        query=user_message,
        messages=[HumanMessage(content=user_message)],
        tool_calls=[],
        intent=None,
        target_task_done=False,
        rag_context=None,
        wiki_context=None,
        waypoints=[],
    )

    context = PlayerContext(
        player_id=event.player.id,
        player_name=event.player.name,
        location={
            "x": event.player.pos.x,
            "y": event.player.pos.y,
            "z": event.player.pos.z,
        },
        dimension=event.player.world,
    )

    store.put_message(
        writer=event.player.id,
        writer_type="human",
        message=user_message,
        player_id=event.player.id,
    )

    print(
        f"Received message from {event.player.name} on thread {asyncio.current_task().get_name()}: {user_message}"
    )

    app = await get_app()
    response = await app.ainvoke(
        {
            **initial_state,
        },
        config=config,
        context=context,
    )

    mc.postToChat(
        f"{text.RED + text.BOLD}<Gepeto>{text.RESET}{text.GREEN}@{event.player.name}{text.RESET}{text.BLUE} {response['response']}{text.RESET}"
    )
    print(
        f"Responded to {event.player.name} on thread {asyncio.current_task().get_name()}"
    )


def call_agent(event: ChatEvent):
    # Offload the async handler to a background thread to avoid blocking the event loop
    executor.submit(asyncio.run, async_call_agent(event))


mc.events.chat.register(call_agent)
print("Listener started - press Ctrl+C to stop")

# Keep the script running indefinitely
import time

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    mc.events.chat.stop()
    executor.shutdown(wait=False)
    print("Listener stopped - connection will close automatically")
