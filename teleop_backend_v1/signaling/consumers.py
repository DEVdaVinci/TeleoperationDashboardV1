import json
import time
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer

# Tracks everyone currently connected: { userName: {"channel_name": ..., "role": ...} }
CONNECTED_CLIENTS = {}


class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Read ?userName=...&role=...&password=... from the WebSocket URL
        query_params = parse_qs(self.scope.get("query_string", b"").decode("utf-8"))
        self.user_name = query_params.get("userName", [f"Peer-{int(time.time())}"])[0]
        self.role = query_params.get("role", ["operator"])[0]
        password = query_params.get("password", ["x"])[0]

        if password != "x":
            await self.close(code=4001)
            return

        # Add this socket to a shared broadcast group so we can announce topology updates
        self.room_group_name = "teleop_signaling_hub"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        CONNECTED_CLIENTS[self.user_name] = {
            "channel_name": self.channel_name,
            "role": self.role,
            "connected_at": time.time(),
        }
        await self.broadcast_topology()

    async def disconnect(self, code):
        CONNECTED_CLIENTS.pop(self.user_name, None)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.broadcast_topology()

    async def receive(self, text_data=None, bytes_data=None):
        # In Phase 2-4, we will add handlers here for operatorFrame, robotFrame, and WebRTC offers
        if text_data:
            data = json.loads(text_data)
            await self.send_json({"type": "echo", "received": data})

    async def broadcast_topology(self):
        peers = [
            {"userName": uname, "role": info["role"], "connectedAt": info["connected_at"]}
            for uname, info in CONNECTED_CLIENTS.items()
        ]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "RelayMessage",
                "payload": {"type": "topologyUpdate", "peers": peers},
            },
        )

    async def RelayMessage(self, event):
        await self.send_json(event["payload"])

    async def send_json(self, payload: dict):
        await self.send(text_data=json.dumps(payload))