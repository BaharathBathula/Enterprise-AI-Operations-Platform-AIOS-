import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.organization_dependencies import (
    get_current_membership,
)
from app.db.database import get_db
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
)
from app.services.audit_service import log_audit_event
from app.services.conversation_service import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_messages,
    list_user_conversations,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_conversation(
    organization_id: uuid.UUID,
    request: ConversationCreate,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    conversation = create_conversation(
        db=db,
        organization_id=organization_id,
        current_user=current_user,
        title=request.title,
    )

    log_audit_event(
        db=db,
        action="conversation.created",
        resource_type="conversation",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=str(conversation.id),
        details={
            "title": conversation.title,
        },
    )

    return conversation


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def get_conversations(
    organization_id: uuid.UUID,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> list[ConversationResponse]:
    return list_user_conversations(
        db=db,
        organization_id=organization_id,
        user_id=current_user.id,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation_by_id(
    organization_id: uuid.UUID,
    conversation_id: uuid.UUID,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> ConversationDetailResponse:
    conversation = get_conversation(
        db=db,
        organization_id=organization_id,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = list_messages(
        db=db,
        conversation_id=conversation.id,
        organization_id=organization_id,
    )

    return ConversationDetailResponse(
        id=conversation.id,
        organization_id=conversation.organization_id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse.model_validate(message)
            for message in messages
        ],
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_conversation(
    organization_id: uuid.UUID,
    conversation_id: uuid.UUID,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> Response:
    conversation = get_conversation(
        db=db,
        organization_id=organization_id,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    conversation_resource_id = str(
        conversation.id
    )

    conversation_title = conversation.title

    delete_conversation(
        db=db,
        conversation=conversation,
    )

    log_audit_event(
        db=db,
        action="conversation.deleted",
        resource_type="conversation",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=conversation_resource_id,
        details={
            "title": conversation_title,
        },
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
