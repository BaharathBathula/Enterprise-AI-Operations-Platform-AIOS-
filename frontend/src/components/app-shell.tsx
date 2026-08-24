import type {
  ReactNode,
} from "react";

import {
  SessionGuard,
} from "@/components/session-guard";
import {
  Sidebar,
} from "@/components/sidebar";
import {
  Topbar,
} from "@/components/topbar";


type AppShellProps = {
  children: ReactNode;
};


export function AppShell({
  children,
}: AppShellProps) {
  return (
    <SessionGuard>
      <div className="app-shell">
        <Sidebar />

        <div className="main-area">
          <Topbar />

          <main className="page-content">
            {children}
          </main>
        </div>
      </div>
    </SessionGuard>
  );
}
