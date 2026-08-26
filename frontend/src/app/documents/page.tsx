"use client";

import {
  ChangeEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  FileText,
  Loader2,
  Play,
  RefreshCw,
  Search,
  Trash2,
  Upload,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import {
  ApiError,
  apiRequest,
} from "@/lib/api";
import { getSession } from "@/lib/session";


type DocumentStatus =
  | "uploaded"
  | "processing"
  | "processed"
  | "failed"
  | string;


type DocumentRecord = {
  id: string;
  organization_id: string;
  uploaded_by_user_id: string | null;

  filename: string;
  original_filename: string;
  content_type: string;
  file_size: number;

  status: DocumentStatus;
  processing_error: string | null;
  page_count: number | null;

  created_at: string;
  updated_at: string;
};


type DocumentProcessingResponse = {
  id: string;
  status: DocumentStatus;
  page_count: number | null;
  processing_error: string | null;
};


export default function DocumentsPage() {
  const [documents, setDocuments] =
    useState<DocumentRecord[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const [processingId, setProcessingId] =
    useState<string | null>(null);

  const [deletingId, setDeletingId] =
    useState<string | null>(null);

  const [search, setSearch] =
    useState("");

  const [error, setError] =
    useState<string | null>(null);

  const fileInputRef =
    useRef<HTMLInputElement | null>(
      null,
    );


  const loadDocuments =
    useCallback(async () => {
      const session = getSession();

      if (!session) {
        setError(
          "No active session. Sign in before loading documents.",
        );
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const result =
          await apiRequest<
            DocumentRecord[]
          >(
            `/organizations/${session.organizationId}/documents`,
            {
              token:
                session.accessToken,
            },
          );

        setDocuments(result);
      } catch (requestError) {
        setError(
          getErrorMessage(
            requestError,
            "Unable to load documents.",
          ),
        );
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    void loadDocuments();
  }, [loadDocuments]);


  const filteredDocuments =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();

      if (!query) {
        return documents;
      }

      return documents.filter(
        (document) =>
          document.original_filename
            .toLowerCase()
            .includes(query) ||
          document.content_type
            .toLowerCase()
            .includes(query) ||
          document.status
            .toLowerCase()
            .includes(query),
      );
    }, [documents, search]);


  const metrics =
    useMemo(() => {
      const processing =
        documents.filter(
          (document) =>
            normalizeStatus(
              document.status,
            ) === "processing",
        ).length;

      const processed =
        documents.filter(
          (document) =>
            isProcessed(
              document.status,
            ),
        ).length;

      const totalPages =
        documents.reduce(
          (total, document) =>
            total +
            (document.page_count ??
              0),
          0,
        );

      return {
        total:
          documents.length,
        processed,
        processing,
        totalPages,
      };
    }, [documents]);


  async function handleFileChange(
    event:
      ChangeEvent<HTMLInputElement>,
  ) {
    const file =
      event.target.files?.[0];

    event.target.value = "";

    if (!file) {
      return;
    }

    await uploadDocument(file);
  }


  async function uploadDocument(
    file: File,
  ) {
    const session = getSession();

    if (!session) {
      setError(
        "No active session.",
      );
      return;
    }

    setUploading(true);
    setError(null);

    const formData =
      new FormData();

    formData.append(
      "file",
      file,
    );

    try {
      const uploaded =
        await apiRequest<
          DocumentRecord
        >(
          `/organizations/${session.organizationId}/documents`,
          {
            method: "POST",
            token:
              session.accessToken,
            body: formData,
          },
        );

      setDocuments(
        (current) => [
          uploaded,
          ...current,
        ],
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to upload document.",
        ),
      );
    } finally {
      setUploading(false);
    }
  }


  async function processDocument(
    document: DocumentRecord,
  ) {
    const session = getSession();

    if (!session) {
      setError(
        "No active session.",
      );
      return;
    }

    setProcessingId(
      document.id,
    );
    setError(null);

    try {
      const result =
        await apiRequest<
          DocumentProcessingResponse
        >(
          `/organizations/${session.organizationId}/documents/${document.id}/process`,
          {
            method: "POST",
            token:
              session.accessToken,
          },
        );

      setDocuments(
        (current) =>
          current.map((item) =>
            item.id ===
            result.id
              ? {
                  ...item,
                  status:
                    result.status,
                  page_count:
                    result.page_count,
                  processing_error:
                    result.processing_error,
                }
              : item,
          ),
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to process document.",
        ),
      );

      await loadDocuments();
    } finally {
      setProcessingId(null);
    }
  }


  async function deleteDocument(
    document: DocumentRecord,
  ) {
    const confirmed =
      window.confirm(
        `Delete "${document.original_filename}"? This cannot be undone.`,
      );

    if (!confirmed) {
      return;
    }

    const session = getSession();

    if (!session) {
      setError(
        "No active session.",
      );
      return;
    }

    setDeletingId(
      document.id,
    );
    setError(null);

    try {
      await apiRequest<void>(
        `/organizations/${session.organizationId}/documents/${document.id}`,
        {
          method: "DELETE",
          token:
            session.accessToken,
        },
      );

      setDocuments(
        (current) =>
          current.filter(
            (item) =>
              item.id !==
              document.id,
          ),
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to delete document.",
        ),
      );
    } finally {
      setDeletingId(null);
    }
  }


  function openFilePicker() {
    fileInputRef.current?.click();
  }


  return (
    <AppShell>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={
          handleFileChange
        }
        style={{
          display: "none",
        }}
      />

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
            Documents
          </h1>

          <p className="page-subtitle">
            Upload, process, and
            manage enterprise
            knowledge used by AIOS.
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
              void loadDocuments()
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
            onClick={
              openFilePicker
            }
            disabled={uploading}
            style={{
              ...primaryButtonStyle,
              opacity:
                uploading
                  ? 0.65
                  : 1,
            }}
          >
            {uploading ? (
              <Loader2
                size={16}
              />
            ) : (
              <Upload
                size={16}
              />
            )}

            {uploading
              ? "Uploading..."
              : "Upload document"}
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
            display: "flex",
            alignItems:
              "flex-start",
            gap: 8,
            fontSize: 12,
          }}
        >
          <AlertCircle
            size={16}
          />

          <span>{error}</span>
        </div>
      )}


      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(4, minmax(0, 1fr))",
          gap: 18,
          marginTop: 26,
        }}
      >
        <MetricCard
          label="Total documents"
          value={
            loading
              ? "—"
              : String(
                  metrics.total,
                )
          }
          detail="Workspace files"
        />

        <MetricCard
          label="Processed"
          value={
            loading
              ? "—"
              : String(
                  metrics.processed,
                )
          }
          detail="Ready documents"
        />

        <MetricCard
          label="Total pages"
          value={
            loading
              ? "—"
              : String(
                  metrics.totalPages,
                )
          }
          detail="Pages extracted"
        />

        <MetricCard
          label="Processing"
          value={
            loading
              ? "—"
              : String(
                  metrics.processing,
                )
          }
          detail="Active processing"
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
            borderBottom:
              "1px solid #e4e7ec",
            display: "flex",
            justifyContent:
              "space-between",
            alignItems:
              "center",
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
              Real documents stored
              in the current AIOS
              organization
            </div>
          </div>


          <div
            style={{
              width: 300,
              display: "flex",
              alignItems:
                "center",
              gap: 8,
              border:
                "1px solid #d0d5dd",
              borderRadius: 9,
              padding:
                "8px 10px",
              color: "#98a2b3",
            }}
          >
            <Search size={15} />

            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target
                    .value,
                )
              }
              placeholder="Search documents"
              style={{
                width: "100%",
                border: "none",
                outline: "none",
                fontSize: 12,
                background:
                  "transparent",
              }}
            />
          </div>
        </div>


        {loading ? (
          <EmptyState
            title="Loading documents..."
            detail="Reading workspace documents from the AIOS API."
          />
        ) : filteredDocuments.length ===
          0 ? (
          <EmptyState
            title={
              search
                ? "No matching documents"
                : "No documents yet"
            }
            detail={
              search
                ? "Try a different search."
                : "Upload the first PDF to this workspace."
            }
          />
        ) : (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "minmax(260px, 2fr) 100px 100px 100px 135px 150px 180px",
                padding:
                  "11px 18px",
                background:
                  "#f9fafb",
                borderBottom:
                  "1px solid #e4e7ec",
                color: "#667085",
                fontSize: 11,
                fontWeight: 600,
              }}
            >
              <div>DOCUMENT</div>
              <div>TYPE</div>
              <div>SIZE</div>
              <div>PAGES</div>
              <div>STATUS</div>
              <div>UPLOADED</div>
              <div>ACTIONS</div>
            </div>


            {filteredDocuments.map(
              (document) => (
                <DocumentRow
                  key={document.id}
                  document={
                    document
                  }
                  processing={
                    processingId ===
                    document.id
                  }
                  deleting={
                    deletingId ===
                    document.id
                  }
                  onProcess={() =>
                    void processDocument(
                      document,
                    )
                  }
                  onDelete={() =>
                    void deleteDocument(
                      document,
                    )
                  }
                />
              ),
            )}
          </>
        )}
      </section>


      <section
        className="card"
        style={{
          marginTop: 18,
          padding: 28,
          borderStyle:
            "dashed",
          textAlign:
            "center",
        }}
      >
        <div
          style={{
            width: 44,
            height: 44,
            margin: "0 auto",
            borderRadius: 12,
            background:
              "#f1f3f7",
            display: "grid",
            placeItems:
              "center",
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
          Upload a PDF and then
          explicitly process it
          through the AIOS document
          pipeline.
        </div>

        <button
          type="button"
          onClick={
            openFilePicker
          }
          disabled={uploading}
          style={{
            ...secondaryButtonStyle,
            margin:
              "14px auto 0",
          }}
        >
          <Upload size={14} />

          Select PDF
        </button>
      </section>
    </AppShell>
  );
}


