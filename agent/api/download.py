import os
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import verify_jwt_token
from models.models import GeneratedFile

router = APIRouter()


def _get_user_id(token: str) -> int:
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return int(payload.get("sub"))


@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """Download a generated file by ID. Requires JWT token as query param."""
    user_id = _get_user_id(token)

    gf = db.query(GeneratedFile).filter(GeneratedFile.id == file_id).first()
    if not gf:
        raise HTTPException(status_code=404, detail="File not found")
    if gf.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.exists(gf.path):
        raise HTTPException(status_code=404, detail="File no longer exists on disk")

    return FileResponse(
        path=gf.path,
        filename=gf.filename,
        media_type=gf.mime_type or "application/octet-stream",
    )


@router.get("/generated-files/{message_id}")
async def list_generated_files(
    message_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """List generated files for a message."""
    user_id = _get_user_id(token)

    files = (
        db.query(GeneratedFile)
        .filter(
            GeneratedFile.message_id == message_id,
            GeneratedFile.user_id == user_id,
        )
        .order_by(GeneratedFile.created_at)
        .all()
    )

    return [
        {
            "id": f.id,
            "filename": f.filename,
            "size": f.size,
            "mimeType": f.mime_type,
            "createdAt": f.created_at.isoformat() if f.created_at else None,
        }
        for f in files
    ]
