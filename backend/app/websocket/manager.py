"""
WebSocket менеджер — управляет активными соединениями стримов.
"""

import asyncio
import json
import threading
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    """Хранит активные WebSocket соединения по camera_id."""

    def __init__(self):
        # camera_id -> list of websockets
        self.active: Dict[int, list[WebSocket]] = {}

    async def connect(self, camera_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(camera_id, []).append(websocket)

    def disconnect(self, camera_id: int, websocket: WebSocket):
        if camera_id in self.active:
            try:
                self.active[camera_id].remove(websocket)
            except ValueError:
                pass

    async def broadcast(self, camera_id: int, data: dict):
        """Отправляет данные всем подписчикам камеры."""
        if camera_id not in self.active:
            return
        dead = []
        for ws in self.active[camera_id]:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(camera_id, ws)


manager = ConnectionManager()