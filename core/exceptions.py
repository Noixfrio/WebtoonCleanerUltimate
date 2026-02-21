class MangaCleanerError(Exception):
    """Base exception for all project-specific errors."""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class InvalidImageError(MangaCleanerError):
    """Raised when the input is not a valid image array or format."""
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_IMAGE")

class MemoryLimitExceededError(MangaCleanerError):
    """Raised when estimated memory usage exceeds safety thresholds."""
    def __init__(self, message: str):
        super().__init__(message, error_code="MEMORY_LIMIT_EXCEEDED")

class OCRInitializationError(MangaCleanerError):
    """Raised when the OCR engine fails to start."""
    def __init__(self, message: str):
        super().__init__(message, error_code="OCR_INIT_FAILED")

class OCRFailureError(MangaCleanerError):
    """Raised when a specific OCR operation fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="OCR_PROCESS_FAILED")

class InpaintServiceError(MangaCleanerError):
    """Raised when the inpainting service (LaMa) returns an error."""
    def __init__(self, message: str, error_code: str = "INPAINT_SERVICE_ERROR"):
        super().__init__(message, error_code=error_code)

class InpaintTimeoutError(InpaintServiceError):
    """Raised when the inpainting service times out."""
    def __init__(self, message: str):
        super().__init__(message, error_code="INPAINT_TIMEOUT")

class TileSeamError(MangaCleanerError):
    """Raised when a tile merge results in visible seam artifacts."""
    def __init__(self, message: str):
        super().__init__(message, error_code="TILE_SEAM_ERROR")

class MaskAlignmentError(MangaCleanerError):
    """Raised when mask and image dimensions or formats mismatch."""
    def __init__(self, message: str):
        super().__init__(message, error_code="MASK_ALIGNMENT_ERROR")
