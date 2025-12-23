from src.config import mc
from src.core import app
from mcpq import ChatEvent, text

def myfunc(event: ChatEvent):
    if not event.message.startswith("@gpt"):  
        return
    
    config = {"configurable": {"thread_id": event.player.id}}
    response = app.invoke(
        {"messages": [event.message]},timeout=60, config=config
    )
    mc.postToChat(f"{text.RED + text.BOLD}<Gepeto> {text.RESET} {text.BLUE} {response['response']}{text.RESET}")

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