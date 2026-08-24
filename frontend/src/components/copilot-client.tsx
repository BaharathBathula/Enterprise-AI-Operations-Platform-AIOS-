"use client";

import {
  Bot,
  Loader2,
  Send,
  ShieldCheck,
  Sparkles,
  User,
} from "lucide-react";
import {
  FormEvent,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import {
  clearSession,
  getSession,
  type SessionData,
} from "@/lib/session";
import type {
  AgentResponse,
} from "@/lib/types";


type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  approvalId?: string;
  toolName?: string;
};


function createMessageId(): string {
  return `${Date.now()}-${Math.random()}`;
}


export function CopilotClient() {
  const router = useRouter();

  const [session, setSession] =
    useState<SessionData | null>(null);

  const [sessionReady, setSessionReady] =
    useState(false);

  const [input, setInput] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [messages, setMessages] =
    useState<ChatMessage[]>([
      {
        id: "welcome",
        role: "assistant",
        content:
          "Ask me about enterprise knowledge or request a governed operational action.",
      },
    ]);


  useEffect(() => {
    const currentSession =
      getSession();

    if (!currentSession) {
      router.replace("/login");
      return;
    }

    setSession(currentSession);
    setSessionReady(true);
  }, [router]);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const message =
      input.trim();

    if (
      !message ||
      loading ||
      !session
    ) {
      return;
    }

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content: message,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      const response =
        await apiRequest<AgentResponse>(
          `/organizations/${session.organizationId}/agent`,
          {
            method: "POST",
            token:
              session.accessToken,
            body: JSON.stringify({
              message,
            }),
          },
        );

      const approvalId =
        typeof response.data
          .approval_id === "string"
          ? response.data
              .approval_id
          : undefined;

      const toolName =
        typeof response.data
          .tool_name === "string"
          ? response.data
              .tool_name
          : undefined;

      let content =
        response.message ??
        "AIOS completed the request.";

      if (
        response.error ===
        "approval_required"
      ) {
        content =
          response.message ??
          "This action requires human approval.";
      } else if (
        !response.success
      ) {
        content =
          response.error ??
          "AIOS could not complete the request.";
      } else if (
        typeof response.data
          .answer === "string"
      ) {
        content =
          response.data.answer;
      } else if (
        typeof response.data
          .message === "string"
      ) {
        content =
          response.data.message;
      }

      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          content,
          approvalId,
          toolName,
        },
      ]);
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 401
      ) {
        clearSession();

        router.replace(
          "/login",
        );

        return;
      }

      let errorMessage =
        "Unable to reach the AIOS backend.";

      if (
        error instanceof ApiError
      ) {
        errorMessage =
          `Request failed (${error.status}): ` +
          error.detail;
      }

      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          content:
            errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }


  if (!sessionReady) {
    return (
      <section
        className="card"
        style={{
          minHeight:
            "calc(100vh - 132px)",
          display: "grid",
          placeItems: "center",
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

          Loading AIOS session...
        </div>
      </section>
    );
  }


  return (
    <section
      className="card"
      style={{
        display: "flex",
        flexDirection: "column",
        minHeight:
          "calc(100vh - 132px)",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          padding: "20px 22px",
          borderBottom:
            "1px solid #e4e7ec",
          display: "flex",
          alignItems: "center",
          justifyContent:
            "space-between",
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
            Authenticated enterprise
            agent interface
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 7,
            padding: "7px 10px",
            borderRadius: 999,
            background: "#ecfdf3",
            color: "#067647",
            fontSize: 11,
            fontWeight: 700,
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
          overflowY: "auto",
        }}
      >
        {messages.map(
          (message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ),
        )}

        {loading && (
          <div
            style={{
              display: "flex",
              gap: 10,
              alignItems:
                "center",
              color: "#667085",
              fontSize: 12,
            }}
          >
            <Loader2
              size={16}
              className="spin"
            />

            AIOS is processing...
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        style={{
          borderTop:
            "1px solid #e4e7ec",
          padding: 16,
          background: "#ffffff",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            gap: 10,
            border:
              "1px solid #d0d5dd",
            borderRadius: 12,
            padding: 10,
          }}
        >
          <textarea
            value={input}
            onChange={(event) =>
              setInput(
                event.target.value,
              )
            }
            placeholder="Ask AIOS or request an operational action..."
            rows={2}
            disabled={loading}
            style={{
              flex: 1,
              border: "none",
              outline: "none",
              resize: "none",
              fontSize: 13,
              lineHeight: 1.5,
              background:
                "transparent",
            }}
          />

          <button
            type="submit"
            disabled={
              loading ||
              input.trim()
                .length === 0
            }
            aria-label="Send message"
            style={{
              width: 38,
              height: 38,
              borderRadius: 10,
              border: "none",
              background:
                "#111827",
              color: "#ffffff",
              display: "grid",
              placeItems: "center",
              cursor: loading
                ? "not-allowed"
                : "pointer",
              opacity:
                loading ||
                input.trim()
                  .length === 0
                  ? 0.5
                  : 1,
            }}
          >
            <Send size={16} />
          </button>
        </div>
      </form>
    </section>
  );
}


function MessageBubble({
  message,
}: {
  message: ChatMessage;
}) {
  const isUser =
    message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser
          ? "flex-end"
          : "flex-start",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: isUser
            ? "row-reverse"
            : "row",
          gap: 10,
          maxWidth: "78%",
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            flexShrink: 0,
            borderRadius: 9,
            background: isUser
              ? "#eef2f6"
              : "#111827",
            color: isUser
              ? "#475467"
              : "#ffffff",
            display: "grid",
            placeItems: "center",
          }}
        >
          {isUser ? (
            <User size={15} />
          ) : (
            <Bot size={15} />
          )}
        </div>

        <div>
          <div
            style={{
              borderRadius: 14,
              padding: "13px 15px",
              background: isUser
                ? "#111827"
                : "#ffffff",
              color: isUser
                ? "#ffffff"
                : "#111827",
              border: isUser
                ? "none"
                : "1px solid #e4e7ec",
              fontSize: 13,
              lineHeight: 1.6,
              whiteSpace: "pre-wrap",
            }}
          >
            {message.content}
          </div>

          {message.approvalId && (
            <div
              style={{
                marginTop: 8,
                padding: 12,
                borderRadius: 10,
                background: "#fffaeb",
                border:
                  "1px solid #fedf89",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems:
                    "center",
                  gap: 6,
                  fontSize: 11,
                  fontWeight: 700,
                  color: "#b54708",
                }}
              >
                <Sparkles
                  size={13}
                />

                Human approval required
              </div>

              <div
                style={{
                  marginTop: 5,
                  color: "#667085",
                  fontSize: 11,
                }}
              >
                Tool:{" "}
                {message.toolName ??
                  "governed action"}
              </div>

              <div
                style={{
                  marginTop: 3,
                  color: "#98a2b3",
                  fontSize: 10,
                }}
              >
                Approval ID:{" "}
                {message.approvalId}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
