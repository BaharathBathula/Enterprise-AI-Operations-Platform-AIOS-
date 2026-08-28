import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.organization_dependencies import (
    get_current_membership,
    require_organization_admin,
)
from app.db.database import get_db
from app.models.document import Document
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User
from app.schemas.document import (
    DocumentProcessingResponse,
    DocumentResponse,
)
from app.services.audit_service import log_audit_event
from app.services.document_processing_service import (
    DocumentProcessingError,
    process_document,
)
from app.services.document_service import (
    create_document_record,
    delete_document,
    get_document,
    list_documents,
)
from app.services.storage_service import (
    FileTooLargeError,
    UnsupportedFileTypeError,
    save_uploaded_file,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/documents",
    tags=["Documents"],
)


def require_document_write_access(
    membership: OrganizationMember = Depends(
        get_current_membership,
    ),
) -> OrganizationMember:
    allowed_roles = {
        OrganizationRole.owner,
        OrganizationRole.admin,
        OrganizationRole.member,
    }

    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document write access required",
        )

    return membership


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    organization_id: uuid.UUID,
    file: UploadFile = File(...),
    _: OrganizationMember = Depends(
        require_document_write_access,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    original_filename = (
        file.filename
        or "document.pdf"
    )

    content_type = (
        file.content_type
        or "application/octet-stream"
    )

    try:
        (
            storage_path,
            file_size,
            stored_filename,
        ) = await save_uploaded_file(
            file=file,
            organization_id=organization_id,
        )

    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            ),
            detail=str(exc),
        ) from exc

    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            ),
            detail=str(exc),
        ) from exc

    document = create_document_record(
        db=db,
        organization_id=organization_id,
        user_id=current_user.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        content_type=content_type,
        file_size=file_size,
        storage_path=storage_path,
    )

    log_audit_event(
        db=db,
        action="document.uploaded",
        resource_type="document",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=str(document.id),
        details={
            "filename":
                document.original_filename,
            "file_size":
                document.file_size,
        },
    )

    return document


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def get_documents(
    organization_id: uuid.UUID,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    db: Session = Depends(get_db),
) -> list[Document]:
    return list_documents(
        db=db,
        organization_id=organization_id,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document_by_id(
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    db: Session = Depends(get_db),
) -> Document:
    document = get_document(
        db=db,
        organization_id=organization_id,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.post(
    "/{document_id}/process",
    response_model=DocumentProcessingResponse,
)
def process_uploaded_document(
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    _: OrganizationMember = Depends(
        require_document_write_access,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> DocumentProcessingResponse:
    document = get_document(
        db=db,
        organization_id=organization_id,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        processed_document = process_document(
            db=db,
            document=document,
        )

    except DocumentProcessingError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc

    log_audit_event(
        db=db,
        action="document.processed",
        resource_type="document",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=str(
            processed_document.id
        ),
        details={
            "status":
                processed_document.status.value,
            "page_count":
                processed_document.page_count,
        },
    )

    return DocumentProcessingResponse(
        id=processed_document.id,
        status=processed_document.status,
        page_count=(
            processed_document.page_count
        ),
        processing_error=(
            processed_document.processing_error
        ),
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_document(
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> Response:
    document = get_document(
        db=db,
        organization_id=organization_id,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    original_filename = (
        document.original_filename
    )

    document_resource_id = str(
        document.id
    )

    delete_document(
        db=db,
        document=document,
    )

    log_audit_event(
        db=db,
        action="document.deleted",
        resource_type="document",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=document_resource_id,
        details={
            "filename":
                original_filename,
        },
    )

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        ),
    )