function DocumentRow({
  document,
  processing,
  deleting,
  onProcess,
  onDelete,
}: {
  document: DocumentRecord;
  processing: boolean;
  deleting: boolean;
  onProcess: () => void;
  onDelete: () => void;
}) {
  const status =
    normalizeStatus(
      document.status,
    );

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "minmax(260px, 2fr) 100px 100px 100px 135px 150px 180px",
        padding:
          "15px 18px",
        borderBottom:
          "1px solid #f0f1f3",
        alignItems:
          "center",
        fontSize: 12,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems:
            "center",
          gap: 11,
          minWidth: 0,
        }}
      >
        <div
          style={{
            width: 34,
            height: 34,
            flexShrink: 0,
            borderRadius: 8,
            background:
              "#f1f3f7",
            display: "grid",
            placeItems:
              "center",
          }}
        >
          <FileText
            size={16}
            color="#475467"
          />
        </div>

        <div
          style={{
            minWidth: 0,
          }}
        >
          <div
            title={
              document.original_filename
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
            {
              document.original_filename
            }
          </div>

          {document.processing_error && (
            <div
              title={
                document.processing_error
              }
              style={{
                marginTop: 3,
                color:
                  "#b42318",
                fontSize: 10,
                overflow:
                  "hidden",
                textOverflow:
                  "ellipsis",
                whiteSpace:
                  "nowrap",
              }}
            >
              {
                document.processing_error
              }
            </div>
          )}
        </div>
      </div>


      <div
        style={{
          color: "#667085",
        }}
      >
        {formatType(
          document.content_type,
        )}
      </div>


      <div
        style={{
          color: "#667085",
        }}
      >
        {formatBytes(
          document.file_size,
        )}
      </div>


      <div
        style={{
          color: "#667085",
        }}
      >
        {document.page_count ??
          "—"}
      </div>


      <StatusBadge
        status={status}
      />


      <div
        style={{
          color: "#667085",
        }}
      >
        {formatDate(
          document.created_at,
        )}
      </div>


      <div
        style={{
          display: "flex",
          alignItems:
            "center",
          gap: 8,
        }}
      >
        {!isProcessed(
          document.status,
        ) && (
          <button
            type="button"
            onClick={
              onProcess
            }
            disabled={
              processing ||
              deleting ||
              status ===
                "processing"
            }
            title="Process document"
            style={
              smallButtonStyle
            }
          >
            {processing ? (
              <Loader2
                size={13}
              />
            ) : (
              <Play
                size={13}
              />
            )}

            {processing
              ? "Processing"
              : "Process"}
          </button>
        )}

        <button
          type="button"
          onClick={onDelete}
          disabled={
            deleting ||
            processing
          }
          title="Delete document"
          style={{
            ...smallButtonStyle,
            color: "#b42318",
          }}
        >
          {deleting ? (
            <Loader2
              size={13}
            />
          ) : (
            <Trash2
              size={13}
            />
          )}

          {deleting
            ? "Deleting"
            : "Delete"}
        </button>
      </div>
    </div>
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
  let background =
    "#f2f4f7";

  let color =
    "#475467";

  let icon =
    <Clock3 size={13} />;

  if (
    status === "processed" ||
    status === "indexed" ||
    status === "completed"
  ) {
    background =
      "#ecfdf3";
    color = "#067647";
    icon =
      <CheckCircle2
        size={13}
      />;
  }

  if (
    status === "processing"
  ) {
    background =
      "#fffaeb";
    color = "#b54708";
    icon =
      <Loader2
        size={13}
      />;
  }

  if (
    status === "failed" ||
    status === "error"
  ) {
    background =
      "#fef3f2";
    color = "#b42318";
    icon =
      <AlertCircle
        size={13}
      />;
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems:
          "center",
        gap: 6,
        width: "fit-content",
        padding: "5px 8px",
        borderRadius: 999,
        background,
        color,
        fontSize: 11,
        fontWeight: 600,
        textTransform:
          "capitalize",
      }}
    >
      {icon}
      {status}
    </div>
  );
}


