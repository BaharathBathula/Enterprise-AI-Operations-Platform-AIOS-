import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.organization_dependencies import (
    get_current_membership,
)
from app.db.database import get_db
from app.models.message import MessageRole
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.rag import (
    RAGAnswerResponse,
    RAGQuestionRequest,
    RAGSource,
)
from app.services.conversation_service import (
    add_message,
    create_conversation,
    get_conversation,
    list_messages,
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
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> RAGAnswerResponse:
    if request.conversation_id is not None:
        conversation = get_conversation(
            db=db,
            organization_id=organization_id,
            conversation_id=request.conversation_id,
            user_id=current_user.id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

    else:
        title = request.question.strip()[:80]

        conversation = create_conversation(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
            title=title,
        )

    previous_messages = list_messages(
        db=db,
        conversation_id=conversation.id,
        organization_id=organization_id,
    )

    add_message(
        db=db,
        conversation_id=conversation.id,
        organization_id=organization_id,
        role=MessageRole.user,
        content=request.question,
    )

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
            messages=previous_messages,
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

    add_message(
        db=db,
        conversation_id=conversation.id,
        organization_id=organization_id,
        role=MessageRole.assistant,
        content=answer,
    )

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
        conversation_id=conversation.id,
        answer=answer,
        sources=sources,
    )
