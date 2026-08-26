"""Universal download infrastructure.

Sprint 3 contains task orchestration only. It does not perform network
downloads and does not know anything about OPENLANE.
"""

from src.core.download.checksum import calculate_crc32, calculate_md5, calculate_sha256
from src.core.download.events import DownloadEvent, DownloadEventType
from src.core.download.manager import DownloadManager
from src.core.download.models import DownloadJob, DownloadResult, DownloadStatus
from src.core.download.progress import DownloadProgress
from src.core.download.queue import DownloadQueue
from src.core.download.retry import RetryPolicy

__all__ = [
    "DownloadEvent",
    "DownloadEventType",
    "DownloadJob",
    "DownloadManager",
    "DownloadProgress",
    "DownloadQueue",
    "DownloadResult",
    "DownloadStatus",
    "RetryPolicy",
    "calculate_crc32",
    "calculate_md5",
    "calculate_sha256",
]

