"use client";

import {
  Bot,
  FileText,
  Loader2,
  MessageSquarePlus,
  Send,
  ShieldCheck,
  Sparkles,
  User,
} from "lucide-react";
import {
  FormEvent,
  KeyboardEvent,
  useEffect,
  useRef,
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


type CopilotMode =
  | "knowledge"
  | "agent";


type Source = {
  document_id: string;
  filename: string;
  page_number: number;
  similarity_score: number;
};


type RAGResponse = {
  conversation_id: string;
  answer: string;
  sources: Source[];
};


type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  mode?: CopilotMode;
  sources?: Source[];
  approvalId?: string;
  toolName?: string;
  isError?: boolean;
};


function createMessageId(): string {
  return `${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`;
}


const welcomeMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "I am AIOS Copilot. Use Knowledge mode to ask questions grounded in processed enterprise documents, or Agent mode to request governed operational actions.",
};


export function CopilotClient() {
  const router = useRouter();

  const bottomRef =
    useRef<HTMLDivElement | null>(
      null,
    );

  const [session, setSession] =
    useState<SessionData | null>(
      null,
    );

  const [
    sessionReady,
    setSessionReady,
  ] = useState(false);

  const [mode, setMode] =
    useState<CopilotMode>(
      "knowledge",
    );

  const [
    conversationId,
    setConversationId,
  ] = useState<string | null>(
    null,
  );

  const [input, setInput] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [messages, setMessages] =
    useState<ChatMessage[]>([
      welcomeMessage,
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


  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);


  function startNewConversation() {
    if (loading) {
      return;
    }

    setConversationId(null);
    setMessages([
      welcomeMessage,
    ]);
    setInput("");
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    await sendMessage();
  }


  async function sendMessage() {
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
      mode,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      if (mode === "knowledge") {
        await sendKnowledgeMessage(
          message,
          session,
        );
      } else {
        await sendAgentMessage(
          message,
          session,
        );
      }
    } catch (error) {
      handleRequestError(error);
    } finally {
      setLoading(false);
    }
  }


  async function sendKnowledgeMessage(
    message: string,
    activeSession: SessionData,
  ) {
    const response =
      await apiRequest<RAGResponse>(
        `/organizations/${activeSession.organizationId}/chat`,
        {
          method: "POST",
          token:
            activeSession.accessToken,
          body: JSON.stringify({
            question: message,
            conversation_id:
              conversationId,
            top_k: 5,
          }),
        },
      );

    setConversationId(
      response.conversation_id,
    );

    setMessages((current) => [
      ...current,
      {
        id: createMessageId(),
        role: "assistant",
        mode: "knowledge",
        content:
          response.answer,
        sources:
          response.sources,
      },
    ]);
  }


  async function sendAgentMessage(
    message: string,
    activeSession: SessionData,
  ) {
    const response =
      await apiRequest<AgentResponse>(
        `/organizations/${activeSession.organizationId}/agent`,
        {
          method: "POST",
          token:
            activeSession.accessToken,
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
        mode: "agent",
        content,
        approvalId,
        toolName,
        isError:
          !response.success &&
          response.error !==
            "approval_required",
      },
    ]);
  }


  function handleRequestError(
    error: unknown,
  ) {
    if (
      error instanceof ApiError &&
      error.status === 401
    ) {
      clearSession();
      router.replace("/login");
      return;
    }

    let errorMessage =
      "Unable to reach the AIOS backend.";

    if (
      error instanceof ApiError
    ) {
      errorMessage =
        `Request failed (${error.status}): ${error.detail}`;
    }

    setMessages((current) => [
      ...current,
      {
        id: createMessageId(),
        role: "assistant",
        content: errorMessage,
        isError: true,
      },
    ]);
  }


  function handleKeyDown(
    event:
      KeyboardEvent<HTMLTextAreaElement>,
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (
        input.trim() &&
        !loading
      ) {
        void sendMessage();
      }
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
        maxHeight:
          "calc(100vh - 80px)",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          padding: "18px 20px",
          borderBottom:
            "1px solid #e4e7ec",
          display: "flex",
          alignItems: "center",
          justifyContent:
            "space-between",
          gap: 16,
        }}
      >
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 9,
            }}
          >
            <Bot size={20} />

            <div
              style={{
                fontSize: 18,
                fontWeight: 700,
              }}
            >
              AIOS Copilot
            </div>
          </div>

          <div
            style={{
              marginTop: 5,
              color: "#98a2b3",
              fontSize: 12,
            }}
          >
            Enterprise knowledge and
            governed operational
            actions
          </div>
        </div>


        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 9,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "7px 10px",
              borderRadius: 999,
              background:
                "#ecfdf3",
              color: "#067647",
              fontSize: 11,
              fontWeight: 700,
            }}
          >
            <ShieldCheck
              size={14}
            />

            Governed
          </div>

          <button
            type="button"
            onClick={
              startNewConversation
            }
            disabled={loading}
            style={
              secondaryButtonStyle
            }
          >
            <MessageSquarePlus
              size={14}
            />

            New
          </button>
        </div>
      </div>


      <div
        style={{
          padding: "12px 18px",
          borderBottom:
            "1px solid #e4e7ec",
          background: "#ffffff",
        }}
      >
        <div
          style={{
            display: "inline-flex",
            padding: 4,
            borderRadius: 10,
            background: "#f2f4f7",
            gap: 4,
          }}
        >
          <ModeButton
            active={
              mode === "knowledge"
            }
            onClick={() =>
              setMode("knowledge")
            }
            icon={
              <FileText size={14} />
            }
            label="Knowledge"
          />

          <ModeButton
            active={
              mode === "agent"
            }
            onClick={() =>
              setMode("agent")
            }
            icon={
              <ShieldCheck
                size={14}
              />
            }
            label="Agent Actions"
          />
        </div>


        <div
          style={{
            marginTop: 8,
            color: "#98a2b3",
            fontSize: 10,
          }}
        >
          {mode === "knowledge"
            ? "Knowledge mode uses processed workspace documents and persists the RAG conversation."
            : "Agent mode invokes governed AIOS tools. Write actions may require human approval."}
        </div>
      </div>


      <div
        style={{
          flex: 1,
          padding: 22,
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
              alignItems: "center",
              gap: 9,
              color: "#667085",
              fontSize: 12,
            }}
          >
            <Loader2
              size={16}
              className="spin"
            />

            {mode === "knowledge"
              ? "Searching enterprise knowledge..."
              : "AIOS is evaluating the action..."}
          </div>
        )}


        <div ref={bottomRef} />
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
            onKeyDown={
              handleKeyDown
            }
            placeholder={
              mode === "knowledge"
                ? "Ask a question about your enterprise documents..."
                : "Request a governed operational action..."
            }
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
              width: 40,
              height: 40,
              flexShrink: 0,
              borderRadius: 10,
              border: "none",
              background: "#111827",
              color: "#ffffff",
              display: "grid",
              placeItems: "center",
              cursor:
                loading
                  ? "not-allowed"
                  : "pointer",
              opacity:
                loading ||
                input.trim()
                  .length === 0
                  ? 0.45
                  : 1,
            }}
          >
            {loading ? (
              <Loader2
                size={16}
                className="spin"
              />
            ) : (
              <Send size={16} />
            )}
          </button>
        </div>

        <div
          style={{
            marginTop: 7,
            display: "flex",
            justifyContent:
              "space-between",
            color: "#98a2b3",
            fontSize: 9,
          }}
        >
          <span>
            Enter to send •
            Shift+Enter for new line
          </span>

          {conversationId &&
            mode === "knowledge" && (
              <span>
                Conversation{" "}
                {conversationId.slice(
                  0,
                  8,
                )}
              </span>
            )}
        </div>
      </form>
    </section>
  );
}


function ModeButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        border: "none",
        borderRadius: 8,
        padding: "7px 10px",
        background: active
          ? "#ffffff"
          : "transparent",
        color: active
          ? "#344054"
          : "#667085",
        display: "flex",
        alignItems: "center",
        gap: 6,
        fontSize: 11,
        fontWeight: 600,
        cursor: "pointer",
        boxShadow: active
          ? "0 1px 2px rgba(16,24,40,0.06)"
          : "none",
      }}
    >
      {icon}
      {label}
    </button>
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
          maxWidth: "82%",
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


        <div
          style={{
            minWidth: 0,
          }}
        >
          <div
            style={{
              borderRadius: 14,
              padding: "13px 15px",
              background: isUser
                ? "#111827"
                : message.isError
                  ? "#fef3f2"
                  : "#ffffff",
              color: isUser
                ? "#ffffff"
                : message.isError
                  ? "#b42318"
                  : "#111827",
              border: isUser
                ? "none"
                : message.isError
                  ? "1px solid #fecdca"
                  : "1px solid #e4e7ec",
              fontSize: 13,
              lineHeight: 1.65,
              whiteSpace: "pre-wrap",
            }}
          >
            {message.content}
          </div>


          {message.sources &&
            message.sources.length >
              0 && (
              <Sources
                sources={
                  message.sources
                }
              />
            )}


          {message.approvalId && (
            <ApprovalCard
              approvalId={
                message.approvalId
              }
              toolName={
                message.toolName
              }
            />
          )}


          {message.mode &&
            !isUser && (
              <div
                style={{
                  marginTop: 5,
                  color:
                    "#98a2b3",
                  fontSize: 9,
                  textTransform:
                    "capitalize",
                }}
              >
                {message.mode ===
                "knowledge"
                  ? "Grounded knowledge response"
                  : "Governed agent response"}
              </div>
            )}
        </div>
      </div>
    </div>
  );
}


