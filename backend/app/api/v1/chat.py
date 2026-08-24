import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.organization_dependencies import (
    get_current_membership,
)
from app.db.database import get_db
from app.models.organization_member import OrganizationMember
from app.schemas.rag import (
    RAGAnswerResponse,
    RAGQuestionRequest,
    RAGSource,
)
from app.services.embedding_service import (
    EmbeddingGenerationError,
)
from app.services.rag_service import (
    RAGGenerationError,
    generate_grounded_answer,
)
from app.services.retrieval_service import (
    retrieve_relevant_chunks,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/chat",
    tags=["RAG Chat"],
)


@router.post(
    "",
    response_model=RAGAnswerResponse,
)
def ask_organization_documents(
    organization_id: uuid.UUID,
    request: RAGQuestionRequest,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    db: Session = Depends(get_db),
) -> RAGAnswerResponse:
    try:
        chunks = retrieve_relevant_chunks(
            db=db,
            organization_id=organization_id,
            question=request.question,
            limit=request.top_k,
        )

        answer = generate_grounded_answer(
            question=request.question,
            chunks=chunks,
        )

    except EmbeddingGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except RAGGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    sources = [
        RAGSource(
            document_id=chunk.document_id,
            filename=chunk.filename,
            page_number=chunk.page_number,
            similarity_score=round(
                chunk.similarity_score,
                4,
            ),
        )
        for chunk in chunks
    ]

    return RAGAnswerResponse(
        answer=answer,
        sources=sources,
    )
