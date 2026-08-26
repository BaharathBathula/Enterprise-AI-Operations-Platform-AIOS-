"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import {
  Bot,
  Clock3,
  Loader2,
  MessageSquare,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  User,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import { getSession } from "@/lib/session";


type MessageRole =
  | "user"
  | "assistant"
  | "system"
  | string;


type Conversation = {
  id: string;
  organization_id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
};


type ConversationMessage = {
  id: string;
  conversation_id: string;
  organization_id: string;
  role: MessageRole;
  content: string;
  created_at: string;
};


type ConversationDetail =
  Conversation & {
    messages: ConversationMessage[];
  };


export default function ConversationsPage() {
  const router = useRouter();

  const [conversations, setConversations] =
    useState<Conversation[]>([]);

  const [
    selectedConversation,
    setSelectedConversation,
  ] =
    useState<ConversationDetail | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);

  const [
    loadingConversation,
    setLoadingConversation,
  ] = useState(false);

  const [creating, setCreating] =
    useState(false);

  const [
    deletingId,
    setDeletingId,
  ] = useState<string | null>(
    null,
  );

  const [search, setSearch] =
    useState("");

  const [error, setError] =
    useState<string | null>(
      null,
    );


  const loadConversations =
    useCallback(async () => {
      const session =
        getSession();

      if (!session) {
        setError(
          "No active session. Sign in before loading conversations.",
        );

        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const result =
          await apiRequest<
            Conversation[]
          >(
            `/organizations/${session.organizationId}/conversations`,
            {
              token:
                session.accessToken,
            },
          );

        setConversations(
          result,
        );

        setSelectedConversation(
          (current) => {
            if (!current) {
              return null;
            }

            const stillExists =
              result.some(
                (item) =>
                  item.id ===
                  current.id,
              );

            return stillExists
              ? current
              : null;
          },
        );
      } catch (
        requestError
      ) {
        setError(
          getErrorMessage(
            requestError,
            "Unable to load conversations.",
          ),
        );
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    void loadConversations();
  }, [loadConversations]);


  const filteredConversations =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();

      if (!query) {
        return conversations;
      }

      return conversations.filter(
        (conversation) =>
          conversation.title
            .toLowerCase()
            .includes(query),
      );
    }, [
      conversations,
      search,
    ]);


  async function openConversation(
    conversation:
      Conversation,
  ) {
    const session =
      getSession();

    if (!session) {
      setError(
        "No active session.",
      );

      return;
    }

    setLoadingConversation(
      true,
    );

    setError(null);

    try {
      const result =
        await apiRequest<
          ConversationDetail
        >(
          `/organizations/${session.organizationId}/conversations/${conversation.id}`,
          {
            token:
              session.accessToken,
          },
        );

      setSelectedConversation(
        result,
      );
    } catch (
      requestError
    ) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to open conversation.",
        ),
      );
    } finally {
      setLoadingConversation(
        false,
      );
    }
  }


  async function createConversation() {
    const session =
      getSession();

    if (!session) {
      setError(
        "No active session.",
      );

      return;
    }

    const title =
      window.prompt(
        "Conversation title",
        "New conversation",
      );

    if (title === null) {
      return;
    }

    const cleanTitle =
      title.trim();

    if (!cleanTitle) {
      setError(
        "Conversation title cannot be empty.",
      );

      return;
    }

    setCreating(true);
    setError(null);

    try {
      const created =
        await apiRequest<
          Conversation
        >(
          `/organizations/${session.organizationId}/conversations`,
          {
            method: "POST",
            token:
              session.accessToken,
            body:
              JSON.stringify({
                title:
                  cleanTitle,
              }),
          },
        );

      setConversations(
        (current) => [
          created,
          ...current,
        ],
      );

      await openConversation(
        created,
      );
    } catch (
      requestError
    ) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to create conversation.",
        ),
      );
    } finally {
      setCreating(false);
    }
  }


  async function deleteConversation(
    conversation:
      Conversation,
  ) {
    const confirmed =
      window.confirm(
        `Delete "${conversation.title}" and its messages?`,
      );

    if (!confirmed) {
      return;
    }

    const session =
      getSession();

    if (!session) {
      setError(
        "No active session.",
      );

      return;
    }

    setDeletingId(
      conversation.id,
    );

    setError(null);

    try {
      await apiRequest<void>(
        `/organizations/${session.organizationId}/conversations/${conversation.id}`,
        {
          method: "DELETE",
          token:
            session.accessToken,
        },
      );

      setConversations(
        (current) =>
          current.filter(
            (item) =>
              item.id !==
              conversation.id,
          ),
      );

      if (
        selectedConversation?.id ===
        conversation.id
      ) {
        setSelectedConversation(
          null,
        );
      }
    } catch (
      requestError
    ) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to delete conversation.",
        ),
      );
    } finally {
      setDeletingId(null);
    }
  }


  function continueInCopilot() {
    if (
      !selectedConversation
    ) {
      return;
    }

    router.push(
      `/copilot?conversationId=${encodeURIComponent(
        selectedConversation.id,
      )}`,
    );
  }


  return (
    <AppShell>
      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems:
            "flex-start",
          gap: 20,
        }}
      >
        <div>
          <h1 className="page-title">
            Conversations
          </h1>

          <p className="page-subtitle">
            Reopen previous AIOS
            knowledge conversations
            and continue them in
            Copilot.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: 10,
          }}
        >
          <button
            type="button"
            onClick={() =>
              void loadConversations()
            }
            disabled={loading}
            style={
              secondaryButtonStyle
            }
          >
            <RefreshCw
              size={15}
            />

            Refresh
          </button>

          <button
            type="button"
            onClick={() =>
              void createConversation()
            }
            disabled={creating}
            style={
              primaryButtonStyle
            }
          >
            {creating ? (
              <Loader2
                size={15}
              />
            ) : (
              <Plus
                size={15}
              />
            )}

            New conversation
          </button>
        </div>
      </div>


      {error && (
        <div
          style={{
            marginTop: 18,
            padding:
              "12px 14px",
            borderRadius: 10,
            background:
              "#fef3f2",
            color: "#b42318",
            fontSize: 12,
          }}
        >
          {error}
        </div>
      )}


      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "340px minmax(0, 1fr)",
          gap: 18,
          marginTop: 24,
          minHeight: 620,
        }}
      >
        <article
          className="card"
          style={{
            overflow:
              "hidden",
          }}
        >
          <div
            style={{
              padding: 16,
              borderBottom:
                "1px solid #e4e7ec",
            }}
          >
            <div
              style={{
                fontSize: 14,
                fontWeight:
                  700,
              }}
            >
              Conversation
              History
            </div>

            <div
              style={{
                marginTop: 4,
                color:
                  "#98a2b3",
                fontSize: 11,
              }}
            >
              {
                conversations.length
              }{" "}
              saved conversations
            </div>


            <div
              style={{
                marginTop: 14,
                display: "flex",
                alignItems:
                  "center",
                gap: 8,
                border:
                  "1px solid #d0d5dd",
                borderRadius: 9,
                padding:
                  "8px 10px",
              }}
            >
              <Search
                size={14}
                color="#98a2b3"
              />

              <input
                value={search}
                onChange={(
                  event,
                ) =>
                  setSearch(
                    event.target
                      .value,
                  )
                }
                placeholder="Search conversations"
                style={{
                  width: "100%",
                  border: "none",
                  outline: "none",
                  background:
                    "transparent",
                  fontSize: 12,
                }}
              />
            </div>
          </div>


          <div
            style={{
              maxHeight: 540,
              overflowY:
                "auto",
            }}
          >
            {loading ? (
              <SidebarEmpty
                text="Loading conversations..."
              />
            ) : filteredConversations.length ===
              0 ? (
              <SidebarEmpty
                text={
                  search
                    ? "No matching conversations."
                    : "No conversations yet."
                }
              />
            ) : (
              filteredConversations.map(
                (
                  conversation,
                ) => (
                  <ConversationItem
                    key={
                      conversation.id
                    }
                    conversation={
                      conversation
                    }
                    selected={
                      selectedConversation?.id ===
                      conversation.id
                    }
                    deleting={
                      deletingId ===
                      conversation.id
                    }
                    onOpen={() =>
                      void openConversation(
                        conversation,
                      )
                    }
                    onDelete={() =>
                      void deleteConversation(
                        conversation,
                      )
                    }
                  />
                ),
              )
            )}
          </div>
        </article>


        <article
          className="card"
          style={{
            overflow:
              "hidden",
          }}
        >
          {loadingConversation ? (
            <ConversationEmpty
              icon={
                <Loader2
                  size={28}
                  color="#98a2b3"
                />
              }
              title="Loading conversation..."
              detail="Reading persisted messages from AIOS."
            />
          ) : !selectedConversation ? (
            <ConversationEmpty
              icon={
                <MessageSquare
                  size={28}
                  color="#98a2b3"
                />
              }
              title="Select a conversation"
              detail="Choose a saved thread from the left to inspect its complete message history."
            />
          ) : (
            <>
              <div
                style={{
                  padding:
                    "18px 20px",
                  borderBottom:
                    "1px solid #e4e7ec",
                  display:
                    "flex",
                  justifyContent:
                    "space-between",
                  alignItems:
                    "center",
                  gap: 16,
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize:
                        15,
                      fontWeight:
                        700,
                    }}
                  >
                    {
                      selectedConversation.title
                    }
                  </div>

                  <div
                    style={{
                      marginTop: 5,
                      display:
                        "flex",
                      alignItems:
                        "center",
                      gap: 6,
                      color:
                        "#98a2b3",
                      fontSize:
                        11,
                    }}
                  >
                    <Clock3
                      size={12}
                    />

                    Updated{" "}
                    {formatDate(
                      selectedConversation.updated_at,
                    )}

                    <span>
                      •
                    </span>

                    {
                      selectedConversation
                        .messages
                        .length
                    }{" "}
                    messages
                  </div>
                </div>


                <button
                  type="button"
                  onClick={
                    continueInCopilot
                  }
                  style={
                    primaryButtonStyle
                  }
                >
                  <Bot
                    size={15}
                  />

                  Continue in
                  Copilot
                </button>
              </div>


              <div
                style={{
                  padding: 22,
                  display:
                    "grid",
                  gap: 18,
                  maxHeight:
                    540,
                  overflowY:
                    "auto",
                }}
              >
                {selectedConversation
                  .messages
                  .length ===
                0 ? (
                  <div
                    style={{
                      padding: 40,
                      textAlign:
                        "center",
                      color:
                        "#98a2b3",
                      fontSize:
                        12,
                    }}
                  >
                    This
                    conversation
                    does not
                    contain any
                    messages yet.
                  </div>
                ) : (
                  selectedConversation.messages.map(
                    (
                      message,
                    ) => (
                      <MessageBubble
                        key={
                          message.id
                        }
                        message={
                          message
                        }
                      />
                    ),
                  )
                )}
              </div>
            </>
          )}
        </article>
      </section>
    </AppShell>
  );
}


