"""위젯 HTML 자산 로딩."""
import re
import logging
import json
from pathlib import Path
from typing import Optional, Dict
try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


def detect_widget_hash(component_name: str, base_url: str, assets_dir_str: str) -> Optional[str]:
    """Detect the hash for a widget component from manifest.json via HTTP.

    Args:
        component_name: Widget component base name (e.g., 'game-result-viewer')
        base_url: Component server base URL (e.g., 'http://localhost:4444')
        assets_dir_str: Assets directory path (fallback for local file scanning)

    Returns:
        Hash string (e.g., '4b37264f') or None if not found
    """
    # Try fetching manifest.json from component server (supports CDN deployment)
    if httpx:
        try:
            manifest_url = f"{base_url.rstrip('/')}/manifest.json"
            response = httpx.get(manifest_url, timeout=2.0)
            if response.status_code == 200:
                manifest: Dict[str, str] = response.json()
                widget_hash = manifest.get(component_name)
                if widget_hash:
                    logger.debug(f"Fetched hash for '{component_name}' from {manifest_url}: {widget_hash}")
                    return widget_hash
        except Exception as e:
            logger.debug(f"Failed to fetch manifest from {base_url}: {e}")

    # Fallback: Scan local assets directory (for backwards compatibility)
    assets_dir = Path(assets_dir_str)
    if not assets_dir.exists():
        return None

    # Look for hashed HTML files: component-name-HASH.html
    pattern = f"{component_name}-*.html"
    candidates = sorted(assets_dir.glob(pattern))

    if not candidates:
        return None

    # Extract hash from filename (e.g., 'game-result-viewer-4b37264f.html' -> '4b37264f')
    latest_file = candidates[-1]
    match = re.search(rf'{re.escape(component_name)}-([a-f0-9]+)\.html$', latest_file.name)
    if match:
        hash_value = match.group(1)
        logger.debug(f"Detected hash for '{component_name}' from local files: {hash_value}")
        return hash_value

    return None


def load_widget_html(component_name: str, assets_dir_str: str) -> str:
    """Load widget HTML from assets directory (with hashed-filename fallback).

    Args:
        component_name: Widget component name (e.g., 'example', 'game-result-viewer-4b37264f')
        assets_dir_str: Assets directory path as string

    Returns:
        Widget HTML content

    Raises:
        FileNotFoundError: If assets directory or widget HTML not found
    """
    assets_dir = Path(assets_dir_str)
    if not assets_dir.exists():
        raise FileNotFoundError(
            f"Assets directory not found: {assets_dir}. "
            "Run `npm run build` to generate the assets before starting the server."
        )

    # Remove hash suffix (e.g., 'game-result-viewer-4b37264f' -> 'game-result-viewer')
    # to find the base widget name
    # Use regex to match hash pattern: 8 hex characters at the end
    base_name = component_name
    if re.search(r'-[a-f0-9]{8}$', component_name):
        base_name = re.sub(r'-[a-f0-9]{8}$', '', component_name)

    html_path = assets_dir / f"{base_name}.html"
    if html_path.exists():
        html = html_path.read_text(encoding="utf8")
        # Log what file we're reading and snippet of content (for debugging cache issues)
        script_tag = html[html.find('<script'):html.find('</script>')] if '<script' in html else ''
        logger.info(f"Loaded {html_path.name}: {script_tag[:100]}...")
        return html

    # Try with hash suffix (e.g., my-app-a1b2.html)
    fallback_candidates = sorted(assets_dir.glob(f"{base_name}-*.html"))
    if fallback_candidates:
        return fallback_candidates[-1].read_text(encoding="utf8")

    raise FileNotFoundError(
        f"Widget HTML not found: {html_path}. "
        "Run `npm run build` to generate widget assets."
    )
