import {
  FileText,
  ShieldCheck,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { CopilotClient } from "@/components/copilot-client";


export default function CopilotPage() {
  return (
    <AppShell>
      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1fr) 300px",
          gap: 18,
        }}
      >
        <CopilotClient />

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
              Agent Capabilities
            </div>

            <Capability
              icon={<FileText size={16} />}
              title="Enterprise Knowledge"
              description={
                "Search indexed organizational documents."
              }
            />

            <Capability
              icon={
                <ShieldCheck size={16} />
              }
              title="Governed Actions"
              description={
                "Write actions require persisted human approval."
              }
            />
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
              Registered Tools
            </div>

            <Tool
              name="knowledge_search"
              mode="Automatic"
            />

            <Tool
              name="create_incident"
              mode="Approval"
            />
          </section>
        </aside>
      </div>
    </AppShell>
  );
}


function Capability({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        gap: 10,
        marginTop: 16,
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          flexShrink: 0,
          borderRadius: 8,
          background: "#f1f3f7",
          display: "grid",
          placeItems: "center",
          color: "#475467",
        }}
      >
        {icon}
      </div>

      <div>
        <div
          style={{
            fontSize: 12,
            fontWeight: 700,
          }}
        >
          {title}
        </div>

        <div
          style={{
            marginTop: 4,
            color: "#98a2b3",
            fontSize: 10,
            lineHeight: 1.5,
          }}
        >
          {description}
        </div>
      </div>
    </div>
  );
}


function Tool({
  name,
  mode,
}: {
  name: string;
  mode: string;
}) {
  const automatic =
    mode === "Automatic";

  return (
    <div
      style={{
        marginTop: 12,
        border: "1px solid #e4e7ec",
        borderRadius: 9,
        padding: 10,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 8,
      }}
    >
      <code
        style={{
          fontSize: 10,
        }}
      >
        {name}
      </code>

      <span
        style={{
          borderRadius: 999,
          padding: "4px 7px",
          background: automatic
            ? "#ecfdf3"
            : "#fffaeb",
          color: automatic
            ? "#067647"
            : "#b54708",
          fontSize: 9,
          fontWeight: 700,
        }}
      >
        {mode}
      </span>
    </div>
  );
}
