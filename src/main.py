from mcpq import ChatEvent, text

from src.config import mc
from src.core import app


def myfunc(event: ChatEvent):
    if not event.message.startswith("@gpt"):
        return

    # Normalize user message by stripping the trigger token
    user_message = event.message.replace("@gpt", "", 1).strip()

    config = {"configurable": {"thread_id": event.player.id}}

    initial_state = {
        "messages": [{"role": "user", "content": user_message}],
        "player": {"player_id": event.player.id},
        "tool_calls": [],
        "intent": None,
        "target_task_done": False,
        "rag_context": None,
        "wiki_context": None,
        "waypoints": [],
    }

    response = app.invoke(initial_state, timeout=60, config=config)

    mc.postToChat(
        f"{text.RED + text.BOLD}<Gepeto> {text.RESET} {text.BLUE} {response['response']}{text.RESET}"
    )


mc.events.chat.register(myfunc)
print("Listener started - press Ctrl+C to stop")

# Keep the script running indefinitely
import time

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    mc.events.projectile_hit.stop()
    print("Listener stopped - connection will close automatically")
