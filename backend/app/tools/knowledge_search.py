from typing import Any

from app.services.embedding_service import (
    EmbeddingGenerationError,
)
from app.services.retrieval_service import (
    retrieve_relevant_chunks,
)
from app.tools.base import (
    BaseTool,
    ToolExecutionContext,
    ToolResult,
)


class KnowledgeSearchTool(BaseTool):
    name = "knowledge_search"

    description = (
        "Search the organization's indexed enterprise documents "
        "for information relevant to a user query."
    )

    requires_approval = False

    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict[str, Any],
    ) -> ToolResult:
        if context.db is None:
            return ToolResult(
                success=False,
                error="Database session is required",
            )

        query = str(
            arguments.get(
                "query",
                "",
            )
        ).strip()

        if not query:
            return ToolResult(
                success=False,
                error="A search query is required",
            )

        raw_limit = arguments.get(
            "limit",
            5,
        )

        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            return ToolResult(
                success=False,
                error="Search limit must be an integer",
            )

        if limit < 1 or limit > 10:
            return ToolResult(
                success=False,
                error="Search limit must be between 1 and 10",
            )

        try:
            chunks = retrieve_relevant_chunks(
                db=context.db,
                organization_id=context.organization_id,
                question=query,
                limit=limit,
            )

        except EmbeddingGenerationError as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )

        results = [
            {
                "chunk_id": str(chunk.chunk_id),
                "document_id": str(
                    chunk.document_id
                ),
                "filename": chunk.filename,
                "page_number": chunk.page_number,
                "content": chunk.content,
                "similarity_score": round(
                    chunk.similarity_score,
                    4,
                ),
            }
            for chunk in chunks
        ]

        return ToolResult(
            success=True,
            data={
                "query": query,
                "result_count": len(results),
                "results": results,
            },
            message=(
                f"Found {len(results)} relevant "
                "document chunks."
            ),
        )
