import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  MoreHorizontal,
  Search,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";

const incidents = [
  {
    id: "INC-2041",
    title: "Checkout API returning HTTP 503",
    severity: "Critical",
    status: "Open",
    source: "AIOS Agent",
    created: "4 min ago",
  },
  {
    id: "INC-2040",
    title: "Payment gateway latency above threshold",
    severity: "High",
    status: "Investigating",
    source: "AIOS Agent",
    created: "22 min ago",
  },
  {
    id: "INC-2039",
    title: "Authentication service unavailable",
    severity: "Critical",
    status: "Investigating",
    source: "Manual",
    created: "47 min ago",
  },
  {
    id: "INC-2038",
    title: "Background processing queue delayed",
    severity: "Medium",
    status: "Resolved",
    source: "AIOS Agent",
    created: "2 hrs ago",
  },
];

export default function IncidentsPage() {
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
            Incidents
          </h1>

          <p className="page-subtitle">
            Track operational incidents created
            manually or through governed AIOS agents.
          </p>
        </div>

        <button
          type="button"
          style={{
            border: "none",
            borderRadius: 10,
            background: "#111827",
            color: "#ffffff",
            padding: "10px 15px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Create incident
        </button>
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
          label="Open"
          value="12"
          detail="Requires attention"
        />

        <MetricCard
          label="Critical"
          value="3"
          detail="Highest severity"
        />

        <MetricCard
          label="Investigating"
          value="6"
          detail="Active response"
        />

        <MetricCard
          label="Resolved today"
          value="18"
          detail="Closed incidents"
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
                fontSize: 15,
                fontWeight: 700,
              }}
            >
              Incident Queue
            </div>

            <div
              style={{
                marginTop: 4,
                color: "#98a2b3",
                fontSize: 12,
              }}
            >
              Operational events across the workspace
            </div>
          </div>

          <div
            style={{
              width: 280,
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
              placeholder="Search incidents"
              style={{
                width: "100%",
                border: "none",
                outline: "none",
                fontSize: 12,
                background: "transparent",
              }}
            />
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "100px minmax(320px, 1fr) 110px 130px 130px 120px 50px",
            padding: "11px 18px",
            background: "#f9fafb",
            borderBottom: "1px solid #e4e7ec",
            color: "#667085",
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          <div>INCIDENT</div>
          <div>DESCRIPTION</div>
          <div>SEVERITY</div>
          <div>STATUS</div>
          <div>SOURCE</div>
          <div>CREATED</div>
          <div />
        </div>

        {incidents.map((incident) => (
          <div
            key={incident.id}
            style={{
              display: "grid",
              gridTemplateColumns:
                "100px minmax(320px, 1fr) 110px 130px 130px 120px 50px",
              padding: "16px 18px",
              borderBottom:
                "1px solid #f0f1f3",
              alignItems: "center",
              fontSize: 12,
            }}
          >
            <div
              style={{
                fontWeight: 700,
              }}
            >
              {incident.id}
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 9,
                  background: "#fef3f2",
                  display: "grid",
                  placeItems: "center",
                }}
              >
                <AlertTriangle
                  size={16}
                  color="#b42318"
                />
              </div>

              <div
                style={{
                  fontWeight: 600,
                }}
              >
                {incident.title}
              </div>
            </div>

            <SeverityBadge
              severity={incident.severity}
            />

            <StatusBadge
              status={incident.status}
            />

            <div
              style={{
                color: "#667085",
              }}
            >
              {incident.source}
            </div>

            <div
              style={{
                color: "#98a2b3",
              }}
            >
              {incident.created}
            </div>

            <button
              type="button"
              aria-label={`Actions for ${incident.id}`}
              style={{
                border: "none",
                background: "transparent",
                color: "#667085",
                cursor: "pointer",
              }}
            >
              <MoreHorizontal size={17} />
            </button>
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
            AI-assisted incident operations
          </div>

          <p
            style={{
              margin: "10px 0 0",
              color: "#667085",
              fontSize: 12,
              lineHeight: 1.7,
            }}
          >
            AIOS can detect operational intent,
            propose incident creation, require
            human authorization, and persist the
            approved incident with a complete audit
            trail.
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
              fontSize: 14,
              fontWeight: 700,
            }}
          >
            Mean Time to Resolution
          </div>

          <div
            style={{
              marginTop: 16,
              fontSize: 28,
              fontWeight: 700,
            }}
          >
            38m
          </div>

          <div
            style={{
              marginTop: 5,
              color: "#98a2b3",
              fontSize: 11,
            }}
          >
            14% improvement this month
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
  let background = "#fffaeb";
  let color = "#b54708";

  if (severity === "Critical") {
    background = "#fef3f2";
    color = "#b42318";
  }

  if (severity === "High") {
    background = "#fff6ed";
    color = "#c4320a";
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
  let icon = <Clock3 size={12} />;

  if (status === "Open") {
    background = "#fef3f2";
    color = "#b42318";
    icon = <AlertTriangle size={12} />;
  }

  if (status === "Resolved") {
    background = "#ecfdf3";
    color = "#067647";
    icon = <CheckCircle2 size={12} />;
  }

  return (
    <span
      style={{
        width: "fit-content",
        display: "flex",
        alignItems: "center",
        gap: 5,
        borderRadius: 999,
        padding: "5px 8px",
        background,
        color,
        fontSize: 10,
        fontWeight: 700,
      }}
    >
      {icon}
      {status}
    </span>
  );
}
