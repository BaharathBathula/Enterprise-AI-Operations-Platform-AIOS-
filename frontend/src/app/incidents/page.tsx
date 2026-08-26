"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Plus,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import {
  getSession,
} from "@/lib/session";


type IncidentSeverity =
  | "low"
  | "medium"
  | "high"
  | "critical";

type IncidentStatus =
  | "open"
  | "investigating"
  | "resolved";


type Incident = {
  id: string;
  organization_id: string;
  created_by_user_id: string;
  title: string;
  description: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  source: string;
  created_at: string;
  updated_at: string;
};


type CreateIncidentPayload = {
  title: string;
  description: string;
  severity: IncidentSeverity;
  source: string;
};


export default function IncidentsPage() {
  const [incidents, setIncidents] =
    useState<Incident[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [search, setSearch] =
    useState("");

  const [showCreateForm, setShowCreateForm] =
    useState(false);

  const loadIncidents =
    useCallback(async () => {
      const session = getSession();

      if (!session) {
        setError(
          "No active session. Sign in before loading incidents.",
        );
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data =
          await apiRequest<Incident[]>(
            `/organizations/${session.organizationId}/incidents`,
            {
              token: session.accessToken,
            },
          );

        setIncidents(data);
      } catch (requestError) {
        if (
          requestError instanceof ApiError
        ) {
          setError(requestError.detail);
        } else {
          setError(
            "Unable to load incidents.",
          );
        }
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    void loadIncidents();
  }, [loadIncidents]);


  const filteredIncidents =
    useMemo(() => {
      const query =
        search.trim().toLowerCase();

      if (!query) {
        return incidents;
      }

      return incidents.filter(
        (incident) =>
          incident.title
            .toLowerCase()
            .includes(query) ||
          incident.description
            .toLowerCase()
            .includes(query) ||
          incident.source
            .toLowerCase()
            .includes(query) ||
          incident.severity
            .toLowerCase()
            .includes(query) ||
          incident.status
            .toLowerCase()
            .includes(query),
      );
    }, [incidents, search]);


  const metrics =
    useMemo(() => {
      return {
        open: incidents.filter(
          (incident) =>
            incident.status === "open",
        ).length,

        critical: incidents.filter(
          (incident) =>
            incident.severity ===
            "critical",
        ).length,

        investigating: incidents.filter(
          (incident) =>
            incident.status ===
            "investigating",
        ).length,

        resolved: incidents.filter(
          (incident) =>
            incident.status ===
            "resolved",
        ).length,
      };
    }, [incidents]);


  async function updateStatus(
    incident: Incident,
    nextStatus: IncidentStatus,
  ) {
    const session = getSession();

    if (!session) {
      setError(
        "No active session.",
      );
      return;
    }

    setError(null);

    try {
      const updated =
        await apiRequest<Incident>(
          `/organizations/${session.organizationId}/incidents/${incident.id}`,
          {
            method: "PATCH",
            token: session.accessToken,
            body: JSON.stringify({
              status: nextStatus,
            }),
          },
        );

      setIncidents(
        (current) =>
          current.map((item) =>
            item.id === updated.id
              ? updated
              : item,
          ),
      );
    } catch (requestError) {
      if (
        requestError instanceof ApiError
      ) {
        setError(requestError.detail);
      } else {
        setError(
          "Unable to update incident.",
        );
      }
    }
  }


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
            Incidents
          </h1>

          <p className="page-subtitle">
            Track operational incidents
            stored in the AIOS workspace.
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
              void loadIncidents()
            }
            style={secondaryButtonStyle}
          >
            <RefreshCw size={15} />
            Refresh
          </button>

          <button
            type="button"
            onClick={() =>
              setShowCreateForm(true)
            }
            style={primaryButtonStyle}
          >
            <Plus size={15} />
            Create incident
          </button>
        </div>
      </div>


      {error && (
        <div
          style={{
            marginTop: 18,
            padding: "12px 14px",
            borderRadius: 10,
            background: "#fef3f2",
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
          label="Open"
          value={metrics.open}
          detail="Requires attention"
        />

        <MetricCard
          label="Critical"
          value={metrics.critical}
          detail="Highest severity"
        />

        <MetricCard
          label="Investigating"
          value={metrics.investigating}
          detail="Active response"
        />

        <MetricCard
          label="Resolved"
          value={metrics.resolved}
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
            borderBottom:
              "1px solid #e4e7ec",
            display: "flex",
            justifyContent:
              "space-between",
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
              Real incidents persisted
              through the AIOS API
            </div>
          </div>

          <div
            style={{
              width: 300,
              display: "flex",
              alignItems: "center",
              gap: 8,
              border:
                "1px solid #d0d5dd",
              borderRadius: 9,
              padding: "8px 10px",
              color: "#98a2b3",
            }}
          >
            <Search size={15} />

            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Search incidents"
              style={{
                width: "100%",
                border: "none",
                outline: "none",
                fontSize: 12,
                background:
                  "transparent",
              }}
            />
          </div>
        </div>


        {loading ? (
          <EmptyState
            title="Loading incidents..."
            detail={
              "Reading incident data from the AIOS API."
            }
          />
        ) : filteredIncidents.length ===
          0 ? (
          <EmptyState
            title={
              search
                ? "No matching incidents"
                : "No incidents yet"
            }
            detail={
              search
                ? "Try a different search."
                : "Create the first incident for this workspace."
            }
          />
        ) : (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "110px minmax(300px, 1fr) 110px 140px 130px 140px",
                padding: "11px 18px",
                background: "#f9fafb",
                borderBottom:
                  "1px solid #e4e7ec",
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
            </div>

            {filteredIncidents.map(
              (incident) => (
                <IncidentRow
                  key={incident.id}
                  incident={incident}
                  onStatusChange={
                    updateStatus
                  }
                />
              ),
            )}
          </>
        )}
      </section>


      {showCreateForm && (
        <CreateIncidentModal
          onClose={() =>
            setShowCreateForm(false)
          }
          onCreated={(incident) => {
            setIncidents(
              (current) => [
                incident,
                ...current,
              ],
            );

            setShowCreateForm(false);
          }}
        />
      )}
    </AppShell>
  );
}


function IncidentRow({
  incident,
  onStatusChange,
}: {
  incident: Incident;
  onStatusChange: (
    incident: Incident,
    status: IncidentStatus,
  ) => Promise<void>;
}) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "110px minmax(300px, 1fr) 110px 140px 130px 140px",
        padding: "16px 18px",
        borderBottom:
          "1px solid #f0f1f3",
        alignItems: "center",
        fontSize: 12,
      }}
    >
      <div
        title={incident.id}
        style={{
          fontWeight: 700,
        }}
      >
        {shortIncidentId(
          incident.id,
        )}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          minWidth: 0,
        }}
      >
        <div
          style={{
            width: 34,
            height: 34,
            flexShrink: 0,
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
            minWidth: 0,
          }}
        >
          <div
            style={{
              fontWeight: 600,
            }}
          >
            {incident.title}
          </div>

          <div
            style={{
              marginTop: 3,
              color: "#98a2b3",
              fontSize: 11,
              overflow: "hidden",
              textOverflow:
                "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {incident.description}
          </div>
        </div>
      </div>

      <SeverityBadge
        severity={incident.severity}
      />

      <select
        value={incident.status}
        onChange={(event) =>
          void onStatusChange(
            incident,
            event.target
              .value as IncidentStatus,
          )
        }
        aria-label={
          `Status for ${incident.title}`
        }
        style={{
          width: 125,
          border:
            "1px solid #d0d5dd",
          borderRadius: 8,
          background: "#ffffff",
          padding: "7px 8px",
          fontSize: 11,
        }}
      >
        <option value="open">
          Open
        </option>

        <option value="investigating">
          Investigating
        </option>

        <option value="resolved">
          Resolved
        </option>
      </select>

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
        {formatDate(
          incident.created_at,
        )}
      </div>
    </div>
  );
}


function CreateIncidentModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: (
    incident: Incident,
  ) => void;
}) {
  const [title, setTitle] =
    useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [severity, setSeverity] =
    useState<IncidentSeverity>(
      "medium",
    );

  const [source, setSource] =
    useState("manual");

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const session = getSession();

    if (!session) {
      setError(
        "No active session.",
      );
      return;
    }

    setSubmitting(true);
    setError(null);

    const payload:
      CreateIncidentPayload = {
        title: title.trim(),
        description:
          description.trim(),
        severity,
        source: source.trim(),
      };

    try {
      const incident =
        await apiRequest<Incident>(
          `/organizations/${session.organizationId}/incidents`,
          {
            method: "POST",
            token: session.accessToken,
            body:
              JSON.stringify(
                payload,
              ),
          },
        );

      onCreated(incident);
    } catch (requestError) {
      if (
        requestError instanceof ApiError
      ) {
        setError(requestError.detail);
      } else {
        setError(
          "Unable to create incident.",
        );
      }
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <div
      role="presentation"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        background:
          "rgba(16, 24, 40, 0.45)",
        display: "grid",
        placeItems: "center",
        padding: 24,
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={
          "create-incident-title"
        }
        style={{
          width: "100%",
          maxWidth: 560,
          borderRadius: 16,
          background: "#ffffff",
          boxShadow:
            "0 24px 48px rgba(16,24,40,0.18)",
          padding: 24,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent:
              "space-between",
            alignItems: "center",
            gap: 16,
          }}
        >
          <div>
            <h2
              id="create-incident-title"
              style={{
                margin: 0,
                fontSize: 20,
              }}
            >
              Create incident
            </h2>

            <p
              style={{
                margin:
                  "6px 0 0",
                color: "#667085",
                fontSize: 12,
              }}
            >
              Persist a new operational
              incident in AIOS.
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            style={{
              border: "none",
              background:
                "transparent",
              cursor: "pointer",
              color: "#667085",
            }}
          >
            <X size={20} />
          </button>
        </div>


        <form
          onSubmit={handleSubmit}
          style={{
            display: "grid",
            gap: 16,
            marginTop: 22,
          }}
        >
          <FormField label="Title">
            <input
              required
              minLength={3}
              maxLength={255}
              value={title}
              onChange={(event) =>
                setTitle(
                  event.target.value,
                )
              }
              style={inputStyle}
              placeholder="Checkout API unavailable"
            />
          </FormField>


          <FormField label="Description">
            <textarea
              required
              minLength={3}
              value={description}
              onChange={(event) =>
                setDescription(
                  event.target.value,
                )
              }
              style={{
                ...inputStyle,
                minHeight: 110,
                resize: "vertical",
              }}
              placeholder="Describe the operational impact..."
            />
          </FormField>


          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "1fr 1fr",
              gap: 14,
            }}
          >
            <FormField label="Severity">
              <select
                value={severity}
                onChange={(event) =>
                  setSeverity(
                    event.target
                      .value as IncidentSeverity,
                  )
                }
                style={inputStyle}
              >
                <option value="low">
                  Low
                </option>

                <option value="medium">
                  Medium
                </option>

                <option value="high">
                  High
                </option>

                <option value="critical">
                  Critical
                </option>
              </select>
            </FormField>


            <FormField label="Source">
              <input
                required
                value={source}
                onChange={(event) =>
                  setSource(
                    event.target.value,
                  )
                }
                style={inputStyle}
                placeholder="manual"
              />
            </FormField>
          </div>


          {error && (
            <div
              style={{
                padding:
                  "10px 12px",
                borderRadius: 9,
                background:
                  "#fef3f2",
                color: "#b42318",
                fontSize: 12,
              }}
            >
              {error}
            </div>
          )}


          <div
            style={{
              display: "flex",
              justifyContent:
                "flex-end",
              gap: 10,
              marginTop: 4,
            }}
          >
            <button
              type="button"
              onClick={onClose}
              style={
                secondaryButtonStyle
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={submitting}
              style={{
                ...primaryButtonStyle,
                opacity:
                  submitting
                    ? 0.6
                    : 1,
                cursor:
                  submitting
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              {submitting
                ? "Creating..."
                : "Create incident"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}


function FormField({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label
      style={{
        display: "grid",
        gap: 6,
        color: "#344054",
        fontSize: 12,
        fontWeight: 600,
      }}
    >
      {label}
      {children}
    </label>
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
        padding: "52px 20px",
        textAlign: "center",
      }}
    >
      <AlertTriangle
        size={26}
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


function SeverityBadge({
  severity,
}: {
  severity: IncidentSeverity;
}) {
  let background = "#f2f4f7";
  let color = "#344054";

  if (severity === "medium") {
    background = "#fffaeb";
    color = "#b54708";
  }

  if (severity === "high") {
    background = "#fff6ed";
    color = "#c4320a";
  }

  if (severity === "critical") {
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
        textTransform:
          "capitalize",
      }}
    >
      {severity}
    </span>
  );
}


function shortIncidentId(
  id: string,
): string {
  return `INC-${id
    .replaceAll("-", "")
    .slice(0, 6)
    .toUpperCase()}`;
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


const inputStyle:
  React.CSSProperties = {
    width: "100%",
    boxSizing: "border-box",
    border:
      "1px solid #d0d5dd",
    borderRadius: 9,
    padding: "10px 11px",
    background: "#ffffff",
    color: "#101828",
    outline: "none",
    fontSize: 12,
  };


const primaryButtonStyle:
  React.CSSProperties = {
    border: "none",
    borderRadius: 10,
    background: "#111827",
    color: "#ffffff",
    padding: "10px 15px",
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: 7,
  };


const secondaryButtonStyle:
  React.CSSProperties = {
    border:
      "1px solid #d0d5dd",
    borderRadius: 10,
    background: "#ffffff",
    color: "#344054",
    padding: "10px 14px",
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: 7,
  };
