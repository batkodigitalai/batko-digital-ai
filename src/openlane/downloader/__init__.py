"""OPENLANE page snapshot downloader MVP.

Sprint 4 captures already-open Playwright pages. It does not login, parse
business data, download assets, or perform network capture.
"""

from src.openlane.downloader.downloader import OpenLaneDownloader
from src.openlane.downloader.models import PageMetadata, PageSnapshot

__all__ = ["OpenLaneDownloader", "PageMetadata", "PageSnapshot"]

