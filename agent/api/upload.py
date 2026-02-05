from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import shutil

from core.config import settings
from core.database import get_db
from core.security import verify_jwt_token
from models.models import Attachment

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: int = Form(...),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Upload a file and store metadata in DB."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.replace("Bearer ", "").strip()
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(payload.get("sub"))

    # Save file to local storage
    safe_name = Path(file.filename).name
    upload_dir = Path(settings.AGENT_UPLOAD_DATA_PATH) / "uploads" / str(user_id) / str(conversation_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid.uuid4().hex}_{safe_name}"
    file_path = upload_dir / stored_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size = file_path.stat().st_size

    attachment = Attachment(
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=None,
        filename=safe_name,
        path=str(file_path),
        size=size,
        mime_type=file.content_type,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return {
        "id": attachment.id,
        "filename": attachment.filename,
        "path": attachment.path,
        "size": attachment.size,
        "mimeType": attachment.mime_type,
    }
