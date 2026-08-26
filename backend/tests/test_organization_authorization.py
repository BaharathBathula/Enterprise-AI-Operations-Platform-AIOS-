import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.organization_dependencies import (
    get_current_membership,
    require_organization_admin,
    require_organization_member,
    require_organization_owner,
)
from app.models.organization_member import (
    OrganizationRole,
)


def test_member_has_member_access():
    membership = SimpleNamespace(
        role=OrganizationRole.member,
    )

    result = require_organization_member(
        membership
    )

    assert result is membership


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

    with pytest.raises(
        HTTPException
    ) as exc:
        require_organization_admin(
            membership
        )

    assert (
        exc.value.status_code
        == 403
    )

    assert (
        exc.value.detail
        == "Organization administrator access required"
    )


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

    with pytest.raises(
        HTTPException
    ) as exc:
        require_organization_owner(
            membership
        )

    assert (
        exc.value.status_code
        == 403
    )

    assert (
        exc.value.detail
        == "Organization owner access required"
    )


def test_member_cannot_access_owner_route():
    membership = SimpleNamespace(
        role=OrganizationRole.member,
    )

    with pytest.raises(
        HTTPException
    ) as exc:
        require_organization_owner(
            membership
        )

    assert (
        exc.value.status_code
        == 403
    )


def test_cross_tenant_user_is_treated_as_organization_not_found():
    db = MagicMock()

    organization_b_id = (
        uuid.uuid4()
    )

    user_from_org_a = (
        SimpleNamespace(
            id=uuid.uuid4(),
        )
    )

    with patch(
        "app.api.organization_dependencies.get_membership",
        return_value=None,
    ) as mocked_get_membership:
        with pytest.raises(
            HTTPException
        ) as exc:
            get_current_membership(
                organization_id=(
                    organization_b_id
                ),
                current_user=(
                    user_from_org_a
                ),
                db=db,
            )

    assert (
        exc.value.status_code
        == 404
    )

    assert (
        exc.value.detail
        == "Organization not found"
    )

    mocked_get_membership.assert_called_once_with(
        db=db,
        organization_id=(
            organization_b_id
        ),
        user_id=(
            user_from_org_a.id
        ),
    )


def test_membership_lookup_uses_authenticated_user_id():
    db = MagicMock()

    organization_id = (
        uuid.uuid4()
    )

    authenticated_user = (
        SimpleNamespace(
            id=uuid.uuid4(),
        )
    )

    expected_membership = (
        SimpleNamespace(
            organization_id=(
                organization_id
            ),
            user_id=(
                authenticated_user.id
            ),
            role=(
                OrganizationRole.member
            ),
        )
    )

    with patch(
        "app.api.organization_dependencies.get_membership",
        return_value=(
            expected_membership
        ),
    ) as mocked_get_membership:
        result = (
            get_current_membership(
                organization_id=(
                    organization_id
                ),
                current_user=(
                    authenticated_user
                ),
                db=db,
            )
        )

    assert (
        result
        is expected_membership
    )

    mocked_get_membership.assert_called_once_with(
        db=db,
        organization_id=(
            organization_id
        ),
        user_id=(
            authenticated_user.id
        ),
    )


def test_cross_tenant_lookup_does_not_leak_role_information():
    db = MagicMock()

    foreign_organization_id = (
        uuid.uuid4()
    )

    authenticated_user = (
        SimpleNamespace(
            id=uuid.uuid4(),
        )
    )

    with patch(
        "app.api.organization_dependencies.get_membership",
        return_value=None,
    ):
        with pytest.raises(
            HTTPException
        ) as exc:
            get_current_membership(
                organization_id=(
                    foreign_organization_id
                ),
                current_user=(
                    authenticated_user
                ),
                db=db,
            )

    assert (
        exc.value.status_code
        == 404
    )

    assert (
        "admin"
        not in exc.value.detail.lower()
    )

    assert (
        "owner"
        not in exc.value.detail.lower()
    )

    assert (
        "member"
        not in exc.value.detail.lower()
    )
