"""
Notification service — creates notifications and broadcasts via WebSocket.
"""

from sqlalchemy.orm import Session
from backend.db import crud
from backend.api.websocket import manager


async def notify(
    db: Session,
    type: str,
    title: str,
    message: str,
    data: dict = None,
) -> dict:
    """Create a notification in the DB and push via WebSocket."""
    notif = crud.create_notification(db, type=type, title=title, message=message, data=data or {})
    await manager.send_notification(
        notif_type=type,
        title=title,
        message=message,
        data={"id": notif.id, **(data or {})},
    )
    return {"id": notif.id, "title": title, "message": message}
