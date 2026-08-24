from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.organization_dependencies import (
    require_organization_admin,
    require_organization_owner,
)
from app.models.organization_member import (
    OrganizationRole,
)


def test_owner_has_admin_access():
    membership = SimpleNamespace(
        role=OrganizationRole.owner,
    )

    result = require_organization_admin(
        membership
    )

    assert result is membership


def test_admin_has_admin_access():
    membership = SimpleNamespace(
        role=OrganizationRole.admin,
    )

    result = require_organization_admin(
        membership
    )

    assert result is membership


def test_member_cannot_access_admin_route():
    membership = SimpleNamespace(
        role=OrganizationRole.member,
    )

    with pytest.raises(HTTPException) as exc:
        require_organization_admin(
            membership
        )

    assert exc.value.status_code == 403


def test_only_owner_has_owner_access():
    membership = SimpleNamespace(
        role=OrganizationRole.owner,
    )

    result = require_organization_owner(
        membership
    )

    assert result is membership


def test_admin_cannot_access_owner_route():
    membership = SimpleNamespace(
        role=OrganizationRole.admin,
    )

    with pytest.raises(HTTPException) as exc:
        require_organization_owner(
            membership
        )

    assert exc.value.status_code == 403