function Sources({
  sources,
}: {
  sources: Source[];
}) {
  return (
    <div
      style={{
        marginTop: 8,
        border:
          "1px solid #e4e7ec",
        borderRadius: 10,
        background: "#ffffff",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          padding: "8px 10px",
          borderBottom:
            "1px solid #f0f1f3",
          display: "flex",
          alignItems: "center",
          gap: 6,
          color: "#475467",
          fontSize: 10,
          fontWeight: 700,
        }}
      >
        <FileText size={12} />

        Sources
      </div>

      {sources.map(
        (source, index) => (
          <div
            key={`${source.document_id}-${source.page_number}-${index}`}
            style={{
              padding: "9px 10px",
              borderBottom:
                index ===
                sources.length - 1
                  ? "none"
                  : "1px solid #f0f1f3",
              display: "flex",
              justifyContent:
                "space-between",
              gap: 14,
              fontSize: 10,
            }}
          >
            <div
              style={{
                minWidth: 0,
              }}
            >
              <div
                title={
                  source.filename
                }
                style={{
                  fontWeight: 600,
                  overflow:
                    "hidden",
                  textOverflow:
                    "ellipsis",
                  whiteSpace:
                    "nowrap",
                }}
              >
                {source.filename}
              </div>

              <div
                style={{
                  marginTop: 3,
                  color:
                    "#98a2b3",
                }}
              >
                Page{" "}
                {
                  source.page_number
                }
              </div>
            </div>

            <div
              style={{
                color: "#667085",
                whiteSpace:
                  "nowrap",
              }}
            >
              {formatScore(
                source.similarity_score,
              )}
            </div>
          </div>
        ),
      )}
    </div>
  );
}


function ApprovalCard({
  approvalId,
  toolName,
}: {
  approvalId: string;
  toolName?: string;
}) {
  return (
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
          alignItems: "center",
          gap: 6,
          color: "#b54708",
          fontSize: 11,
          fontWeight: 700,
        }}
      >
        <Sparkles size={13} />

        Human approval required
      </div>

      <div
        style={{
          marginTop: 6,
          color: "#667085",
          fontSize: 10,
        }}
      >
        Tool:{" "}
        {toolName ??
          "governed action"}
      </div>

      <div
        style={{
          marginTop: 3,
          color: "#98a2b3",
          fontSize: 9,
        }}
      >
        Approval ID:{" "}
        {approvalId}
      </div>
    </div>
  );
}


function formatScore(
  score: number,
): string {
  if (
    !Number.isFinite(score)
  ) {
    return "—";
  }

  return `${(
    score * 100
  ).toFixed(1)}%`;
}


const secondaryButtonStyle:
  React.CSSProperties = {
    border:
      "1px solid #d0d5dd",
    borderRadius: 9,
    background: "#ffffff",
    color: "#344054",
    padding: "8px 10px",
    display: "flex",
    alignItems: "center",
    gap: 6,
    fontSize: 11,
    fontWeight: 600,
    cursor: "pointer",
  };
