from dataclasses import dataclass

import fitz


class PDFExtractionError(Exception):
    pass


class EmptyPDFError(Exception):
    pass


@dataclass
class ExtractedPage:
    page_number: int
    text: str


def extract_pdf_pages(
    file_path: str,
) -> list[ExtractedPage]:
    try:
        document = fitz.open(file_path)
    except Exception as exc:
        raise PDFExtractionError(
            "Unable to open PDF document"
        ) from exc

    pages: list[ExtractedPage] = []

    try:
        for index, page in enumerate(
            document,
            start=1,
        ):
            text = page.get_text(
                "text",
            ).strip()

            if not text:
                continue

            pages.append(
                ExtractedPage(
                    page_number=index,
                    text=text,
                )
            )
    except Exception as exc:
        raise PDFExtractionError(
            "Unable to extract text from PDF"
        ) from exc

    finally:
        document.close()

    if not pages:
        raise EmptyPDFError(
            "PDF contains no extractable text"
        )

    return pages