function ConversationItem({
  conversation,
  selected,
  deleting,
  onOpen,
  onDelete,
}: {
  conversation:
    Conversation;
  selected: boolean;
  deleting: boolean;
  onOpen: () => void;
  onDelete: () => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems:
          "center",
        gap: 8,
        padding:
          "12px 12px",
        borderBottom:
          "1px solid #f0f1f3",
        background:
          selected
            ? "#f8fafc"
            : "#ffffff",
      }}
    >
      <button
        type="button"
        onClick={onOpen}
        style={{
          flex: 1,
          minWidth: 0,
          border: "none",
          background:
            "transparent",
          cursor:
            "pointer",
          textAlign:
            "left",
          padding: 4,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems:
              "center",
            gap: 8,
          }}
        >
          <MessageSquare
            size={15}
            color={
              selected
                ? "#344054"
                : "#98a2b3"
            }
          />

          <div
            title={
              conversation.title
            }
            style={{
              flex: 1,
              overflow:
                "hidden",
              textOverflow:
                "ellipsis",
              whiteSpace:
                "nowrap",
              fontSize: 12,
              fontWeight:
                selected
                  ? 700
                  : 600,
              color:
                "#344054",
            }}
          >
            {
              conversation.title
            }
          </div>
        </div>

        <div
          style={{
            marginTop: 6,
            marginLeft: 23,
            color:
              "#98a2b3",
            fontSize: 10,
          }}
        >
          {formatDate(
            conversation.updated_at,
          )}
        </div>
      </button>


      <button
        type="button"
        onClick={
          onDelete
        }
        disabled={
          deleting
        }
        title="Delete conversation"
        style={{
          border: "none",
          background:
            "transparent",
          color: "#b42318",
          cursor:
            deleting
              ? "not-allowed"
              : "pointer",
          padding: 6,
        }}
      >
        {deleting ? (
          <Loader2
            size={14}
          />
        ) : (
          <Trash2
            size={14}
          />
        )}
      </button>
    </div>
  );
}


