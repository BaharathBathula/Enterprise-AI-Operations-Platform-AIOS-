import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


def validate_pdf_upload(
    file: UploadFile,
) -> None:
    if file.content_type not in ALLOWED_PDF_CONTENT_TYPES:
        raise UnsupportedFileTypeError(
            "Only PDF documents are supported"
        )


async def save_uploaded_file(
    file: UploadFile,
    organization_id: uuid.UUID,
) -> tuple[str, int, str]:
    validate_pdf_upload(file)

    file_extension = Path(
        file.filename or ""
    ).suffix.lower()

    if file_extension != ".pdf":
        raise UnsupportedFileTypeError(
            "Uploaded file must have a .pdf extension"
        )

    storage_root = Path(
        settings.STORAGE_PATH
    )

    organization_directory = (
        storage_root / str(organization_id)
    )

    organization_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = (
        f"{uuid.uuid4()}.pdf"
    )

    file_path = (
        organization_directory
        / stored_filename
    )

    total_size = 0

    try:
        with file_path.open("wb") as destination:
            while chunk := await file.read(
                1024 * 1024
            ):
                total_size += len(chunk)

                if (
                    total_size
                    > MAX_FILE_SIZE_BYTES
                ):
                    raise FileTooLargeError(
                        "PDF exceeds the 20 MB upload limit"
                    )

                destination.write(chunk)

    except Exception:
        if file_path.exists():
            file_path.unlink()

        raise

    finally:
        await file.close()

    return (
        str(file_path),
        total_size,
        stored_filename,
    )
