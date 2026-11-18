import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

OrgRoleField = Literal["org_admin", "admin", "technician", "requester"]


class _Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MeResponse(_Out):
    id: uuid.UUID
    email: str
    full_name: str
    is_super_admin: bool


class MyOrganization(BaseModel):
    id: uuid.UUID
    name: str
    role: OrgRoleField


class MyOrganizationsResponse(BaseModel):
    data: list[MyOrganization]


class OrganizationCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class OrganizationResponse(_Out):
    id: uuid.UUID
    name: str
    created_at: datetime


class MembershipCreate(BaseModel):
    email: EmailStr
    role: OrgRoleField


class MembershipResponse(_Out):
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    role: OrgRoleField


class TeamCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    member_count: int


class TeamListResponse(BaseModel):
    data: list[TeamResponse]
    next_cursor: str | None


class TeamMemberCreate(BaseModel):
    user_id: uuid.UUID


class TeamMemberResponse(BaseModel):
    team_id: uuid.UUID
    user_id: uuid.UUID
