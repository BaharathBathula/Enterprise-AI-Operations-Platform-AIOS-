"use client";

import {
  FormEvent,
  useState,
} from "react";
import {
  BookOpen,
  FileText,
  Loader2,
  Search,
  Sparkles,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import {
  getSession,
} from "@/lib/session";


type RAGSource = {
  document_id: string;
  filename: string;
  page_number: number;
  similarity_score: number;
};


type RAGAnswerResponse = {
  conversation_id: string;
  answer: string;
  sources: RAGSource[];
};


type SearchResult = {
  question: string;
  answer: string;
  sources: RAGSource[];
};


export default function KnowledgePage() {
  const [question, setQuestion] =
    useState("");

  const [topK, setTopK] =
    useState(5);

  const [
    conversationId,
    setConversationId,
  ] = useState<string | null>(
    null,
  );

  const [result, setResult] =
    useState<SearchResult | null>(
      null,
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const cleanQuestion =
      question.trim();

    if (
      cleanQuestion.length < 3
    ) {
      setError(
        "Enter a question with at least 3 characters.",
      );
      return;
    }

    const session = getSession();

    if (!session) {
      setError(
        "No active session. Sign in before searching workspace knowledge.",
      );
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response =
        await apiRequest<
          RAGAnswerResponse
        >(
          `/organizations/${session.organizationId}/chat`,
          {
            method: "POST",
            token:
              session.accessToken,
            body:
              JSON.stringify({
                question:
                  cleanQuestion,
                conversation_id:
                  conversationId,
                top_k: topK,
              }),
          },
        );

      setConversationId(
        response.conversation_id,
      );

      setResult({
        question:
          cleanQuestion,
        answer:
          response.answer,
        sources:
          response.sources,
      });

      setQuestion("");
    } catch (requestError) {
      if (
        requestError instanceof
        ApiError
      ) {
        setError(
          requestError.detail,
        );
      } else {
        setError(
          "Unable to search workspace knowledge.",
        );
      }
    } finally {
      setLoading(false);
    }
  }


  function startNewConversation() {
    setConversationId(null);
    setResult(null);
    setQuestion("");
    setError(null);
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
            Knowledge Retrieval
          </h1>

          <p className="page-subtitle">
            Ask questions across
            processed enterprise
            documents and receive
            grounded answers with
            source evidence.
          </p>
        </div>

        <button
          type="button"
          onClick={
            startNewConversation
          }
          style={
            secondaryButtonStyle
          }
        >
          New conversation
        </button>
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
        className="card"
        style={{
          marginTop: 24,
          padding: 24,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems:
              "center",
            gap: 10,
          }}
        >
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: 10,
              background:
                "#f1f3f7",
              display: "grid",
              placeItems:
                "center",
            }}
          >
            <BookOpen
              size={18}
              color="#475467"
            />
          </div>

          <div>
            <div
              style={{
                fontWeight: 700,
                fontSize: 15,
              }}
            >
              Ask your knowledge
              base
            </div>

            <div
              style={{
                marginTop: 3,
                color:
                  "#98a2b3",
                fontSize: 12,
              }}
            >
              AIOS retrieves the
              most relevant document
              context before
              generating an answer.
            </div>
          </div>
        </div>


        <form
          onSubmit={handleSubmit}
          style={{
            marginTop: 22,
          }}
        >
          <div
            style={{
              display: "flex",
              gap: 10,
              alignItems:
                "stretch",
            }}
          >
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems:
                  "center",
                gap: 9,
                border:
                  "1px solid #d0d5dd",
                borderRadius: 10,
                padding:
                  "10px 12px",
                background:
                  "#ffffff",
              }}
            >
              <Search
                size={17}
                color="#98a2b3"
              />

              <input
                type="text"
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target
                      .value,
                  )
                }
                placeholder="Example: What is the incident escalation procedure?"
                disabled={loading}
                style={{
                  flex: 1,
                  border: "none",
                  outline: "none",
                  fontSize: 13,
                  background:
                    "transparent",
                }}
              />
            </div>

            <select
              value={topK}
              onChange={(event) =>
                setTopK(
                  Number(
                    event.target
                      .value,
                  ),
                )
              }
              disabled={loading}
              aria-label="Number of sources"
              style={{
                border:
                  "1px solid #d0d5dd",
                borderRadius: 10,
                background:
                  "#ffffff",
                padding:
                  "10px 12px",
                color:
                  "#475467",
                fontSize: 12,
              }}
            >
              <option value={3}>
                Top 3
              </option>

              <option value={5}>
                Top 5
              </option>

              <option value={8}>
                Top 8
              </option>

              <option value={10}>
                Top 10
              </option>
            </select>

            <button
              type="submit"
              disabled={
                loading ||
                question
                  .trim()
                  .length < 3
              }
              style={{
                ...primaryButtonStyle,
                opacity:
                  loading
                    ? 0.65
                    : 1,
              }}
            >
              {loading ? (
                <Loader2
                  size={16}
                />
              ) : (
                <Sparkles
                  size={16}
                />
              )}

              {loading
                ? "Searching..."
                : "Ask AIOS"}
            </button>
          </div>
        </form>


        {conversationId && (
          <div
            style={{
              marginTop: 12,
              color:
                "#98a2b3",
              fontSize: 10,
            }}
          >
            Conversation{" "}
            {conversationId.slice(
              0,
              8,
            )}
          </div>
        )}
      </section>


      {!result && !loading && (
        <section
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(3, minmax(0, 1fr))",
            gap: 18,
            marginTop: 18,
          }}
        >
          <ExampleCard
            title="Operational procedures"
            question="What steps should engineers follow during a production outage?"
            onSelect={
              setQuestion
            }
          />

          <ExampleCard
            title="Architecture knowledge"
            question="How does the checkout service communicate with downstream systems?"
            onSelect={
              setQuestion
            }
          />

          <ExampleCard
            title="Policy retrieval"
            question="What approval requirements apply before executing a production change?"
            onSelect={
              setQuestion
            }
          />
        </section>
      )}


      {result && (
        <section
          style={{
            display: "grid",
            gridTemplateColumns:
              "minmax(0, 1.7fr) minmax(300px, 1fr)",
            gap: 18,
            marginTop: 18,
          }}
        >
          <article
            className="card"
            style={{
              padding: 24,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems:
                  "center",
                gap: 8,
                fontWeight: 700,
                fontSize: 15,
              }}
            >
              <Sparkles
                size={17}
              />
              Grounded Answer
            </div>

            <div
              style={{
                marginTop: 18,
                padding:
                  "14px 16px",
                borderRadius: 10,
                background:
                  "#f8fafc",
              }}
            >
              <div
                style={{
                  color:
                    "#667085",
                  fontSize: 11,
                  fontWeight: 600,
                }}
              >
                QUESTION
              </div>

              <div
                style={{
                  marginTop: 6,
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                {result.question}
              </div>
            </div>

            <div
              style={{
                marginTop: 20,
                whiteSpace:
                  "pre-wrap",
                lineHeight: 1.75,
                fontSize: 13,
                color:
                  "#344054",
              }}
            >
              {result.answer}
            </div>
          </article>


          <article
            className="card"
            style={{
              padding: 22,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems:
                  "center",
                gap: 8,
                fontWeight: 700,
                fontSize: 14,
              }}
            >
              <FileText
                size={16}
              />
              Sources
            </div>

            <div
              style={{
                marginTop: 4,
                color:
                  "#98a2b3",
                fontSize: 11,
              }}
            >
              Retrieved document
              evidence used for this
              answer
            </div>


            <div
              style={{
                marginTop: 16,
                display: "grid",
                gap: 10,
              }}
            >
              {result.sources.length ===
              0 ? (
                <div
                  style={{
                    padding:
                      "20px 10px",
                    textAlign:
                      "center",
                    color:
                      "#98a2b3",
                    fontSize: 12,
                  }}
                >
                  No document sources
                  were returned.
                </div>
              ) : (
                result.sources.map(
                  (
                    source,
                    index,
                  ) => (
                    <SourceCard
                      key={`${source.document_id}-${source.page_number}-${index}`}
                      source={
                        source
                      }
                      index={
                        index + 1
                      }
                    />
                  ),
                )
              )}
            </div>
          </article>
        </section>
      )}
    </AppShell>
  );
}


