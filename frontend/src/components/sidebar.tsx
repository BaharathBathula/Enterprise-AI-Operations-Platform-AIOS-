import Link from "next/link";
import {
  Activity,
  Bot,
  FileText,
  Gauge,
  ShieldCheck,
  TriangleAlert,
  BookOpen,
} from "lucide-react";

const navigation = [
  {
    label: "Overview",
    href: "/",
    icon: Gauge,
  },
  {
    label: "Copilot",
    href: "/copilot",
    icon: Bot,
  },
  {
    label: "Documents",
    href: "/documents",
    icon: FileText,
  },
  {
  label: "Knowledge",
  href: "/knowledge",
  icon: BookOpen,
  },
  {
    label: "Incidents",
    href: "/incidents",
    icon: TriangleAlert,
  },
  {
    label: "Approvals",
    href: "/approvals",
    icon: ShieldCheck,
  },
  {
    label: "Audit Activity",
    href: "/audit",
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
        {navigation.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                gap: 10,
                borderRadius: 10,
                padding: "10px 12px",
                color: "#667085",
                fontWeight: 500,
              }}
            >
              <Icon size={18} />
              {item.label}
            </Link>
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