function EmptyState({
  title,
  detail,
}: {
  title: string;
  detail: string;
}) {
  return (
    <div
      style={{
        padding:
          "52px 20px",
        textAlign:
          "center",
      }}
    >
      <FileText
        size={27}
        color="#98a2b3"
      />

      <div
        style={{
          marginTop: 12,
          fontSize: 14,
          fontWeight: 700,
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 6,
          color: "#98a2b3",
          fontSize: 12,
        }}
      >
        {detail}
      </div>
    </div>
  );
}


function normalizeStatus(
  status: string,
): string {
  return status
    .trim()
    .toLowerCase();
}


function isProcessed(
  status: string,
): boolean {
  const normalized =
    normalizeStatus(status);

  return (
    normalized ===
      "processed" ||
    normalized ===
      "indexed" ||
    normalized ===
      "completed"
  );
}


function formatType(
  contentType: string,
): string {
  if (
    contentType ===
    "application/pdf"
  ) {
    return "PDF";
  }

  return contentType;
}


function formatBytes(
  bytes: number,
): string {
  if (
    !Number.isFinite(bytes) ||
    bytes < 0
  ) {
    return "—";
  }

  if (bytes < 1024) {
    return `${bytes} B`;
  }

  const kb =
    bytes / 1024;

  if (kb < 1024) {
    return `${kb.toFixed(
      1,
    )} KB`;
  }

  const mb =
    kb / 1024;

  return `${mb.toFixed(
    1,
  )} MB`;
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
      year: "numeric",
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
  };


const secondaryButtonStyle:
  React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: 7,
    border:
      "1px solid #d0d5dd",
    borderRadius: 10,
    background: "#ffffff",
    color: "#344054",
    padding: "10px 14px",
    fontWeight: 600,
    cursor: "pointer",
  };


const smallButtonStyle:
  React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: 5,
    border:
      "1px solid #d0d5dd",
    borderRadius: 8,
    background: "#ffffff",
    color: "#344054",
    padding: "6px 8px",
    fontSize: 11,
    fontWeight: 600,
    cursor: "pointer",
  };
