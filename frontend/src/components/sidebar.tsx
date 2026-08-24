import {
  Activity,
  Bot,
  FileText,
  Gauge,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";

const navigation = [
  {
    label: "Overview",
    icon: Gauge,
  },
  {
    label: "Copilot",
    icon: Bot,
  },
  {
    label: "Documents",
    icon: FileText,
  },
  {
    label: "Incidents",
    icon: TriangleAlert,
  },
  {
    label: "Approvals",
    icon: ShieldCheck,
  },
  {
    label: "Audit Activity",
    icon: Activity,
  },
];

export function Sidebar() {
  return (
    <aside
      style={{
        width: 252,
        background: "#ffffff",
        borderRight: "1px solid #e4e7ec",
        padding: "20px 16px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "4px 8px 24px",
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
            fontWeight: 700,
          }}
        >
          A
        </div>

        <div>
          <div
            style={{
              fontSize: 16,
              fontWeight: 700,
            }}
          >
            AIOS
          </div>

          <div
            style={{
              color: "#98a2b3",
              fontSize: 12,
            }}
          >
            Enterprise AI
          </div>
        </div>
      </div>

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 6,
        }}
      >
        {navigation.map((item, index) => {
          const Icon = item.icon;
          const active = index === 0;

          return (
            <button
              key={item.label}
              type="button"
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                gap: 10,
                border: "none",
                borderRadius: 10,
                padding: "10px 12px",
                cursor: "pointer",
                background: active
                  ? "#f1f3f7"
                  : "transparent",
                color: active
                  ? "#111827"
                  : "#667085",
                fontWeight: active ? 600 : 500,
                textAlign: "left",
              }}
            >
              <Icon size={18} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div
        style={{
          marginTop: "auto",
          borderTop: "1px solid #e4e7ec",
          paddingTop: 16,
        }}
      >
        <div
          style={{
            padding: "10px 12px",
            borderRadius: 10,
            background: "#f8fafc",
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            Enterprise Workspace
          </div>

          <div
            style={{
              marginTop: 4,
              fontSize: 12,
              color: "#98a2b3",
            }}
          >
            Production
          </div>
        </div>
      </div>
    </aside>
  );
}
