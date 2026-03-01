"""
WebSocket connection manager for real-time notifications.
"""

import json
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        """Broadcast a message to all connected clients."""
        message = json.dumps(data)
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_notification(self, notif_type: str, title: str, message: str, data: dict = None):
        """Convenience: broadcast a notification event."""
        await self.broadcast({
            "event": "notification",
            "type": notif_type,
            "title": title,
            "message": message,
            "data": data or {},
        })


manager = ConnectionManager()
