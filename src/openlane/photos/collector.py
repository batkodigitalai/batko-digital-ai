"""Collect photo URLs from an already-open OPENLANE auction page."""

from __future__ import annotations

from src.core.logging import get_logger

logger = get_logger(__name__)


class PhotoCollector:
    """Find unique gallery photo URLs in the current page DOM."""

    def collect(self, page) -> list[str]:
        """Return unique absolute photo URLs while preserving DOM order."""
        raw_urls = page.evaluate(self._script())
        unique: list[str] = []
        seen: set[str] = set()
        for url in raw_urls or []:
            if not url or url in seen:
                continue
            seen.add(url)
            unique.append(url)
        logger.info("Collected {} unique photo URLs", len(unique))
        return unique

    @staticmethod
    def _script() -> str:
        return """
        () => {
          const urls = [];
          const add = (value) => {
            if (!value) return;
            const trimmed = String(value).trim();
            if (!trimmed || trimmed.startsWith('javascript:')) return;
            try {
              urls.push(new URL(trimmed, document.baseURI).href);
            } catch (_) {}
          };
          const addSrcset = (value) => {
            if (!value) return;
            String(value).split(',').forEach((part) => add(part.trim().split(/\\s+/)[0]));
          };
          const gallerySelectors = [
            '[data-openlane-gallery]',
            '[data-photo-gallery]',
            '[data-gallery]',
            '.gallery',
            '.photo-gallery',
            '.vehicle-gallery'
          ];
          const roots = gallerySelectors.flatMap((selector) => Array.from(document.querySelectorAll(selector)));
          if (!roots.length) roots.push(document);
          roots.forEach((root) => {
            root.querySelectorAll('img').forEach((img) => {
              add(img.getAttribute('data-full'));
              add(img.getAttribute('data-large'));
              add(img.getAttribute('data-src'));
              add(img.getAttribute('src'));
              addSrcset(img.getAttribute('srcset'));
            });
            root.querySelectorAll('a[href]').forEach((link) => {
              const href = link.getAttribute('href');
              if (/\\.(jpe?g|png|webp)(\\?|#|$)/i.test(href || '')) add(href);
            });
          });
          return urls;
        }
        """
