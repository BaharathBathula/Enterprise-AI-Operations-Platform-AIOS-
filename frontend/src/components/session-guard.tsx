"use client";

import {
  useEffect,
  useState,
} from "react";
import {
  useRouter,
} from "next/navigation";
import {
  Loader2,
} from "lucide-react";

import {
  getSession,
} from "@/lib/session";


export function SessionGuard({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  const [ready, setReady] =
    useState(false);

  useEffect(() => {
    const session =
      getSession();

    if (!session) {
      router.replace(
        "/login",
      );

      return;
    }

    setReady(true);
  }, [router]);

  if (!ready) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "grid",
          placeItems: "center",
          background: "#f7f8fb",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            color: "#667085",
            fontSize: 12,
          }}
        >
          <Loader2
            size={16}
            className="spin"
          />

          Loading AIOS...
        </div>
      </div>
    );
  }

  return children;
}
