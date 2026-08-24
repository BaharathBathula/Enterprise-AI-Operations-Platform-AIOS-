import {
  Check,
  Clock3,
  Eye,
  ShieldCheck,
  X,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";

const approvals = [
  {
    id: "APR-1048",
    tool: "create_incident",
    requester: "Operations Agent",
    action: "Create critical incident",
    detail: "Checkout API returning HTTP 503 errors",
    severity: "Critical",
    requested: "2 min ago",
    status: "Pending",
  },
  {
    id: "APR-1047",
    tool: "create_incident",
    requester: "AIOS Copilot",
    action: "Create high severity incident",
    detail: "Payment gateway latency above threshold",
    severity: "High",
    requested: "18 min ago",
    status: "Pending",
  },
  {
    id: "APR-1046",
    tool: "create_incident",
    requester: "Operations Agent",
    action: "Create critical incident",
    detail: "Authentication service unavailable",
    severity: "Critical",
    requested: "42 min ago",
    status: "Approved",
  },
  {
    id: "APR-1045",
    tool: "create_incident",
    requester: "AIOS Copilot",
    action: "Create medium severity incident",
    detail: "Background processing queue delayed",
    severity: "Medium",
    requested: "1 hr ago",
    status: "Rejected",
  },
];

export default function ApprovalsPage() {
  return (
    <AppShell>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 20,
        }}
      >
        <div>
          <h1 className="page-title">
            Agent Approvals
          </h1>

          <p className="page-subtitle">
            Review and authorize consequential
            actions proposed by AIOS agents.
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
          value="7"
          detail="Requires human review"
        />

        <MetricCard
          label="Approved today"
          value="23"
          detail="Authorized actions"
        />

        <MetricCard
          label="Rejected today"
          value="3"
          detail="Prevented executions"
        />

        <MetricCard
          label="Executed"
          value="326"
          detail="Governed tool actions"
        />
      </section>

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
            borderBottom: "1px solid #e4e7ec",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
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
              Review tool calls before execution
            </div>
          </div>

          <select
            defaultValue="all"
            style={{
              border: "1px solid #d0d5dd",
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
          </select>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "100px 150px minmax(300px, 1fr) 110px 110px 120px",
            padding: "11px 18px",
            background: "#f9fafb",
            borderBottom: "1px solid #e4e7ec",
            color: "#667085",
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          <div>REQUEST</div>
          <div>TOOL</div>
          <div>ACTION</div>
          <div>SEVERITY</div>
          <div>STATUS</div>
          <div>ACTIONS</div>
        </div>

        {approvals.map((approval) => (
          <div
            key={approval.id}
            style={{
              display: "grid",
              gridTemplateColumns:
                "100px 150px minmax(300px, 1fr) 110px 110px 120px",
              padding: "16px 18px",
              borderBottom:
                "1px solid #f0f1f3",
              alignItems: "center",
              fontSize: 12,
            }}
          >
            <div>
              <div
                style={{
                  fontWeight: 700,
                }}
              >
                {approval.id}
              </div>

              <div
                style={{
                  marginTop: 4,
                  color: "#98a2b3",
                  fontSize: 10,
                }}
              >
                {approval.requested}
              </div>
            </div>

            <div>
              <code
                style={{
                  fontSize: 11,
                  background: "#f2f4f7",
                  borderRadius: 6,
                  padding: "4px 6px",
                }}
              >
                {approval.tool}
              </code>
            </div>

            <div>
              <div
                style={{
                  fontWeight: 600,
                }}
              >
                {approval.action}
              </div>

              <div
                style={{
                  marginTop: 4,
                  color: "#667085",
                  fontSize: 11,
                }}
              >
                {approval.detail}
              </div>

              <div
                style={{
                  marginTop: 5,
                  color: "#98a2b3",
                  fontSize: 10,
                }}
              >
                Requested by{" "}
                {approval.requester}
              </div>
            </div>

            <SeverityBadge
              severity={approval.severity}
            />

            <StatusBadge
              status={approval.status}
            />

            <div
              style={{
                display: "flex",
                gap: 6,
              }}
            >
              {approval.status ===
              "Pending" ? (
                <>
                  <ActionButton
                    label="Approve"
                    icon={<Check size={14} />}
                  />

                  <ActionButton
                    label="Reject"
                    icon={<X size={14} />}
                  />
                </>
              ) : (
                <ActionButton
                  label="View"
                  icon={<Eye size={14} />}
                />
              )}
            </div>
          </div>
        ))}
      </section>

      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1.4fr) minmax(300px, 1fr)",
          gap: 18,
          marginTop: 18,
        }}
      >
        <article
          className="card"
          style={{
            padding: 20,
          }}
        >
          <div
            style={{
              fontSize: 14,
              fontWeight: 700,
            }}
          >
            Why approval matters
          </div>

          <p
            style={{
              margin: "10px 0 0",
              color: "#667085",
              fontSize: 12,
              lineHeight: 1.7,
            }}
          >
            AIOS separates autonomous reasoning
            from consequential execution. Read-only
            tools can run automatically, while
            write-capable tools require explicit
            authorization before they can change
            enterprise state.
          </p>
        </article>

        <article
          className="card"
          style={{
            padding: 20,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 14,
              fontWeight: 700,
            }}
          >
            <Clock3 size={16} />
            Approval SLA
          </div>

          <div
            style={{
              marginTop: 16,
              fontSize: 26,
              fontWeight: 700,
            }}
          >
            4m 18s
          </div>

          <div
            style={{
              marginTop: 4,
              color: "#98a2b3",
              fontSize: 11,
            }}
          >
            Average review time today
          </div>
        </article>
      </section>
    </AppShell>
  );
}


function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
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


function SeverityBadge({
  severity,
}: {
  severity: string;
}) {
  let background = "#f2f4f7";
  let color = "#475467";

  if (severity === "Critical") {
    background = "#fef3f2";
    color = "#b42318";
  }

  if (severity === "High") {
    background = "#fff6ed";
    color = "#c4320a";
  }

  if (severity === "Medium") {
    background = "#fffaeb";
    color = "#b54708";
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
      }}
    >
      {severity}
    </span>
  );
}


function StatusBadge({
  status,
}: {
  status: string;
}) {
  let background = "#fffaeb";
  let color = "#b54708";

  if (status === "Approved") {
    background = "#ecfdf3";
    color = "#067647";
  }

  if (status === "Rejected") {
    background = "#fef3f2";
    color = "#b42318";
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
      }}
    >
      {status}
    </span>
  );
}


function ActionButton({
  label,
  icon,
}: {
  label: string;
  icon: React.ReactNode;
}) {
  return (
    <button
      type="button"
      title={label}
      aria-label={label}
      style={{
        width: 32,
        height: 32,
        border: "1px solid #d0d5dd",
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
