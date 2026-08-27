import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.audit_log import AuditLog
from app.models.organization import Organization
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.tool_approval import (
    ToolApproval,
    ToolApprovalStatus,
)
from app.models.user import User


def _create_user(
    db: Session,
    email: str,
) -> User:
    user = User(
        email=email,
        full_name="Approval Test User",
        hashed_password="not-used-in-test",
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    return user


def _create_organization(
    db: Session,
    name: str,
) -> Organization:
    organization = Organization(
        name=name,
        slug=f"approval-{uuid.uuid4()}",
    )

    db.add(organization)
    db.flush()

    return organization


def _add_membership(
    db: Session,
    organization: Organization,
    user: User,
    role: OrganizationRole,
) -> OrganizationMember:
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role=role,
    )

    db.add(membership)
    db.flush()

    return membership


def _create_approval(
    db: Session,
    organization: Organization,
    requester: User,
    *,
    status: ToolApprovalStatus = ToolApprovalStatus.pending,
) -> ToolApproval:
    approval = ToolApproval(
        organization_id=organization.id,
        requested_by_user_id=requester.id,
        conversation_id=None,
        tool_name="create_incident",
        arguments={
            "title": "Database latency incident",
            "description": "Integration test incident",
            "severity": "high",
        },
        status=status,
    )

    db.add(approval)
    db.flush()

    return approval


def _auth_headers(
    user: User,
) -> dict[str, str]:
    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_member_cannot_list_tool_approvals(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "approval-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Approval Member Org",
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals"
        ),
        headers=_auth_headers(member),
    )

    assert response.status_code == 403


def test_admin_can_list_tool_approvals(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "approval-list-requester@example.com",
    )

    admin = _create_user(
        db_session,
        "approval-list-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Approval List Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()
    }

    assert str(approval.id) in ids


def test_requester_cannot_approve_own_tool_request(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "self-approval@example.com",
    )

    organization = _create_organization(
        db_session,
        "Self Approval Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/approve"
        ),
        headers=_auth_headers(requester),
        json={
            "review_note": "Trying self approval",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Users cannot approve their own tool requests",
    }


def test_different_admin_can_approve_tool_request(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "approval-requester@example.com",
    )

    approver = _create_user(
        db_session,
        "approval-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Approval Admin Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        approver,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/approve"
        ),
        headers=_auth_headers(approver),
        json={
            "review_note":
                "Approved by independent administrator",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "approved"

    assert (
        body["reviewed_by_user_id"]
        == str(approver.id)
    )


def test_member_cannot_approve_tool_request(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "member-approval-requester@example.com",
    )

    reviewer = _create_user(
        db_session,
        "member-reviewer@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Approval Denied Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        reviewer,
        OrganizationRole.member,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/approve"
        ),
        headers=_auth_headers(reviewer),
        json={
            "review_note": "Member trying approval",
        },
    )

    assert response.status_code == 403


def test_admin_can_reject_pending_tool_request(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "reject-requester@example.com",
    )

    reviewer = _create_user(
        db_session,
        "reject-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Reject Approval Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        reviewer,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/reject"
        ),
        headers=_auth_headers(reviewer),
        json={
            "review_note":
                "Rejected during integration test",
        },
    )

    assert response.status_code == 200

    assert response.json()["status"] == "rejected"


def test_pending_tool_request_cannot_be_executed(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "pending-execute-requester@example.com",
    )

    admin = _create_user(
        db_session,
        "pending-execute-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Pending Execution Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
        status=ToolApprovalStatus.pending,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/execute"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail":
            "Only approved tool requests can be executed",
    }


def test_rejected_tool_request_cannot_be_executed(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "rejected-execute-requester@example.com",
    )

    admin = _create_user(
        db_session,
        "rejected-execute-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Rejected Execution Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
        status=ToolApprovalStatus.rejected,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/execute"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 409


def test_approved_tool_request_executes_and_becomes_executed(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "execute-requester@example.com",
    )

    approver = _create_user(
        db_session,
        "execute-approver@example.com",
    )

    organization = _create_organization(
        db_session,
        "Approved Execution Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        approver,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
    )

    db_session.commit()

    approve_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/approve"
        ),
        headers=_auth_headers(approver),
        json={
            "review_note": "Approved for execution",
        },
    )

    assert approve_response.status_code == 200

    execute_response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/execute"
        ),
        headers=_auth_headers(approver),
    )

    assert execute_response.status_code == 200

    body = execute_response.json()

    assert body["success"] is True

    db_session.expire_all()

    refreshed_approval = db_session.get(
        ToolApproval,
        approval.id,
    )

    assert refreshed_approval is not None

    assert (
        refreshed_approval.status
        == ToolApprovalStatus.executed
    )

    assert refreshed_approval.executed_at is not None


def test_failed_tool_execution_creates_audit_log(
    client: TestClient,
    db_session: Session,
):
    requester = _create_user(
        db_session,
        "failed-audit-requester@example.com",
    )

    admin = _create_user(
        db_session,
        "failed-audit-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Failed Execution Audit Org",
    )

    _add_membership(
        db_session,
        organization,
        requester,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    approval = _create_approval(
        db_session,
        organization,
        requester,
        status=ToolApprovalStatus.approved,
    )

    approval.arguments = {
        "title": "Invalid severity incident",
        "description": "Force tool execution failure",
        "severity": "invalid-severity",
    }

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/tool-approvals/"
            f"{approval.id}/execute"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 409

    db_session.expire_all()

    statement = (
        select(AuditLog)
        .where(
            AuditLog.organization_id
            == organization.id,
            AuditLog.resource_id
            == str(approval.id),
            AuditLog.action
            == "tool.approval_execution_failed",
        )
    )

    audit_log = db_session.scalar(statement)

    assert audit_log is not None
    assert audit_log.event_type == "tool_execution"
    assert audit_log.outcome == "failed"
    assert audit_log.user_id == admin.id
    assert audit_log.resource_type == "tool_approval"

    assert audit_log.details is not None

    assert (
        audit_log.details["tool_name"]
        == "create_incident"
    )

    assert (
        audit_log.details["requested_by_user_id"]
        == str(requester.id)
    )

    assert (
        "Invalid incident severity"
        in audit_log.details["error"]
    )


def test_tool_approval_cannot_be_read_from_foreign_organization(
    client: TestClient,
    db_session: Session,
):
    requester_b = _create_user(
        db_session,
        "approval-foreign-requester@example.com",
    )

    admin_a = _create_user(
        db_session,
        "approval-foreign-admin@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Approval Foreign A",
    )

    organization_b = _create_organization(
        db_session,
        "Approval Foreign B",
    )

    _add_membership(
        db_session,
        organization_a,
        admin_a,
        OrganizationRole.admin,
    )

    _add_membership(
        db_session,
        organization_b,
        requester_b,
        OrganizationRole.member,
    )

    approval_b = _create_approval(
        db_session,
        organization_b,
        requester_b,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/tool-approvals/"
            f"{approval_b.id}"
        ),
        headers=_auth_headers(admin_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Tool approval request not found",
    }
