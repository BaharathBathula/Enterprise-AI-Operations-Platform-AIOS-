import {
  CheckCircle2,
  Clock3,
  FileText,
  MoreHorizontal,
  Search,
  Upload,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";

const documents = [
  {
    name: "production-runbook.pdf",
    type: "PDF",
    size: "2.4 MB",
    chunks: 86,
    status: "Indexed",
    uploaded: "Aug 24, 2026",
  },
  {
    name: "incident-response-policy.pdf",
    type: "PDF",
    size: "1.1 MB",
    chunks: 42,
    status: "Indexed",
    uploaded: "Aug 24, 2026",
  },
  {
    name: "checkout-api-architecture.pdf",
    type: "PDF",
    size: "3.8 MB",
    chunks: 124,
    status: "Indexed",
    uploaded: "Aug 23, 2026",
  },
  {
    name: "operations-handbook.pdf",
    type: "PDF",
    size: "5.2 MB",
    chunks: 168,
    status: "Processing",
    uploaded: "Aug 23, 2026",
  },
];

export default function DocumentsPage() {
  return (
    <AppShell>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 20,
        }}
      >
        <div>
          <h1 className="page-title">
            Documents
          </h1>

          <p className="page-subtitle">
            Manage enterprise knowledge indexed
            and retrieved by AIOS.
          </p>
        </div>

        <button
          type="button"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            border: "none",
            borderRadius: 10,
            background: "#111827",
            color: "#ffffff",
            padding: "10px 15px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          <Upload size={16} />
          Upload document
        </button>
      </div>

      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(3, minmax(0, 1fr))",
          gap: 18,
          marginTop: 26,
        }}
      >
        <MetricCard
          label="Total documents"
          value="1,248"
          detail="Enterprise knowledge files"
        />

        <MetricCard
          label="Indexed chunks"
          value="38,426"
          detail="Available for retrieval"
        />

        <MetricCard
          label="Processing"
          value="3"
          detail="Documents currently indexing"
        />
      </section>

      <section
        className="card"
        style={{
          marginTop: 18,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: 18,
            borderBottom: "1px solid #e4e7ec",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 20,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 15,
                fontWeight: 700,
              }}
            >
              Knowledge Base
            </div>

            <div
              style={{
                marginTop: 4,
                fontSize: 12,
                color: "#98a2b3",
              }}
            >
              Documents available to enterprise
              retrieval and AI agents
            </div>
          </div>

          <div
            style={{
              width: 280,
              display: "flex",
              alignItems: "center",
              gap: 8,
              border: "1px solid #d0d5dd",
              borderRadius: 9,
              padding: "8px 10px",
              color: "#98a2b3",
            }}
          >
            <Search size={15} />

            <input
              type="text"
              placeholder="Search documents"
              style={{
                width: "100%",
                border: "none",
                outline: "none",
                fontSize: 12,
                background: "transparent",
              }}
            />
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "minmax(260px, 2fr) 90px 100px 100px 130px 140px 50px",
            padding: "11px 18px",
            background: "#f9fafb",
            borderBottom: "1px solid #e4e7ec",
            color: "#667085",
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          <div>DOCUMENT</div>
          <div>TYPE</div>
          <div>SIZE</div>
          <div>CHUNKS</div>
          <div>STATUS</div>
          <div>UPLOADED</div>
          <div />
        </div>

        {documents.map((document) => (
          <div
            key={document.name}
            style={{
              display: "grid",
              gridTemplateColumns:
                "minmax(260px, 2fr) 90px 100px 100px 130px 140px 50px",
              padding: "15px 18px",
              borderBottom:
                "1px solid #f0f1f3",
              alignItems: "center",
              fontSize: 12,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 11,
              }}
            >
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 8,
                  background: "#f1f3f7",
                  display: "grid",
                  placeItems: "center",
                }}
              >
                <FileText
                  size={16}
                  color="#475467"
                />
              </div>

              <div
                style={{
                  fontWeight: 600,
                }}
              >
                {document.name}
              </div>
            </div>

            <div
              style={{
                color: "#667085",
              }}
            >
              {document.type}
            </div>

            <div
              style={{
                color: "#667085",
              }}
            >
              {document.size}
            </div>

            <div
              style={{
                color: "#667085",
              }}
            >
              {document.chunks}
            </div>

            <StatusBadge
              status={document.status}
            />

            <div
              style={{
                color: "#667085",
              }}
            >
              {document.uploaded}
            </div>

            <button
              type="button"
              aria-label={`Actions for ${document.name}`}
              style={{
                border: "none",
                background: "transparent",
                cursor: "pointer",
                color: "#667085",
              }}
            >
              <MoreHorizontal size={17} />
            </button>
          </div>
        ))}
      </section>

      <section
        className="card"
        style={{
          marginTop: 18,
          padding: 22,
          borderStyle: "dashed",
          textAlign: "center",
        }}
      >
        <div
          style={{
            width: 44,
            height: 44,
            margin: "0 auto",
            borderRadius: 12,
            background: "#f1f3f7",
            display: "grid",
            placeItems: "center",
          }}
        >
          <Upload
            size={20}
            color="#475467"
          />
        </div>

        <div
          style={{
            marginTop: 12,
            fontSize: 14,
            fontWeight: 700,
          }}
        >
          Add enterprise knowledge
        </div>

        <div
          style={{
            marginTop: 5,
            color: "#98a2b3",
            fontSize: 12,
          }}
        >
          Upload documents to extract,
          chunk, embed, and index them for
          AIOS retrieval.
        </div>

        <button
          type="button"
          style={{
            marginTop: 14,
            border: "1px solid #d0d5dd",
            borderRadius: 9,
            background: "#ffffff",
            padding: "8px 12px",
            fontSize: 12,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Select file
        </button>
      </section>
    </AppShell>
  );
}


function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article
      className="card"
      style={{
        padding: 20,
      }}
    >
      <div
        style={{
          color: "#667085",
          fontSize: 12,
        }}
      >
        {label}
      </div>

      <div
        style={{
          marginTop: 7,
          fontSize: 28,
          fontWeight: 700,
        }}
      >
        {value}
      </div>

      <div
        style={{
          marginTop: 5,
          color: "#98a2b3",
          fontSize: 11,
        }}
      >
        {detail}
      </div>
    </article>
  );
}


function StatusBadge({
  status,
}: {
  status: string;
}) {
  const indexed = status === "Indexed";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        width: "fit-content",
        padding: "5px 8px",
        borderRadius: 999,
        background: indexed
          ? "#ecfdf3"
          : "#fffaeb",
        color: indexed
          ? "#067647"
          : "#b54708",
        fontSize: 11,
        fontWeight: 600,
      }}
    >
      {indexed ? (
        <CheckCircle2 size={13} />
      ) : (
        <Clock3 size={13} />
      )}

      {status}
    </div>
  );
}
