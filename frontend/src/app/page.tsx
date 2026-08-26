"use client";

import Link from "next/link";
import {
  Activity,
  Bot,
  FileText,
  RefreshCw,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { AppShell } from "@/components/app-shell";
import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import {
  getSession,
} from "@/lib/session";


type DocumentRecord = {
  id: string;
  original_filename: string;
  status: string;
  created_at: string;
};


type Incident = {
  id: string;
  title: string;
  description: string;
  severity:
    | "low"
    | "medium"
    | "high"
    | "critical";
  status:
    | "open"
    | "investigating"
    | "resolved";
  source: string;
  created_at: string;
};


type ToolApproval = {
  id: string;
  tool_name: string;
  status: string;
  created_at: string;
};


type AuditLog = {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details:
    | Record<string, unknown>
    | null;
  created_at: string;
};


type DashboardData = {
  documents: DocumentRecord[];
  incidents: Incident[];
  approvals: ToolApproval[];
  audit: AuditLog[];
};


export default function Home() {
  const [data, setData] =
    useState<DashboardData>({
      documents: [],
      incidents: [],
      approvals: [],
      audit: [],
    });

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  const loadDashboard =
    useCallback(async () => {
      const session = getSession();

      if (!session) {
        setError(
          "No active session. Sign in to load workspace data.",
        );
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      const organizationId =
        session.organizationId;

      const token =
        session.accessToken;

      try {
        const [
          documentsResult,
          incidentsResult,
          approvalsResult,
          auditResult,
        ] = await Promise.allSettled([
          apiRequest<DocumentRecord[]>(
            `/organizations/${organizationId}/documents`,
            {
              token,
            },
          ),

          apiRequest<Incident[]>(
            `/organizations/${organizationId}/incidents`,
            {
              token,
            },
          ),

          apiRequest<ToolApproval[]>(
            `/organizations/${organizationId}/tool-approvals?limit=500`,
            {
              token,
            },
          ),

          apiRequest<AuditLog[]>(
            `/organizations/${organizationId}/audit?limit=100`,
            {
              token,
            },
          ),
        ]);

        const nextData: DashboardData = {
          documents:
            documentsResult.status ===
            "fulfilled"
              ? documentsResult.value
              : [],

          incidents:
            incidentsResult.status ===
            "fulfilled"
              ? incidentsResult.value
              : [],

          approvals:
            approvalsResult.status ===
            "fulfilled"
              ? approvalsResult.value
              : [],

          audit:
            auditResult.status ===
            "fulfilled"
              ? auditResult.value
              : [],
        };

        setData(nextData);

        const failures = [
          documentsResult,
          incidentsResult,
          approvalsResult,
          auditResult,
        ].filter(
          (result) =>
            result.status ===
            "rejected",
        );

        if (failures.length > 0) {
          setError(
            "Some dashboard data could not be loaded. The available workspace data is shown below.",
          );
        }
      } catch (requestError) {
        if (
          requestError instanceof
          ApiError
        ) {
          setError(
            requestError.detail,
          );
        } else {
          setError(
            "Unable to load the operations overview.",
          );
        }
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);


  const metrics =
    useMemo(() => {
      const openIncidents =
        data.incidents.filter(
          (incident) =>
            incident.status !==
            "resolved",
        );

      const criticalIncidents =
        openIncidents.filter(
          (incident) =>
            incident.severity ===
            "critical",
        );

      const pendingApprovals =
        data.approvals.filter(
          (approval) =>
            approval.status ===
            "pending",
        );

      const approved =
        data.approvals.filter(
          (approval) =>
            approval.status ===
            "approved",
        ).length;

      const rejected =
        data.approvals.filter(
          (approval) =>
            approval.status ===
            "rejected",
        ).length;

      const reviewed =
        approved + rejected;

      const approvalRate =
        reviewed === 0
          ? null
          : (approved /
              reviewed) *
            100;

      const governedExecutions =
        data.audit.filter(
          (event) =>
            event.action
              .toLowerCase()
              .includes(
                "execut",
              ),
        ).length;

      const aiRequests =
        data.audit.filter(
          (event) => {
            const text =
              `${event.action} ${event.resource_type}`
                .toLowerCase();

            return (
              text.includes(
                "conversation",
              ) ||
              text.includes(
                "message",
              ) ||
              text.includes(
                "copilot",
              ) ||
              text.includes(
                "knowledge.search",
              )
            );
          },
        ).length;

      return {
        documents:
          data.documents.length,

        aiRequests,

        openIncidents:
          openIncidents.length,

        criticalIncidents:
          criticalIncidents.length,

        pendingApprovals:
          pendingApprovals.length,

        approvalRate,

        governedExecutions,
      };
    }, [data]);


  const recentActivity =
    useMemo(
      () =>
        data.audit.slice(0, 6),
      [data.audit],
    );


  return (
    <AppShell>
      <div
        style={{
          display: "flex",
          alignItems:
            "flex-start",
          justifyContent:
            "space-between",
          gap: 20,
        }}
      >
        <div>
          <h1 className="page-title">
            Operations Overview
          </h1>

          <p className="page-subtitle">
            Monitor real workspace
            activity, incidents,
            documents, and governed
            agent actions.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: 10,
          }}
        >
          <button
            type="button"
            onClick={() =>
              void loadDashboard()
            }
            disabled={loading}
            style={{
              border:
                "1px solid #d0d5dd",
              background:
                "#ffffff",
              borderRadius: 10,
              padding:
                "10px 14px",
              display: "flex",
              alignItems:
                "center",
              gap: 7,
              color: "#344054",
              fontWeight: 600,
              cursor:
                loading
                  ? "not-allowed"
                  : "pointer",
            }}
          >
            <RefreshCw
              size={15}
            />
            Refresh
          </button>

          <Link
            href="/copilot"
            style={{
              background:
                "#111827",
              color: "#ffffff",
              borderRadius: 10,
              padding:
                "10px 16px",
              fontWeight: 600,
              textDecoration:
                "none",
            }}
          >
            Open AI Copilot
          </Link>
        </div>
      </div>


      {error && (
        <div
          style={{
            marginTop: 18,
            padding:
              "12px 14px",
            borderRadius: 10,
            background:
              "#fffaeb",
            color: "#b54708",
            fontSize: 12,
          }}
        >
          {error}
        </div>
      )}


      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(4, minmax(0, 1fr))",
          gap: 18,
          marginTop: 28,
        }}
      >
        <MetricCard
          title="Indexed Documents"
          value={
            loading
              ? "—"
              : String(
                  metrics.documents,
                )
          }
          detail="Workspace documents"
          icon={FileText}
        />

        <MetricCard
          title="AI Activity"
          value={
            loading
              ? "—"
              : String(
                  metrics.aiRequests,
                )
          }
          detail="From recent audit records"
          icon={Bot}
        />

        <MetricCard
          title="Open Incidents"
          value={
            loading
              ? "—"
              : String(
                  metrics.openIncidents,
                )
          }
          detail={
            loading
              ? "Loading..."
              : `${metrics.criticalIncidents} critical`
          }
          icon={
            TriangleAlert
          }
        />

        <MetricCard
          title="Pending Approvals"
          value={
            loading
              ? "—"
              : String(
                  metrics.pendingApprovals,
                )
          }
          detail="Needs administrator review"
          icon={
            ShieldCheck
          }
        />
      </section>


      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1.7fr) minmax(300px, 1fr)",
          gap: 18,
          marginTop: 18,
        }}
      >
        <article
          className="card"
          style={{
            padding: 22,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems:
                "center",
              justifyContent:
                "space-between",
            }}
          >
            <div>
              <div
                style={{
                  fontWeight: 700,
                }}
              >
                AI Operations
                Activity
              </div>

              <div
                style={{
                  marginTop: 4,
                  color:
                    "#98a2b3",
                  fontSize: 12,
                }}
              >
                Recent persisted
                audit activity
              </div>
            </div>

            <Activity
              size={18}
              color="#667085"
            />
          </div>


          <div
            style={{
              marginTop: 22,
            }}
          >
            {loading ? (
              <EmptyActivity
                message="Loading workspace activity..."
              />
            ) : recentActivity.length ===
              0 ? (
              <EmptyActivity
                message="No audit activity has been recorded yet."
              />
            ) : (
              recentActivity.map(
                (item) => (
                  <div
                    key={item.id}
                    style={{
                      display:
                        "grid",
                      gridTemplateColumns:
                        "180px 1fr 130px",
                      gap: 16,
                      padding:
                        "14px 0",
                      borderTop:
                        "1px solid #f0f1f3",
                      alignItems:
                        "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize:
                          13,
                        fontWeight:
                          600,
                      }}
                    >
                      {formatAction(
                        item.action,
                      )}
                    </div>

                    <div
                      style={{
                        color:
                          "#667085",
                        fontSize:
                          13,
                      }}
                    >
                      {activityDetail(
                        item,
                      )}
                    </div>

                    <div
                      style={{
                        textAlign:
                          "right",
                        color:
                          "#98a2b3",
                        fontSize:
                          12,
                      }}
                    >
                      {formatDate(
                        item.created_at,
                      )}
                    </div>
                  </div>
                ),
              )
            )}
          </div>
        </article>


        <article
          className="card"
          style={{
            padding: 22,
          }}
        >
          <div
            style={{
              fontWeight: 700,
            }}
          >
            Agent Governance
          </div>

          <div
            style={{
              marginTop: 4,
              color: "#98a2b3",
              fontSize: 12,
            }}
          >
            Human-in-the-loop
            controls
          </div>


          <GovernanceMetric
            label="Approval rate"
            value={
              loading
                ? "—"
                : metrics.approvalRate ===
                    null
                  ? "N/A"
                  : `${metrics.approvalRate.toFixed(
                      1,
                    )}%`
            }
          />

          <GovernanceMetric
            label="Governed executions"
            value={
              loading
                ? "—"
                : String(
                    metrics.governedExecutions,
                  )
            }
          />

          <div
            style={{
              marginTop: 14,
              color: "#98a2b3",
              fontSize: 11,
              lineHeight: 1.5,
            }}
          >
            Governance metrics are
            calculated from the
            approval records and
            recent audit events
            currently available to
            this workspace.
          </div>
        </article>
      </section>
    </AppShell>
  );
}


