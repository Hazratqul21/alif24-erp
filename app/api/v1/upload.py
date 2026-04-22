import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.dependencies import get_current_user

router = APIRouter(tags=["Upload"])

UPLOAD_DIR = "/app/static/uploads"
ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
}
MAX_SIZE_MB = 20


@router.post(""))
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Ruxsat etilmagan fayl turi: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Fayl hajmi {MAX_SIZE_MB}MB dan oshmasligi kerak")

    ext = os.path.splitext(file.filename or "file")[1].lower() or ".bin"
    filename = f"{uuid.uuid4().hex}{ext}"

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "filename": filename,
        "original_name": file.filename,
        "url": f"/static/uploads/{filename}",
        "size": len(content),
        "content_type": file.content_type,
    }