function SourceCard({
  source,
  index,
}: {
  source: RAGSource;
  index: number;
}) {
  return (
    <div
      style={{
        border:
          "1px solid #e4e7ec",
        borderRadius: 10,
        padding: 12,
      }}
    >
      <div
        style={{
          display: "flex",
          gap: 10,
          alignItems:
            "flex-start",
        }}
      >
        <div
          style={{
            width: 28,
            height: 28,
            flexShrink: 0,
            borderRadius: 8,
            background:
              "#f1f3f7",
            display: "grid",
            placeItems:
              "center",
            fontSize: 11,
            fontWeight: 700,
          }}
        >
          {index}
        </div>

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
              fontSize: 12,
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
              marginTop: 5,
              color:
                "#667085",
              fontSize: 11,
            }}
          >
            Page{" "}
            {source.page_number}
          </div>

          <div
            style={{
              marginTop: 4,
              color:
                "#98a2b3",
              fontSize: 10,
            }}
          >
            Similarity{" "}
            {formatScore(
              source.similarity_score,
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


function ExampleCard({
  title,
  question,
  onSelect,
}: {
  title: string;
  question: string;
  onSelect: (
    question: string,
  ) => void;
}) {
  return (
    <button
      type="button"
      onClick={() =>
        onSelect(question)
      }
      className="card"
      style={{
        padding: 20,
        border: "none",
        textAlign: "left",
        cursor: "pointer",
        background:
          "#ffffff",
      }}
    >
      <BookOpen
        size={18}
        color="#475467"
      />

      <div
        style={{
          marginTop: 12,
          fontWeight: 700,
          fontSize: 13,
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 7,
          color: "#667085",
          fontSize: 11,
          lineHeight: 1.6,
        }}
      >
        {question}
      </div>
    </button>
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
  };