function MetricCard({
  title,
  value,
  detail,
  icon: Icon,
}: {
  title: string;
  value: string;
  detail: string;
  icon: React.ComponentType<{
    size?: number;
    color?: string;
  }>;
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
          width: 38,
          height: 38,
          borderRadius: 10,
          background:
            "#f1f3f7",
          display: "grid",
          placeItems:
            "center",
        }}
      >
        <Icon
          size={18}
          color="#344054"
        />
      </div>

      <div
        style={{
          marginTop: 20,
          fontSize: 13,
          color: "#667085",
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 6,
          fontSize: 30,
          fontWeight: 700,
        }}
      >
        {value}
      </div>

      <div
        style={{
          marginTop: 6,
          fontSize: 12,
          color: "#98a2b3",
        }}
      >
        {detail}
      </div>
    </article>
  );
}


function GovernanceMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div
      style={{
        marginTop: 18,
        padding: 16,
        borderRadius: 12,
        background:
          "#f8fafc",
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
          marginTop: 6,
          fontSize: 26,
          fontWeight: 700,
        }}
      >
        {value}
      </div>
    </div>
  );
}


function EmptyActivity({
  message,
}: {
  message: string;
}) {
  return (
    <div
      style={{
        padding:
          "36px 10px",
        textAlign:
          "center",
        color: "#98a2b3",
        fontSize: 12,
      }}
    >
      {message}
    </div>
  );
}


function formatAction(
  action: string,
): string {
  return action
    .replaceAll("_", " ")
    .replaceAll(".", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}


function activityDetail(
  event: AuditLog,
): string {
  const details =
    event.details ?? {};

  const preferredKeys = [
    "filename",
    "tool_name",
    "title",
    "status",
  ];

  for (
    const key of preferredKeys
  ) {
    const value =
      details[key];

    if (
      typeof value ===
        "string" &&
      value.length > 0
    ) {
      return value;
    }
  }

  if (event.resource_id) {
    return `${formatAction(
      event.resource_type,
    )} ${event.resource_id.slice(
      0,
      8,
    )}`;
  }

  return formatAction(
    event.resource_type,
  );
}


function formatDate(
  value: string,
): string {
  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return date.toLocaleString(
    undefined,
    {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    },
  );
}
