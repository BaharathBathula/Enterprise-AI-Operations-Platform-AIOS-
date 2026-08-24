import {
  Activity,
  Bot,
  CheckCircle2,
  FileText,
  Search,
  ShieldCheck,
  TriangleAlert,
  User,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";

const events = [
  {
    id: "AUD-8821",
    action: "tool.executed",
    resource: "create_incident",
    actor: "AIOS Agent",
    category: "Tool",
    result: "Success",
    time: "2 min ago",
  },
  {
    id: "AUD-8820",
    action: "tool.approved",
    resource: "APR-1048",
    actor: "Workspace Admin",
    category: "Approval",
    result: "Success",
    time: "4 min ago",
  },
  {
    id: "AUD-8819",
    action: "incident.created",
    resource: "INC-2041",
    actor: "AIOS Agent",
    category: "Incident",
    result: "Success",
    time: "4 min ago",
  },
  {
    id: "AUD-8818",
    action: "knowledge.search",
    resource: "production-runbook.pdf",
    actor: "AIOS Copilot",
    category: "Knowledge",
    result: "Success",
    time: "12 min ago",
  },
  {
    id: "AUD-8817",
    action: "document.indexed",
    resource: "incident-response-policy.pdf",
    actor: "System",
    category: "Document",
    result: "Success",
    time: "28 min ago",
  },
  {
    id: "AUD-8816",
    action: "tool.rejected",
    resource: "APR-1045",
    actor: "Workspace Admin",
    category: "Approval",
    result: "Prevented",
    time: "1 hr ago",
  },
];

export default function AuditPage() {
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
            Audit Activity
          </h1>

          <p className="page-subtitle">
            Trace enterprise AI decisions, approvals,
            tool executions, and operational changes.
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
          Audit logging active
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
          label="Events today"
          value="2,481"
          detail="Across all AIOS services"
        />

        <MetricCard
          label="Tool executions"
          value="326"
          detail="Governed actions"
        />

        <MetricCard
          label="Approvals"
          value="33"
          detail="Human decisions"
        />

        <MetricCard
          label="Prevented actions"
          value="3"
          detail="Rejected executions"
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
            justifyContent: "space-between",
            alignItems: "center",
            gap: 20,
          }}
        >
          <div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                fontSize: 15,
                fontWeight: 700,
              }}
            >
              <Activity size={17} />
              Event Timeline
            </div>

            <div
              style={{
                marginTop: 4,
                color: "#98a2b3",
                fontSize: 12,
              }}
            >
              Immutable operational activity history
            </div>
          </div>

          <div
            style={{
              display: "flex",
              gap: 10,
            }}
          >
            <div
              style={{
                width: 260,
                display: "flex",
                alignItems: "center",
                gap: 8,
                border: "1px solid #d0d5dd",
                borderRadius: 9,
                padding: "8px 10px",
                color: "#98a2b3",
              }}
            >
              <Search size={15} />

              <input
                type="text"
                placeholder="Search audit events"
                style={{
                  width: "100%",
                  border: "none",
                  outline: "none",
                  background: "transparent",
                  fontSize: 12,
                }}
              />
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
                All events
              </option>
              <option value="tool">
                Tool
              </option>
              <option value="approval">
                Approval
              </option>
              <option value="incident">
                Incident
              </option>
              <option value="knowledge">
                Knowledge
              </option>
            </select>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "105px 170px minmax(220px, 1fr) 160px 120px 110px 110px",
            padding: "11px 18px",
            background: "#f9fafb",
            borderBottom: "1px solid #e4e7ec",
            color: "#667085",
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          <div>EVENT</div>
          <div>ACTION</div>
          <div>RESOURCE</div>
          <div>ACTOR</div>
          <div>CATEGORY</div>
          <div>RESULT</div>
          <div>TIME</div>
        </div>

        {events.map((event) => (
          <div
            key={event.id}
            style={{
              display: "grid",
              gridTemplateColumns:
                "105px 170px minmax(220px, 1fr) 160px 120px 110px 110px",
              padding: "15px 18px",
              borderBottom: "1px solid #f0f1f3",
              alignItems: "center",
              fontSize: 12,
            }}
          >
            <div
              style={{
                fontWeight: 700,
              }}
            >
              {event.id}
            </div>

            <div>
              <code
                style={{
                  background: "#f2f4f7",
                  borderRadius: 6,
                  padding: "4px 6px",
                  fontSize: 10,
                }}
              >
                {event.action}
              </code>
            </div>

            <div
              style={{
                fontWeight: 600,
              }}
            >
              {event.resource}
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 7,
                color: "#667085",
              }}
            >
              <User size={13} />
              {event.actor}
            </div>

            <CategoryBadge
              category={event.category}
            />

            <ResultBadge
              result={event.result}
            />

            <div
              style={{
                color: "#98a2b3",
              }}
            >
              {event.time}
            </div>
          </div>
        ))}
      </section>

      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(3, minmax(0, 1fr))",
          gap: 18,
          marginTop: 18,
        }}
      >
        <GovernanceCard
          icon={<Bot size={18} />}
          title="Agent traceability"
          description={
            "Track which AI agent proposed or executed each action."
          }
        />

        <GovernanceCard
          icon={<ShieldCheck size={18} />}
          title="Human provenance"
          description={
            "Preserve the identity of reviewers who authorize governed actions."
          }
        />

        <GovernanceCard
          icon={<FileText size={18} />}
          title="Enterprise evidence"
          description={
            "Maintain an operational record for investigations and compliance."
          }
        />
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


function CategoryBadge({
  category,
}: {
  category: string;
}) {
  let icon = <Activity size={12} />;

  if (category === "Tool") {
    icon = <Bot size={12} />;
  }

  if (category === "Approval") {
    icon = <ShieldCheck size={12} />;
  }

  if (category === "Incident") {
    icon = <TriangleAlert size={12} />;
  }

  if (category === "Document") {
    icon = <FileText size={12} />;
  }

  return (
    <span
      style={{
        width: "fit-content",
        display: "flex",
        alignItems: "center",
        gap: 5,
        borderRadius: 999,
        background: "#f2f4f7",
        color: "#475467",
        padding: "5px 8px",
        fontSize: 10,
        fontWeight: 700,
      }}
    >
      {icon}
      {category}
    </span>
  );
}


function ResultBadge({
  result,
}: {
  result: string;
}) {
  const prevented = result === "Prevented";

  return (
    <span
      style={{
        width: "fit-content",
        display: "flex",
        alignItems: "center",
        gap: 5,
        borderRadius: 999,
        background: prevented
          ? "#fef3f2"
          : "#ecfdf3",
        color: prevented
          ? "#b42318"
          : "#067647",
        padding: "5px 8px",
        fontSize: 10,
        fontWeight: 700,
      }}
    >
      {prevented ? (
        <TriangleAlert size={12} />
      ) : (
        <CheckCircle2 size={12} />
      )}

      {result}
    </span>
  );
}


function GovernanceCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
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
          width: 36,
          height: 36,
          borderRadius: 9,
          background: "#f1f3f7",
          display: "grid",
          placeItems: "center",
          color: "#475467",
        }}
      >
        {icon}
      </div>

      <div
        style={{
          marginTop: 13,
          fontSize: 13,
          fontWeight: 700,
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 6,
          color: "#667085",
          fontSize: 11,
          lineHeight: 1.6,
        }}
      >
        {description}
      </div>
    </article>
  );
}
