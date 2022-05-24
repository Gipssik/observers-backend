from fastapi import WebSocket

from database import models


class SocketManager:
    def __init__(self):
        self.active_connections: list[(WebSocket, models.User)] = []

    async def connect(self, websocket: WebSocket, user: models.User):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: models.User):
        self.active_connections.remove((websocket, user))

    async def send(self, data):
        for ws, user in self.active_connections:
            await ws.send_json(data)


socket_manager = SocketManager()
