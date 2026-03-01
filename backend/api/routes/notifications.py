"""
Notifications API routes + WebSocket endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.db import crud
from backend.api.websocket import manager

router = APIRouter(prefix="/notifications", tags=["notifications"])
ws_router = APIRouter(tags=["websocket"])


@router.get("")
def list_notifications(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    notifs, total = crud.get_notifications(db, page=page, per_page=per_page)
    unread = crud.get_unread_count(db)
    return {
        "notifications": [
            {
                "id": n.id, "type": n.type, "title": n.title,
                "message": n.message, "data": n.data,
                "is_read": n.is_read, "created_at": n.created_at,
            }
            for n in notifs
        ],
        "unread_count": unread,
        "total": total,
    }


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db)):
    return {"count": crud.get_unread_count(db)}


@router.patch("/{notif_id}/read")
def mark_read(notif_id: int, db: Session = Depends(get_db)):
    n = crud.mark_notification_read(db, notif_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Marked as read"}


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    crud.mark_all_read(db)
    return {"message": "All notifications marked as read"}


@router.delete("/{notif_id}")
def delete_notification(notif_id: int, db: Session = Depends(get_db)):
    if not crud.delete_notification(db, notif_id):
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}


@ws_router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
