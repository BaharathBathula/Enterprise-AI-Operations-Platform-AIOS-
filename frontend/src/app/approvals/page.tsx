"use client";

import {
  Check,
  CheckCircle2,
  Clock3,
  Loader2,
  Play,
  RefreshCw,
  ShieldCheck,
  X,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import {
  clearSession,
  getSession,
} from "@/lib/session";
import type {
  ToolApproval,
  ToolApprovalStatus,
} from "@/lib/types";


type FilterStatus =
  | "all"
  | ToolApprovalStatus;


type ActionState = {
  approvalId: string;
  action:
    | "approve"
    | "reject"
    | "execute";
} | null;


export default function ApprovalsPage() {
  const router = useRouter();

  const [approvals, setApprovals] =
    useState<ToolApproval[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [filter, setFilter] =
    useState<FilterStatus>("all");

  const [actionState, setActionState] =
    useState<ActionState>(null);


  const handleUnauthorized =
    useCallback(() => {
      clearSession();
      router.replace("/login");
    }, [router]);


  const loadApprovals =
    useCallback(async () => {
      const session = getSession();

      if (!session) {
        handleUnauthorized();
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const query =
          filter === "all"
            ? ""
            : `?status=${encodeURIComponent(
                filter,
              )}`;

        const response =
          await apiRequest<
            ToolApproval[]
          >(
            `/organizations/${session.organizationId}/tool-approvals${query}`,
            {
              token:
                session.accessToken,
            },
          );

        setApprovals(response);
      } catch (requestError) {
        if (
          requestError instanceof
            ApiError &&
          requestError.status === 401
        ) {
          handleUnauthorized();
          return;
        }

        if (
          requestError instanceof
          ApiError
        ) {
          setError(
            requestError.detail,
          );
        } else {
          setError(
            "Unable to load approval requests.",
          );
        }
      } finally {
        setLoading(false);
      }
    }, [
      filter,
      handleUnauthorized,
    ]);


  useEffect(() => {
    void loadApprovals();
  }, [loadApprovals]);


  async function performAction(
    approval: ToolApproval,
    action:
      | "approve"
      | "reject"
      | "execute",
  ) {
    const session = getSession();

    if (!session) {
      handleUnauthorized();
      return;
    }

    setActionState({
      approvalId: approval.id,
      action,
    });

    setError(null);

    try {
      if (
        action === "approve" ||
        action === "reject"
      ) {
        await apiRequest<ToolApproval>(
          `/organizations/${session.organizationId}/tool-approvals/${approval.id}/${action}`,
          {
            method: "POST",
            token:
              session.accessToken,
            body: JSON.stringify({
              review_note:
                action === "approve"
                  ? "Approved from AIOS operations console."
                  : "Rejected from AIOS operations console.",
            }),
          },
        );
      } else {
        await apiRequest<{
          success: boolean;
          message: string | null;
          error: string | null;
          data: Record<
            string,
            unknown
          >;
        }>(
          `/organizations/${session.organizationId}/tool-approvals/${approval.id}/execute`,
          {
            method: "POST",
            token:
              session.accessToken,
          },
        );
      }

      await loadApprovals();
    } catch (requestError) {
      if (
        requestError instanceof
          ApiError &&
        requestError.status === 401
      ) {
        handleUnauthorized();
        return;
      }

      if (
        requestError instanceof
        ApiError
      ) {
        setError(
          requestError.detail,
        );
      } else {
        setError(
          `Unable to ${action} the request.`,
        );
      }
    } finally {
      setActionState(null);
    }
  }


  const metrics = useMemo(() => {
    return {
      pending: approvals.filter(
        (approval) =>
          approval.status ===
          "pending",
      ).length,

      approved: approvals.filter(
        (approval) =>
          approval.status ===
          "approved",
      ).length,

      rejected: approvals.filter(
        (approval) =>
          approval.status ===
          "rejected",
      ).length,

      executed: approvals.filter(
        (approval) =>
          approval.status ===
          "executed",
      ).length,
    };
  }, [approvals]);


  return (
    <AppShell>
      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "flex-start",
          gap: 20,
        }}
      >
        <div>
          <h1 className="page-title">
            Agent Approvals
          </h1>

          <p className="page-subtitle">
            Review, authorize, reject,
            and execute consequential
            actions proposed by AIOS.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            borderRadius: 999,
            background: "#ecfdf3",
            color: "#067647",
            padding: "8px 11px",
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          <ShieldCheck size={15} />
          Human-in-the-loop enabled
        </div>
      </div>

      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(4, minmax(0, 1fr))",
          gap: 18,
          marginTop: 26,
        }}
      >
        <MetricCard
          label="Pending"
          value={metrics.pending}
          detail="Requires human review"
        />

        <MetricCard
          label="Approved"
          value={metrics.approved}
          detail="Ready for execution"
        />

        <MetricCard
          label="Rejected"
          value={metrics.rejected}
          detail="Prevented actions"
        />

        <MetricCard
          label="Executed"
          value={metrics.executed}
          detail="Completed actions"
        />
      </section>

      {error && (
        <div
          style={{
            marginTop: 18,
            padding: "12px 14px",
            borderRadius: 10,
            border:
              "1px solid #fecdca",
            background: "#fef3f2",
            color: "#b42318",
            fontSize: 12,
          }}
        >
          {error}
        </div>
      )}

      <section
        className="card"
        style={{
          marginTop: 18,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: 18,
            borderBottom:
              "1px solid #e4e7ec",
            display: "flex",
            alignItems: "center",
            justifyContent:
              "space-between",
            gap: 16,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 15,
                fontWeight: 700,
              }}
            >
              Approval Queue
            </div>

            <div
              style={{
                marginTop: 4,
                color: "#98a2b3",
                fontSize: 12,
              }}
            >
              Live governed tool requests
              from the AIOS backend
            </div>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <select
              value={filter}
              onChange={(event) =>
                setFilter(
                  event.target
                    .value as FilterStatus,
                )
              }
              style={{
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                background: "#ffffff",
                padding: "8px 10px",
                color: "#475467",
                fontSize: 12,
                outline: "none",
              }}
            >
              <option value="all">
                All requests
              </option>

              <option value="pending">
                Pending
              </option>

              <option value="approved">
                Approved
              </option>

              <option value="rejected">
                Rejected
              </option>

              <option value="executed">
                Executed
              </option>
            </select>

            <button
              type="button"
              onClick={() =>
                void loadApprovals()
              }
              disabled={loading}
              aria-label="Refresh approvals"
              title="Refresh approvals"
              style={{
                width: 34,
                height: 34,
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                background: "#ffffff",
                color: "#475467",
                display: "grid",
                placeItems: "center",
                cursor: loading
                  ? "not-allowed"
                  : "pointer",
              }}
            >
              <RefreshCw
                size={15}
                className={
                  loading
                    ? "spin"
                    : undefined
                }
              />
            </button>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "150px minmax(220px, 1fr) minmax(300px, 1.5fr) 110px 160px",
            padding: "11px 18px",
            background: "#f9fafb",
            borderBottom:
              "1px solid #e4e7ec",
            color: "#667085",
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          <div>TOOL</div>
          <div>REQUEST</div>
          <div>ARGUMENTS</div>
          <div>STATUS</div>
          <div>ACTIONS</div>
        </div>

        {loading ? (
          <LoadingState />
        ) : approvals.length === 0 ? (
          <EmptyState />
        ) : (
          approvals.map(
            (approval) => (
              <ApprovalRow
                key={approval.id}
                approval={approval}
                actionState={
                  actionState
                }
                onAction={
                  performAction
                }
              />
            ),
          )
        )}
      </section>

      <section
        className="card"
        style={{
          marginTop: 18,
          padding: 20,
        }}
      >
        <div
          style={{
            fontSize: 14,
            fontWeight: 700,
          }}
        >
          Governed execution model
        </div>

        <div
          style={{
            marginTop: 10,
            color: "#667085",
            fontSize: 12,
            lineHeight: 1.7,
          }}
        >
          Pending requests can be
          approved or rejected. Approval
          authorizes the request but does
          not execute it. An approved
          request must then be explicitly
          executed, preserving the
          separation between human
          authorization and enterprise
          state mutation.
        </div>
      </section>
    </AppShell>
  );
}