function MessageBubble({
  message,
}: {
  message:
    ConversationMessage;
}) {
  const isUser =
    message.role ===
    "user";

  const isAssistant =
    message.role ===
    "assistant";

  return (
    <div
      style={{
        display: "flex",
        justifyContent:
          isUser
            ? "flex-end"
            : "flex-start",
      }}
    >
      <div
        style={{
          width:
            "min(82%, 760px)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems:
              "center",
            justifyContent:
              isUser
                ? "flex-end"
                : "flex-start",
            gap: 6,
            marginBottom: 6,
            color:
              "#667085",
            fontSize: 10,
            fontWeight: 600,
            textTransform:
              "capitalize",
          }}
        >
          {isUser ? (
            <User
              size={12}
            />
          ) : isAssistant ? (
            <Bot
              size={12}
            />
          ) : (
            <MessageSquare
              size={12}
            />
          )}

          {message.role}

          <span>•</span>

          {formatDate(
            message.created_at,
          )}
        </div>


        <div
          style={{
            borderRadius: 14,
            padding:
              "13px 15px",
            background:
              isUser
                ? "#111827"
                : "#f8fafc",
            color:
              isUser
                ? "#ffffff"
                : "#344054",
            fontSize: 13,
            lineHeight: 1.7,
            whiteSpace:
              "pre-wrap",
            border:
              isUser
                ? "none"
                : "1px solid #e4e7ec",
          }}
        >
          {message.content}
        </div>
      </div>
    </div>
  );
}


