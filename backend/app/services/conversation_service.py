import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.user import User


def create_conversation(
    db: Session,
    *,
    organization_id: uuid.UUID,
    current_user: User,
    title: str = "New conversation",
) -> Conversation:
    conversation = Conversation(
        organization_id=organization_id,
        user_id=current_user.id,
        title=title.strip() or "New conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def list_user_conversations(
    db: Session,
    *,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(
            Conversation.organization_id == organization_id,
            Conversation.user_id == user_id,
        )
        .order_by(
            Conversation.updated_at.desc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_conversation(
    db: Session,
    *,
    organization_id: uuid.UUID,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Conversation | None:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.organization_id == organization_id,
        Conversation.user_id == user_id,
    )

    return db.scalar(statement)


def list_messages(
    db: Session,
    *,
    conversation_id: uuid.UUID,
    organization_id: uuid.UUID,
) -> list[Message]:
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.organization_id == organization_id,
        )
        .order_by(
            Message.created_at.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def add_message(
    db: Session,
    *,
    conversation_id: uuid.UUID,
    organization_id: uuid.UUID,
    role: MessageRole,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        organization_id=organization_id,
        role=role,
        content=content.strip(),
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def update_conversation_title(
    db: Session,
    *,
    conversation: Conversation,
    title: str,
) -> Conversation:
    conversation.title = title.strip()

    db.commit()
    db.refresh(conversation)

    return conversation


def delete_conversation(
    db: Session,
    *,
    conversation: Conversation,
) -> None:
    db.execute(
        delete(Message).where(
            Message.conversation_id == conversation.id,
        )
    )

    db.delete(conversation)
    db.commit()
