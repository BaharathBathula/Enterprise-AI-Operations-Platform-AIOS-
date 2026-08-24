import uuid

from app.models.tool_approval import (
    ToolApproval,
    ToolApprovalStatus,
)


def test_tool_approval_defaults():
    approval = ToolApproval(
        organization_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        tool_name="create_incident",
        arguments={
            "severity": "high",
            "title": "Production API unavailable",
        },
    )

    assert approval.tool_name == "create_incident"

    assert approval.arguments == {
        "severity": "high",
        "title": "Production API unavailable",
    }

    assert approval.reviewed_by_user_id is None
    assert approval.review_note is None


def test_tool_approval_status_values():
    assert ToolApprovalStatus.pending.value == "pending"
    assert ToolApprovalStatus.approved.value == "approved"
    assert ToolApprovalStatus.rejected.value == "rejected"
    assert ToolApprovalStatus.executed.value == "executed"