function ConversationEmpty({
  icon,
  title,
  detail,
}: {
  icon: React.ReactNode;
  title: string;
  detail: string;
}) {
  return (
    <div
      style={{
        height: 560,
        display: "grid",
        placeItems:
          "center",
        padding: 30,
        textAlign:
          "center",
      }}
    >
      <div>
        {icon}

        <div
          style={{
            marginTop: 12,
            fontSize: 15,
            fontWeight: 700,
          }}
        >
          {title}
        </div>

        <div
          style={{
            maxWidth: 420,
            margin:
              "7px auto 0",
            color:
              "#98a2b3",
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          {detail}
        </div>
      </div>
    </div>
  );
}


function SidebarEmpty({
  text,
}: {
  text: string;
}) {
  return (
    <div
      style={{
        padding:
          "42px 18px",
        textAlign:
          "center",
        color:
          "#98a2b3",
        fontSize: 12,
      }}
    >
      {text}
    </div>
  );
}


function formatDate(
  value: string,
): string {
  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return date.toLocaleString(
    undefined,
    {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    },
  );
}


function getErrorMessage(
  error: unknown,
  fallback: string,
): string {
  if (
    error instanceof
    ApiError
  ) {
    return error.detail;
  }

  return fallback;
}


const primaryButtonStyle:
  React.CSSProperties = {
    border: "none",
    borderRadius: 10,
    background: "#111827",
    color: "#ffffff",
    padding: "10px 15px",
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: 7,
  };


const secondaryButtonStyle:
  React.CSSProperties = {
    border:
      "1px solid #d0d5dd",
    borderRadius: 10,
    background: "#ffffff",
    color: "#344054",
    padding: "10px 14px",
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: 7,
  };
