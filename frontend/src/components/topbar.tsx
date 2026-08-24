"use client";

import {
  Bell,
  ChevronDown,
  LogOut,
  Search,
} from "lucide-react";
import {
  useRouter,
} from "next/navigation";

import {
  clearSession,
} from "@/lib/session";


export function Topbar() {
  const router = useRouter();

  function handleLogout() {
    clearSession();

    router.replace(
      "/login",
    );
  }

  return (
    <header
      style={{
        height: 68,
        background: "#ffffff",
        borderBottom:
          "1px solid #e4e7ec",
        display: "flex",
        alignItems: "center",
        justifyContent:
          "space-between",
        padding: "0 28px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          minWidth: 320,
          border:
            "1px solid #e4e7ec",
          borderRadius: 10,
          padding: "9px 12px",
          color: "#98a2b3",
        }}
      >
        <Search size={17} />

        <span
          style={{
            fontSize: 13,
          }}
        >
          Search AIOS
        </span>
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 18,
        }}
      >
        <Bell
          size={19}
          color="#667085"
        />

        <div
          style={{
            width: 1,
            height: 24,
            background: "#e4e7ec",
          }}
        />

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
              borderRadius: "50%",
              background: "#eef2f6",
              display: "grid",
              placeItems: "center",
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            BB
          </div>

          <div>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
              }}
            >
              Workspace Admin
            </div>

            <div
              style={{
                fontSize: 11,
                color: "#98a2b3",
              }}
            >
              Administrator
            </div>
          </div>

          <ChevronDown
            size={16}
            color="#98a2b3"
          />

          <button
            type="button"
            onClick={handleLogout}
            title="Sign out"
            aria-label="Sign out"
            style={{
              width: 34,
              height: 34,
              border:
                "1px solid #d0d5dd",
              borderRadius: 9,
              background: "#ffffff",
              color: "#667085",
              display: "grid",
              placeItems: "center",
              cursor: "pointer",
            }}
          >
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </header>
  );
}
