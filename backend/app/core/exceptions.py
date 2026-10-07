"""Application exceptions with HTTP status mapping."""


class AppError(Exception):
    status_code = 500
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UnsupportedFileTypeError(AppError):
    status_code = 400


class FileTooLargeError(AppError):
    status_code = 413


class DocumentNotFoundError(AppError):
    status_code = 404


class ExtractionError(AppError):
    status_code = 422


class IndexingError(AppError):
    status_code = 500


class LLMError(AppError):
    status_code = 502


class EmbeddingError(AppError):
    status_code = 500
