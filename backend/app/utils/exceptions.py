"""Custom exception classes."""


class BeatForgeException(Exception):
    """Base exception for BeatForge."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AudioAnalysisError(BeatForgeException):
    """Raised when audio analysis fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class MappingError(BeatForgeException):
    """Raised when beatmap generation fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class InvalidFileError(BeatForgeException):
    """Raised when file is invalid."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class FileTooLargeError(BeatForgeException):
    """Raised when file exceeds size limit."""

    def __init__(self, message: str):
        super().__init__(message, status_code=413)


class RateLimitError(BeatForgeException):
    """Raised when rate limit exceeded."""

    def __init__(self, message: str):
        super().__init__(message, status_code=429)
