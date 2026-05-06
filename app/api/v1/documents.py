from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, AppError

router = APIRouter(tags=["Documents"])


@router.get("")
@require_permission("documents", "view")
async def list_documents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    doc_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []
    if doc_type:
        conditions.append("d.doc_type = :doc_type")
        params["doc_type"] = doc_type

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM documents d {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT d.id, d.title, d.doc_type, d.file_path, d.version,
               d.status, d.created_by, d.created_at,
               u.first_name || ' ' || u.last_name as author
        FROM documents d
        LEFT JOIN users u ON u.id = d.created_by
        {where} ORDER BY d.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.post("", status_code=201)
@require_permission("documents", "create")
async def create_document(
    title: str,
    doc_type: str = "general",
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_path = f"uploads/documents/{file.filename}"
    content = await file.read()

    row = await db.execute(text("""
        INSERT INTO documents (title, doc_type, file_path, file_size, mime_type, version, status, created_by)
        VALUES (:title, :doc_type, :file_path, :file_size, :mime_type, 1, 'draft', :created_by)
        RETURNING id
    """), {
        "title": title, "doc_type": doc_type, "file_path": file_path,
        "file_size": len(content), "mime_type": file.content_type,
        "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "file_path": file_path, "message": "Hujjat yaratildi"}


@router.get("/{doc_id}")
@require_permission("documents", "view")
async def get_document(
    doc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT d.*, u.first_name || ' ' || u.last_name as author
        FROM documents d
        LEFT JOIN users u ON u.id = d.created_by
        WHERE d.id = :id
    """), {"id": doc_id})
    doc = row.fetchone()
    if not doc:
        raise NotFoundError("Hujjat")
    return dict(doc._mapping)


@router.put("/{doc_id}")
@require_permission("documents", "update")
async def update_document(
    doc_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE documents SET title = COALESCE(:title, title),
            doc_type = COALESCE(:doc_type, doc_type),
            status = COALESCE(:status, status),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("title", "doc_type", "status")}, "id": doc_id})
    if not result.fetchone():
        raise NotFoundError("Hujjat")
    await db.commit()
    return {"message": "Hujjat yangilandi"}


@router.delete("/{doc_id}")
@require_permission("documents", "delete")
async def delete_document(
    doc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM documents WHERE id = :id RETURNING id"), {"id": doc_id})
    if not result.fetchone():
        raise NotFoundError("Hujjat")
    await db.commit()
    return {"message": "Hujjat o'chirildi"}


@router.post("/{doc_id}/sign")
@require_permission("documents", "update")
async def sign_document(
    doc_id: int,
    data: dict = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id, status FROM documents WHERE id = :id"), {"id": doc_id})
    doc = check.fetchone()
    if not doc:
        raise NotFoundError("Hujjat")

    await db.execute(text("""
        INSERT INTO document_signatures (document_id, user_id, signature_type, signed_at, comment)
        VALUES (:doc_id, :user_id, :sig_type, NOW(), :comment)
    """), {
        "doc_id": doc_id, "user_id": current_user["id"],
        "sig_type": (data or {}).get("signature_type", "approval"),
        "comment": (data or {}).get("comment"),
    })

    await db.execute(text("UPDATE documents SET status = 'signed', updated_at = NOW() WHERE id = :id"), {"id": doc_id})
    await db.commit()
    return {"message": "Hujjat imzolandi"}


@router.get("/{doc_id}/versions")
@require_permission("documents", "view")
async def document_versions(
    doc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT dv.id, dv.version, dv.file_path, dv.change_note, dv.created_at,
               u.first_name || ' ' || u.last_name as author
        FROM document_versions dv
        LEFT JOIN users u ON u.id = dv.created_by
        WHERE dv.document_id = :doc_id
        ORDER BY dv.version DESC
    """), {"doc_id": doc_id})
    return {"versions": [dict(r._mapping) for r in rows]}
