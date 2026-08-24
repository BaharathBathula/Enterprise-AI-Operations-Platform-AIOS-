import {
  Activity,
  ArrowUpRight,
  Bot,
  FileText,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";

import { Sidebar } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";

const stats = [
  {
    title: "Indexed Documents",
    value: "1,248",
    detail: "+42 this week",
    icon: FileText,
  },
  {
    title: "AI Requests",
    value: "8,462",
    detail: "+18.4% this month",
    icon: Bot,
  },
  {
    title: "Open Incidents",
    value: "12",
    detail: "3 critical",
    icon: TriangleAlert,
  },
  {
    title: "Pending Approvals",
    value: "7",
    detail: "Needs review",
    icon: ShieldCheck,
  },
];

const activity = [
  {
    action: "Document indexed",
    detail: "production-runbook.pdf",
    time: "2 min ago",
  },
  {
    action: "AI knowledge query",
    detail: "Checkout API cancellation procedure",
    time: "8 min ago",
  },
  {
    action: "Incident approval requested",
    detail: "Critical checkout API outage",
    time: "15 min ago",
  },
  {
    action: "Tool execution approved",
    detail: "create_incident",
    time: "24 min ago",
  },
];

export default function Home() {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="main-area">
        <Topbar />

        <main className="page-content">
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              gap: 20,
            }}
          >
            <div>
              <h1 className="page-title">
                Operations Overview
              </h1>

              <p className="page-subtitle">
                Monitor enterprise AI activity,
                operational incidents, and governed
                agent actions.
              </p>
            </div>

            <button
              type="button"
              style={{
                background: "#111827",
                color: "#ffffff",
                border: "none",
                borderRadius: 10,
                padding: "10px 16px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Open AI Copilot
            </button>
          </div>

          <section
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(4, minmax(0, 1fr))",
              gap: 18,
              marginTop: 28,
            }}
          >
            {stats.map((stat) => {
              const Icon = stat.icon;

              return (
                <article
                  key={stat.title}
                  className="card"
                  style={{
                    padding: 20,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent:
                        "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div
                      style={{
                        width: 38,
                        height: 38,
                        borderRadius: 10,
                        background: "#f1f3f7",
                        display: "grid",
                        placeItems: "center",
                      }}
                    >
                      <Icon
                        size={18}
                        color="#344054"
                      />
                    </div>

                    <ArrowUpRight
                      size={17}
                      color="#98a2b3"
                    />
                  </div>

                  <div
                    style={{
                      marginTop: 20,
                      fontSize: 13,
                      color: "#667085",
                    }}
                  >
                    {stat.title}
                  </div>

                  <div
                    style={{
                      marginTop: 6,
                      fontSize: 30,
                      fontWeight: 700,
                    }}
                  >
                    {stat.value}
                  </div>

                  <div
                    style={{
                      marginTop: 6,
                      fontSize: 12,
                      color: "#98a2b3",
                    }}
                  >
                    {stat.detail}
                  </div>
                </article>
              );
            })}
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
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div>
                  <div
                    style={{
                      fontWeight: 700,
                    }}
                  >
                    AI Operations Activity
                  </div>

                  <div
                    style={{
                      marginTop: 4,
                      color: "#98a2b3",
                      fontSize: 12,
                    }}
                  >
                    Recent governed actions and
                    knowledge activity
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
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {activity.map((item) => (
                  <div
                    key={`${item.action}-${item.time}`}
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "180px 1fr 90px",
                      gap: 16,
                      padding: "14px 0",
                      borderTop:
                        "1px solid #f0f1f3",
                      alignItems: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: 600,
                      }}
                    >
                      {item.action}
                    </div>

                    <div
                      style={{
                        color: "#667085",
                        fontSize: 13,
                      }}
                    >
                      {item.detail}
                    </div>

                    <div
                      style={{
                        textAlign: "right",
                        color: "#98a2b3",
                        fontSize: 12,
                      }}
                    >
                      {item.time}
                    </div>
                  </div>
                ))}
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
                Human-in-the-loop controls
              </div>

              <div
                style={{
                  marginTop: 24,
                  padding: 16,
                  borderRadius: 12,
                  background: "#f8fafc",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: 12,
                  }}
                >
                  Approval rate
                </div>

                <div
                  style={{
                    marginTop: 6,
                    fontSize: 26,
                    fontWeight: 700,
                  }}
                >
                  91.2%
                </div>
              </div>

              <div
                style={{
                  marginTop: 12,
                  padding: 16,
                  borderRadius: 12,
                  background: "#f8fafc",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: 12,
                  }}
                >
                  Governed executions
                </div>

                <div
                  style={{
                    marginTop: 6,
                    fontSize: 26,
                    fontWeight: 700,
                  }}
                >
                  326
                </div>
              </div>
            </article>
          </section>
        </main>
      </div>
    </div>
  );
}
