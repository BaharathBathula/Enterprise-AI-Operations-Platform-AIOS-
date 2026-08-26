"use client";

import {
  Activity,
  Bot,
  CheckCircle2,
  FileText,
  RefreshCw,
  Search,
  ShieldCheck,
  TriangleAlert,
  User,
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


type AuditLog = {
  id: string;
  organization_id: string | null;
  user_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: Record<
    string,
    unknown
  > | null;
  created_at: string;
};


type AuditCategory =
  | "all"
  | "tool"
  | "approval"
  | "incident"
  | "document"
  | "organization"
  | "authentication"
  | "other";


export default function AuditPage() {
  const [events, setEvents] =
    useState<AuditLog[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [search, setSearch] =
    useState("");

  const [category, setCategory] =
    useState<AuditCategory>("all");


  const loadAuditLogs =
    useCallback(async () => {
      const session = getSession();

      if (!session) {
        setError(
          "No active session. Sign in before loading audit activity.",
        );
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const logs =
          await apiRequest<
            AuditLog[]
          >(
            `/organizations/${session.organizationId}/audit?limit=250`,
            {
              token:
                session.accessToken,
            },
          );

        setEvents(logs);
      } catch (requestError) {
        if (
          requestError instanceof
          ApiError
        ) {
          if (
            requestError.status ===
            403
          ) {
            setError(
              "Administrator access is required to view organization audit logs.",
            );
          } else {
            setError(
              requestError.detail,
            );
          }
        } else {
          setError(
            "Unable to load audit activity.",
          );
        }
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    void loadAuditLogs();
  }, [loadAuditLogs]);


  const filteredEvents =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();

      return events.filter(
        (event) => {
          const eventCategory =
            getCategory(
              event,
            );

          if (
            category !== "all" &&
            eventCategory !==
              category
          ) {
            return false;
          }

          if (!query) {
            return true;
          }

          const searchable =
            [
              event.action,
              event.resource_type,
              event.resource_id ??
                "",
              event.user_id ?? "",
              JSON.stringify(
                event.details ??
                  {},
              ),
            ]
              .join(" ")
              .toLowerCase();

          return searchable.includes(
            query,
          );
        },
      );
    }, [
      events,
      search,
      category,
    ]);


  const metrics =
    useMemo(() => {
      const toolExecutions =
        events.filter(
          (event) =>
            event.action
              .toLowerCase()
              .includes(
                "execut",
              ) ||
            event.resource_type
              .toLowerCase()
              .includes("tool"),
        ).length;

      const approvals =
        events.filter(
          (event) =>
            getCategory(
              event,
            ) ===
            "approval",
        ).length;

      const prevented =
        events.filter(
          (event) =>
            event.action
              .toLowerCase()
              .includes(
                "reject",
              ) ||
            event.action
              .toLowerCase()
              .includes(
                "denied",
              ) ||
            event.action
              .toLowerCase()
              .includes(
                "blocked",
              ),
        ).length;

      return {
        total: events.length,
        toolExecutions,
        approvals,
        prevented,
      };
    }, [events]);


  return (
    <AppShell>
      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems:
            "flex-start",
          gap: 20,
        }}
      >
        <div>
          <h1 className="page-title">
            Audit Activity
          </h1>

          <p className="page-subtitle">
            Trace enterprise AI
            decisions, approvals,
            operational changes,
            and governed executions.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            alignItems:
              "center",
            gap: 8,
            borderRadius: 999,
            background:
              "#ecfdf3",
            color: "#067647",
            padding:
              "8px 11px",
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          <ShieldCheck
            size={15}
          />
          Audit logging active
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
              "#fef3f2",
            color: "#b42318",
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
          marginTop: 26,
        }}
      >
        <MetricCard
          label="Loaded events"
          value={metrics.total}
          detail="Latest audit records"
        />

        <MetricCard
          label="Tool executions"
          value={
            metrics.toolExecutions
          }
          detail="Governed actions"
        />

        <MetricCard
          label="Approvals"
          value={
            metrics.approvals
          }
          detail="Human decisions"
        />

        <MetricCard
          label="Prevented actions"
          value={
            metrics.prevented
          }
          detail="Rejected or blocked"
        />
      </section>


      <section
        className="card"
        style={{
          marginTop: 18,
          overflow:
            "hidden",
        }}
      >
        <div
          style={{
            padding: 18,
            borderBottom:
              "1px solid #e4e7ec",
            display: "flex",
            justifyContent:
              "space-between",
            alignItems:
              "center",
            gap: 20,
          }}
        >
          <div>
            <div
              style={{
                display:
                  "flex",
                alignItems:
                  "center",
                gap: 8,
                fontSize: 15,
                fontWeight: 700,
              }}
            >
              <Activity
                size={17}
              />
              Event Timeline
            </div>

            <div
              style={{
                marginTop: 4,
                color:
                  "#98a2b3",
                fontSize: 12,
              }}
            >
              Organization-scoped
              operational history
            </div>
          </div>

          <div
            style={{
              display: "flex",
              gap: 10,
              alignItems:
                "center",
            }}
          >
            <div
              style={{
                width: 270,
                display:
                  "flex",
                alignItems:
                  "center",
                gap: 8,
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                padding:
                  "8px 10px",
                color:
                  "#98a2b3",
              }}
            >
              <Search
                size={15}
              />

              <input
                type="text"
                value={search}
                onChange={(
                  event,
                ) =>
                  setSearch(
                    event.target
                      .value,
                  )
                }
                placeholder="Search audit events"
                style={{
                  width:
                    "100%",
                  border:
                    "none",
                  outline:
                    "none",
                  background:
                    "transparent",
                  fontSize: 12,
                }}
              />
            </div>

            <select
              value={category}
              onChange={(
                event,
              ) =>
                setCategory(
                  event.target
                    .value as AuditCategory,
                )
              }
              style={{
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                background:
                  "#ffffff",
                padding:
                  "8px 10px",
                color:
                  "#475467",
                fontSize: 12,
                outline:
                  "none",
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

              <option value="document">
                Document
              </option>

              <option value="organization">
                Organization
              </option>

              <option value="authentication">
                Authentication
              </option>

              <option value="other">
                Other
              </option>
            </select>

            <button
              type="button"
              onClick={() =>
                void loadAuditLogs()
              }
              disabled={loading}
              aria-label="Refresh audit activity"
              style={{
                width: 36,
                height: 36,
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                background:
                  "#ffffff",
                display:
                  "grid",
                placeItems:
                  "center",
                color:
                  "#475467",
                cursor:
                  loading
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              <RefreshCw
                size={15}
              />
            </button>
          </div>
        </div>


        {loading ? (
          <EmptyState
            title="Loading audit activity..."
            detail="Reading organization audit records from the AIOS API."
          />
        ) : filteredEvents
            .length === 0 ? (
          <EmptyState
            title={
              events.length ===
              0
                ? "No audit events yet"
                : "No matching audit events"
            }
            detail={
              events.length ===
              0
                ? "Governed operations will appear here as activity occurs."
                : "Change the search text or event category."
            }
          />
        ) : (
          <>
            <div
              style={{
                display:
                  "grid",
                gridTemplateColumns:
                  "110px 180px minmax(180px, 1fr) 150px 130px 150px",
                padding:
                  "11px 18px",
                background:
                  "#f9fafb",
                borderBottom:
                  "1px solid #e4e7ec",
                color:
                  "#667085",
                fontSize: 11,
                fontWeight: 600,
              }}
            >
              <div>EVENT</div>
              <div>ACTION</div>
              <div>RESOURCE</div>
              <div>ACTOR</div>
              <div>CATEGORY</div>
              <div>TIME</div>
            </div>

            {filteredEvents.map(
              (event) => (
                <AuditRow
                  key={event.id}
                  event={event}
                />
              ),
            )}
          </>
        )}
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
          icon={
            <Bot size={18} />
          }
          title="Agent traceability"
          description="Track governed AI and tool activity through persisted organization audit records."
        />

        <GovernanceCard
          icon={
            <ShieldCheck
              size={18}
            />
          }
          title="Human provenance"
          description="Preserve user identifiers and approval decisions associated with operational actions."
        />

        <GovernanceCard
          icon={
            <FileText
              size={18}
            />
          }
          title="Enterprise evidence"
          description="Maintain historical evidence for investigations, governance, and compliance review."
        />
      </section>
    </AppShell>
  );
}


function AuditRow({
  event,
}: {
  event: AuditLog;
}) {
  const category =
    getCategory(event);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "110px 180px minmax(180px, 1fr) 150px 130px 150px",
        padding:
          "15px 18px",
        borderBottom:
          "1px solid #f0f1f3",
        alignItems:
          "center",
        fontSize: 12,
      }}
    >
      <div
        title={event.id}
        style={{
          fontWeight: 700,
        }}
      >
        {shortAuditId(
          event.id,
        )}
      </div>

      <div>
        <code
          style={{
            background:
              "#f2f4f7",
            borderRadius: 6,
            padding:
              "4px 6px",
            fontSize: 10,
          }}
        >
          {event.action}
        </code>
      </div>

      <div>
        <div
          style={{
            fontWeight: 600,
          }}
        >
          {formatResourceType(
            event.resource_type,
          )}
        </div>

        {event.resource_id && (
          <div
            title={
              event.resource_id
            }
            style={{
              marginTop: 3,
              color:
                "#98a2b3",
              fontSize: 10,
            }}
          >
            {shortValue(
              event.resource_id,
            )}
          </div>
        )}
      </div>

      <div
        title={
          event.user_id ??
          "System"
        }
        style={{
          display: "flex",
          alignItems:
            "center",
          gap: 7,
          color: "#667085",
        }}
      >
        <User size={13} />

        {event.user_id
          ? shortValue(
              event.user_id,
            )
          : "System"}
      </div>

      <CategoryBadge
        category={category}
      />

      <div
        style={{
          color: "#98a2b3",
        }}
      >
        {formatDate(
          event.created_at,
        )}
      </div>
    </div>
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


function CategoryBadge({
  category,
}: {
  category: AuditCategory;
}) {
  let icon =
    <Activity size={12} />;

  if (category === "tool") {
    icon =
      <Bot size={12} />;
  }

  if (
    category ===
    "approval"
  ) {
    icon =
      <ShieldCheck
        size={12}
      />;
  }

  if (
    category ===
    "incident"
  ) {
    icon =
      <TriangleAlert
        size={12}
      />;
  }

  if (
    category ===
    "document"
  ) {
    icon =
      <FileText
        size={12}
      />;
  }

  if (
    category ===
    "authentication"
  ) {
    icon =
      <CheckCircle2
        size={12}
      />;
  }

  return (
    <span
      style={{
        width: "fit-content",
        display: "flex",
        alignItems: "center",
        gap: 5,
        borderRadius: 999,
        background:
          "#f2f4f7",
        color: "#475467",
        padding: "5px 8px",
        fontSize: 10,
        fontWeight: 700,
        textTransform:
          "capitalize",
      }}
    >
      {icon}
      {category}
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
          background:
            "#f1f3f7",
          display: "grid",
          placeItems:
            "center",
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


function EmptyState({
  title,
  detail,
}: {
  title: string;
  detail: string;
}) {
  return (
    <div
      style={{
        padding:
          "54px 20px",
        textAlign:
          "center",
      }}
    >
      <Activity
        size={27}
        color="#98a2b3"
      />

      <div
        style={{
          marginTop: 12,
          fontSize: 14,
          fontWeight: 700,
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 6,
          color: "#98a2b3",
          fontSize: 12,
        }}
      >
        {detail}
      </div>
    </div>
  );
}


function getCategory(
  event: AuditLog,
): AuditCategory {
  const text =
    `${event.action} ${event.resource_type}`
      .toLowerCase();

  if (
    text.includes("approval")
  ) {
    return "approval";
  }

  if (
    text.includes("incident")
  ) {
    return "incident";
  }

  if (
    text.includes("document")
  ) {
    return "document";
  }

  if (
    text.includes("tool")
  ) {
    return "tool";
  }

  if (
    text.includes(
      "organization",
    ) ||
    text.includes(
      "member",
    )
  ) {
    return "organization";
  }

  if (
    text.includes("auth") ||
    text.includes("login") ||
    text.includes("user")
  ) {
    return "authentication";
  }

  return "other";
}


function formatResourceType(
  value: string,
): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}


function shortAuditId(
  value: string,
): string {
  return `AUD-${value
    .replaceAll("-", "")
    .slice(0, 6)
    .toUpperCase()}`;
}


function shortValue(
  value: string,
): string {
  if (value.length <= 12) {
    return value;
  }

  return `${value.slice(
    0,
    8,
  )}...`;
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
