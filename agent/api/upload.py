from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import shutil
import mimetypes

from core.config import settings
from core.database import get_db
from core.security import verify_jwt_token
from models.models import Attachment

router = APIRouter()

# Supported file types and their categories
FILE_CATEGORIES = {
    # Tabular data
    '.csv': 'data', '.tsv': 'data', '.xlsx': 'data', '.xls': 'data',
    '.parquet': 'data', '.feather': 'data',
    # Text/documents
    '.txt': 'documents', '.md': 'documents', '.pdf': 'documents',
    '.doc': 'documents', '.docx': 'documents',
    # Code/scripts
    '.py': 'scripts', '.r': 'scripts', '.R': 'scripts',
    '.sh': 'scripts', '.bash': 'scripts',
    # Bioinformatics
    '.fasta': 'sequences', '.fa': 'sequences', '.fastq': 'sequences',
    '.fq': 'sequences', '.gb': 'sequences', '.gbk': 'sequences',
    '.gff': 'sequences', '.gff3': 'sequences', '.gtf': 'sequences',
    '.bed': 'sequences', '.bam': 'sequences', '.sam': 'sequences',
    '.vcf': 'sequences',
    # Images
    '.png': 'images', '.jpg': 'images', '.jpeg': 'images',
    '.gif': 'images', '.svg': 'images', '.tif': 'images', '.tiff': 'images',
    # Archives
    '.zip': 'archives', '.tar': 'archives', '.gz': 'archives',
    '.tar.gz': 'archives', '.tgz': 'archives',
    # JSON/config
    '.json': 'data', '.yaml': 'data', '.yml': 'data', '.toml': 'data',
}


def get_file_category(filename: str) -> str:
    """Determine file category based on extension."""
    suffix = Path(filename).suffix.lower()
    return FILE_CATEGORIES.get(suffix, 'other')


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: int = Form(...),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Upload a file to the unified user workspace.
    
    Files are organized as:
      /opt/biomni/upload/user_{user_id}/{category}/{filename}
    
    A symlink is also created in the agent data directory so the
    agent can easily access uploaded files during code execution.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.replace("Bearer ", "").strip()
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(payload.get("sub"))

    # Determine file category and build organized path
    safe_name = Path(file.filename).name
    category = get_file_category(safe_name)
    
    # Unified upload directory: /opt/biomni/upload/user_{user_id}/{category}/
    upload_dir = Path(settings.AGENT_UPLOAD_DATA_PATH) / f"user_{user_id}" / category
    upload_dir.mkdir(parents=True, exist_ok=True)

    # If file already exists, add a short uuid prefix to avoid collision
    file_path = upload_dir / safe_name
    if file_path.exists():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        stored_name = f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"
        file_path = upload_dir / stored_name
    else:
        stored_name = safe_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size = file_path.stat().st_size

    # Create symlink in agent working directory for easy access during execution
    agent_upload_dir = Path(settings.AGENT_DATA_PATH) / "user_uploads"
    agent_upload_dir.mkdir(parents=True, exist_ok=True)
    symlink_path = agent_upload_dir / stored_name
    try:
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
        symlink_path.symlink_to(file_path)
    except Exception:
        pass  # Symlink is optional, don't fail the upload

    attachment = Attachment(
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=None,
        filename=safe_name,
        path=str(file_path),
        size=size,
        mime_type=file.content_type or mimetypes.guess_type(safe_name)[0],
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
        "category": category,
    }
