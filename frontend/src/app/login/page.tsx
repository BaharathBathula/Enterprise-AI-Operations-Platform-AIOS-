"use client";

import {
  FormEvent,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import {
  saveSession,
} from "@/lib/session";
import type {
  OrganizationMembership,
  TokenResponse,
} from "@/lib/types";


export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError(null);

    try {
      const body =
        new URLSearchParams();

      body.set(
        "username",
        email.trim(),
      );

      body.set(
        "password",
        password,
      );

      const token =
        await apiRequest<TokenResponse>(
          "/auth/login",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/x-www-form-urlencoded",
            },
            body: body.toString(),
          },
        );

      const organizations =
        await apiRequest<
          OrganizationMembership[]
        >(
          "/organizations",
          {
            token:
              token.access_token,
          },
        );

      if (
        organizations.length === 0
      ) {
        setError(
          "Your account does not belong to an organization.",
        );

        return;
      }

      saveSession({
        accessToken:
          token.access_token,
        organizationId:
          organizations[0]
            .organization.id,
      });

      router.push("/");
    } catch (error) {
      if (
        error instanceof ApiError
      ) {
        setError(
          error.detail,
        );
      } else {
        setError(
          "Unable to sign in.",
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        background: "#f7f8fb",
        padding: 24,
      }}
    >
      <section
        style={{
          width: "100%",
          maxWidth: 420,
          background: "#ffffff",
          border:
            "1px solid #e4e7ec",
          borderRadius: 16,
          padding: 30,
          boxShadow:
            "0 8px 24px rgba(16,24,40,0.06)",
        }}
      >
        <div
          style={{
            width: 42,
            height: 42,
            borderRadius: 12,
            background: "#111827",
            color: "#ffffff",
            display: "grid",
            placeItems: "center",
            fontWeight: 800,
          }}
        >
          A
        </div>

        <h1
          style={{
            margin:
              "20px 0 0",
            fontSize: 24,
          }}
        >
          Sign in to AIOS
        </h1>

        <p
          style={{
            marginTop: 8,
            color: "#667085",
            fontSize: 13,
          }}
        >
          Access your enterprise AI
          operations workspace.
        </p>

        <form
          onSubmit={handleSubmit}
          style={{
            marginTop: 24,
            display: "flex",
            flexDirection:
              "column",
            gap: 16,
          }}
        >
          <label
            style={{
              display: "flex",
              flexDirection:
                "column",
              gap: 6,
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            Email

            <input
              type="email"
              required
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value,
                )
              }
              style={{
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                padding:
                  "10px 11px",
                outline: "none",
              }}
            />
          </label>

          <label
            style={{
              display: "flex",
              flexDirection:
                "column",
              gap: 6,
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            Password

            <input
              type="password"
              required
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
              style={{
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                padding:
                  "10px 11px",
                outline: "none",
              }}
            />
          </label>

          {error && (
            <div
              style={{
                borderRadius: 9,
                background:
                  "#fef3f2",
                color:
                  "#b42318",
                padding:
                  "10px 12px",
                fontSize: 12,
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              border: "none",
              borderRadius: 10,
              background:
                "#111827",
              color: "#ffffff",
              padding:
                "11px 14px",
              fontWeight: 700,
              cursor:
                loading
                  ? "not-allowed"
                  : "pointer",
              opacity:
                loading
                  ? 0.6
                  : 1,
            }}
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
