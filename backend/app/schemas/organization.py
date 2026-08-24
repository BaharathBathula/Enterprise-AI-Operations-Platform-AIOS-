import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.organization_member import OrganizationRole


class OrganizationCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=255,
    )

    slug: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationMembershipResponse(BaseModel):
    organization: OrganizationResponse
    role: OrganizationRole


class OrganizationMemberAdd(BaseModel):
    email: EmailStr

    role: OrganizationRole = OrganizationRole.member


class OrganizationMemberRoleUpdate(BaseModel):
    role: OrganizationRole


class OrganizationMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: EmailStr
    full_name: str
    role: OrganizationRole
    created_at: datetime
