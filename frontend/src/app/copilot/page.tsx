import {
  Bot,
  FileText,
  Send,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";

const sources = [
  {
    file: "production-runbook.pdf",
    page: 12,
    score: "94%",
  },
  {
    file: "incident-response-policy.pdf",
    page: 4,
    score: "89%",
  },
];

export default function CopilotPage() {
  return (
    <AppShell>
      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1fr) 320px",
          gap: 18,
          minHeight: "calc(100vh - 132px)",
        }}
      >
        <section
          className="card"
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "20px 22px",
              borderBottom: "1px solid #e4e7ec",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div>
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                }}
              >
                AIOS Copilot
              </div>

              <div
                style={{
                  marginTop: 4,
                  color: "#98a2b3",
                  fontSize: 12,
                }}
              >
                Enterprise knowledge and governed actions
              </div>
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "7px 10px",
                borderRadius: 999,
                background: "#ecfdf3",
                color: "#067647",
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              <ShieldCheck size={14} />
              Governed
            </div>
          </div>

          <div
            style={{
              flex: 1,
              padding: 24,
              display: "flex",
              flexDirection: "column",
              gap: 18,
              background: "#fbfcfe",
            }}
          >
            <div
              style={{
                display: "flex",
                gap: 12,
                maxWidth: 760,
              }}
            >
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 10,
                  background: "#111827",
                  color: "#ffffff",
                  display: "grid",
                  placeItems: "center",
                  flexShrink: 0,
                }}
              >
                <Bot size={17} />
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #e4e7ec",
                  borderRadius: 14,
                  padding: 16,
                  fontSize: 14,
                  lineHeight: 1.6,
                }}
              >
                Ask me about enterprise documents,
                operational procedures, incidents, or
                request governed actions.
              </div>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
              }}
            >
              <div
                style={{
                  maxWidth: 680,
                  background: "#111827",
                  color: "#ffffff",
                  borderRadius: 14,
                  padding: 16,
                  fontSize: 14,
                  lineHeight: 1.6,
                }}
              >
                What should we do when the checkout API
                starts returning HTTP 503 errors?
              </div>
            </div>

            <div
              style={{
                display: "flex",
                gap: 12,
                maxWidth: 780,
              }}
            >
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 10,
                  background: "#111827",
                  color: "#ffffff",
                  display: "grid",
                  placeItems: "center",
                  flexShrink: 0,
                }}
              >
                <Bot size={17} />
              </div>

              <div
                style={{
                  flex: 1,
                }}
              >
                <div
                  style={{
                    background: "#ffffff",
                    border: "1px solid #e4e7ec",
                    borderRadius: 14,
                    padding: 16,
                    fontSize: 14,
                    lineHeight: 1.65,
                  }}
                >
                  The production runbook recommends
                  verifying upstream service health,
                  checking gateway error rates, and
                  reviewing recent deployments before
                  escalating. If error rates remain
                  elevated, create a critical incident and
                  notify the operations team.
                </div>

                <div
                  style={{
                    marginTop: 10,
                    display: "flex",
                    gap: 8,
                  }}
                >
                  <div
                    style={{
                      padding: "6px 9px",
                      border: "1px solid #e4e7ec",
                      borderRadius: 8,
                      background: "#ffffff",
                      fontSize: 11,
                      color: "#667085",
                    }}
                  >
                    Source 1
                  </div>

                  <div
                    style={{
                      padding: "6px 9px",
                      border: "1px solid #e4e7ec",
                      borderRadius: 8,
                      background: "#ffffff",
                      fontSize: 11,
                      color: "#667085",
                    }}
                  >
                    Source 2
                  </div>
                </div>
              </div>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
              }}
            >
              <div
                style={{
                  maxWidth: 680,
                  background: "#111827",
                  color: "#ffffff",
                  borderRadius: 14,
                  padding: 16,
                  fontSize: 14,
                }}
              >
                Raise a P1 incident for the checkout outage.
              </div>
            </div>

            <div
              style={{
                display: "flex",
                gap: 12,
                maxWidth: 780,
              }}
            >
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 10,
                  background: "#111827",
                  color: "#ffffff",
                  display: "grid",
                  placeItems: "center",
                  flexShrink: 0,
                }}
              >
                <Sparkles size={17} />
              </div>

              <div
                style={{
                  flex: 1,
                  background: "#fffaeb",
                  border: "1px solid #fedf89",
                  borderRadius: 14,
                  padding: 16,
                }}
              >
                <div
                  style={{
                    fontWeight: 700,
                    fontSize: 13,
                  }}
                >
                  Human approval required
                </div>

                <div
                  style={{
                    marginTop: 6,
                    fontSize: 13,
                    color: "#667085",
                    lineHeight: 1.5,
                  }}
                >
                  AIOS wants to execute the
                  <strong> create_incident </strong>
                  tool with critical severity.
                </div>

                <button
                  type="button"
                  style={{
                    marginTop: 12,
                    border: "none",
                    borderRadius: 9,
                    background: "#111827",
                    color: "#ffffff",
                    padding: "8px 12px",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Review approval
                </button>
              </div>
            </div>
          </div>

          <div
            style={{
              borderTop: "1px solid #e4e7ec",
              padding: 16,
              background: "#ffffff",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "flex-end",
                gap: 10,
                border: "1px solid #d0d5dd",
                borderRadius: 12,
                padding: 10,
              }}
            >
              <textarea
                placeholder="Ask AIOS or request an operational action..."
                rows={2}
                style={{
                  flex: 1,
                  border: "none",
                  outline: "none",
                  resize: "none",
                  fontSize: 13,
                  lineHeight: 1.5,
                }}
              />

              <button
                type="button"
                style={{
                  width: 38,
                  height: 38,
                  borderRadius: 10,
                  border: "none",
                  background: "#111827",
                  color: "#ffffff",
                  display: "grid",
                  placeItems: "center",
                  cursor: "pointer",
                }}
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </section>

        <aside
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 18,
          }}
        >
          <section
            className="card"
            style={{
              padding: 18,
            }}
          >
            <div
              style={{
                fontSize: 14,
                fontWeight: 700,
              }}
            >
              Retrieved Sources
            </div>

            <div
              style={{
                marginTop: 14,
                display: "flex",
                flexDirection: "column",
                gap: 10,
              }}
            >
              {sources.map((source) => (
                <div
                  key={`${source.file}-${source.page}`}
                  style={{
                    border: "1px solid #e4e7ec",
                    borderRadius: 10,
                    padding: 12,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      gap: 8,
                    }}
                  >
                    <FileText
                      size={16}
                      color="#667085"
                    />

                    <div>
                      <div
                        style={{
                          fontSize: 12,
                          fontWeight: 600,
                        }}
                      >
                        {source.file}
                      </div>

                      <div
                        style={{
                          marginTop: 4,
                          fontSize: 11,
                          color: "#98a2b3",
                        }}
                      >
                        Page {source.page}
                        {" · "}
                        {source.score} match
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section
            className="card"
            style={{
              padding: 18,
            }}
          >
            <div
              style={{
                fontSize: 14,
                fontWeight: 700,
              }}
            >
              Available Tools
            </div>

            <div
              style={{
                marginTop: 14,
                display: "flex",
                flexDirection: "column",
                gap: 10,
              }}
            >
              <ToolRow
                name="knowledge_search"
                mode="Auto"
              />

              <ToolRow
                name="create_incident"
                mode="Approval"
              />
            </div>
          </section>
        </aside>
      </div>
    </AppShell>
  );
}

function ToolRow({
  name,
  mode,
}: {
  name: string;
  mode: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        border: "1px solid #e4e7ec",
        borderRadius: 10,
        padding: 11,
      }}
    >
      <div
        style={{
          fontSize: 12,
          fontWeight: 600,
        }}
      >
        {name}
      </div>

      <div
        style={{
          fontSize: 10,
          color:
            mode === "Auto"
              ? "#067647"
              : "#b54708",
          background:
            mode === "Auto"
              ? "#ecfdf3"
              : "#fffaeb",
          borderRadius: 999,
          padding: "4px 7px",
          fontWeight: 600,
        }}
      >
        {mode}
      </div>
    </div>
  );
}