function ApprovalRow({
  approval,
  actionState,
  onAction,
}: {
  approval: ToolApproval;
  actionState: ActionState;
  onAction: (
    approval: ToolApproval,
    action:
      | "approve"
      | "reject"
      | "execute",
  ) => Promise<void>;
}) {
  const busy =
    actionState?.approvalId ===
    approval.id;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "150px minmax(220px, 1fr) minmax(300px, 1.5fr) 110px 160px",
        padding: "16px 18px",
        borderBottom:
          "1px solid #f0f1f3",
        alignItems: "center",
        fontSize: 12,
      }}
    >
      <div>
        <code
          style={{
            fontSize: 10,
            background: "#f2f4f7",
            borderRadius: 6,
            padding: "5px 7px",
          }}
        >
          {approval.tool_name}
        </code>
      </div>

      <div>
        <div
          style={{
            fontWeight: 600,
          }}
        >
          {shortId(approval.id)}
        </div>

        <div
          style={{
            marginTop: 4,
            color: "#98a2b3",
            fontSize: 10,
          }}
        >
          {formatDate(
            approval.created_at,
          )}
        </div>
      </div>

      <div
        style={{
          paddingRight: 20,
        }}
      >
        <pre
          style={{
            margin: 0,
            padding: 10,
            borderRadius: 8,
            background: "#f8fafc",
            color: "#475467",
            fontSize: 10,
            lineHeight: 1.5,
            whiteSpace: "pre-wrap",
            overflowWrap:
              "anywhere",
            fontFamily:
              "ui-monospace, SFMono-Regular, Menlo, monospace",
          }}
        >
          {JSON.stringify(
            approval.arguments,
            null,
            2,
          )}
        </pre>
      </div>

      <StatusBadge
        status={approval.status}
      />

      <div
        style={{
          display: "flex",
          gap: 7,
        }}
      >
        {busy ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 7,
              color: "#667085",
              fontSize: 11,
            }}
          >
            <Loader2
              size={14}
              className="spin"
            />

            Working
          </div>
        ) : (
          <>
            {approval.status ===
              "pending" && (
              <>
                <ActionButton
                  label="Approve"
                  icon={
                    <Check
                      size={14}
                    />
                  }
                  onClick={() =>
                    void onAction(
                      approval,
                      "approve",
                    )
                  }
                />

                <ActionButton
                  label="Reject"
                  icon={
                    <X size={14} />
                  }
                  onClick={() =>
                    void onAction(
                      approval,
                      "reject",
                    )
                  }
                />
              </>
            )}

            {approval.status ===
              "approved" && (
              <ActionButton
                label="Execute"
                icon={
                  <Play size={14} />
                }
                onClick={() =>
                  void onAction(
                    approval,
                    "execute",
                  )
                }
              />
            )}

            {approval.status ===
              "executed" && (
              <div
                style={{
                  display: "flex",
                  alignItems:
                    "center",
                  gap: 6,
                  color: "#067647",
                  fontSize: 11,
                  fontWeight: 600,
                }}
              >
                <CheckCircle2
                  size={14}
                />

                Completed
              </div>
            )}

            {approval.status ===
              "rejected" && (
              <div
                style={{
                  color: "#b42318",
                  fontSize: 11,
                  fontWeight: 600,
                }}
              >
                Blocked
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}


function ActionButton({
  label,
  icon,
  onClick,
}: {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      title={label}
      aria-label={label}
      onClick={onClick}
      style={{
        width: 34,
        height: 34,
        border:
          "1px solid #d0d5dd",
        borderRadius: 8,
        background: "#ffffff",
        display: "grid",
        placeItems: "center",
        color: "#475467",
        cursor: "pointer",
      }}
    >
      {icon}
    </button>
  );
}


function StatusBadge({
  status,
}: {
  status: ToolApprovalStatus;
}) {
  let background = "#fffaeb";
  let color = "#b54708";

  if (status === "approved") {
    background = "#eff8ff";
    color = "#175cd3";
  }

  if (status === "rejected") {
    background = "#fef3f2";
    color = "#b42318";
  }

  if (status === "executed") {
    background = "#ecfdf3";
    color = "#067647";
  }

  return (
    <span
      style={{
        width: "fit-content",
        borderRadius: 999,
        padding: "5px 8px",
        background,
        color,
        fontSize: 10,
        fontWeight: 700,
        textTransform:
          "capitalize",
      }}
    >
      {status}
    </span>
  );
}


function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: number;
  detail: string;
}) {
  return (
    <article
      className="card"
      style={{
        padding: 20,
      }}
    >
      <div
        style={{
          color: "#667085",
          fontSize: 12,
        }}
      >
        {label}
      </div>

      <div
        style={{
          marginTop: 7,
          fontSize: 28,
          fontWeight: 700,
        }}
      >
        {value}
      </div>

      <div
        style={{
          marginTop: 5,
          color: "#98a2b3",
          fontSize: 11,
        }}
      >
        {detail}
      </div>
    </article>
  );
}


function LoadingState() {
  return (
    <div
      style={{
        padding: 48,
        display: "flex",
        alignItems: "center",
        justifyContent:
          "center",
        gap: 8,
        color: "#667085",
        fontSize: 12,
      }}
    >
      <Loader2
        size={16}
        className="spin"
      />

      Loading approval requests...
    </div>
  );
}


function EmptyState() {
  return (
    <div
      style={{
        padding: 48,
        textAlign: "center",
      }}
    >
      <Clock3
        size={24}
        color="#98a2b3"
      />

      <div
        style={{
          marginTop: 10,
          fontSize: 13,
          fontWeight: 700,
        }}
      >
        No approval requests
      </div>

      <div
        style={{
          marginTop: 5,
          color: "#98a2b3",
          fontSize: 11,
        }}
      >
        Governed agent requests will
        appear here.
      </div>
    </div>
  );
}


function shortId(
  id: string,
): string {
  if (id.length <= 12) {
    return id;
  }

  return `${id.slice(
    0,
    8,
  )}...`;
}


function formatDate(
  value: string,
): string {
  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return date.toLocaleString();
}
