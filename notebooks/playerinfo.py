from mcpq import ChatEvent, text
from mcpq import Minecraft, Vec3
from dotenv import load_dotenv

load_dotenv()

mc = Minecraft(host="192.168.9.132", port=14445)


def myfunc(event: ChatEvent):
    if not event.message.startswith("@gpt"):
        return
    
    player = event.player
    player_info = {
        "player_id": player.id,
        "name": player.name,
        "position": {"x": player.pos.x, "y": player.pos.y, "z": player.pos.z},
    }
    print("Player Info:", player_info)
    mc.postToChat(f"{text.RED + text.BOLD}<Gepeto> {text.RESET}{text.BLUE}{player_info}{text.RESET}")

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