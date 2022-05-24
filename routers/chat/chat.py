import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from database import models, schemas
from dependencies import get_current_user_by_query
from .socket_manager import socket_manager

router = APIRouter(prefix='/chat', tags=['chat'])


@router.websocket('/ws/chat/')
async def chat(
        websocket: WebSocket,
        current_user: models.User = Depends(get_current_user_by_query),
):
    if current_user:
        await socket_manager.connect(websocket, current_user)
        response = {
            'user': current_user.username,
            'message': 'connected to the chat',
            'connection': True
        }
        await socket_manager.send(response)

        try:
            while True:
                data = await websocket.receive_json()
                await socket_manager.send(data)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, current_user)
            response['message'] = 'left the chat'
            await socket_manager.send(response)
