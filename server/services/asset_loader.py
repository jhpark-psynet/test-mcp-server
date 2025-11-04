"""위젯 HTML 자산 로딩."""
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def load_widget_html(component_name: str, assets_dir_str: str) -> str:
    """Load widget HTML from assets directory (with hashed-filename fallback).

    Args:
        component_name: Widget component name (e.g., 'example', 'api-result')
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

    html_path = assets_dir / f"{component_name}.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf8")

    # Try with hash suffix (e.g., my-app-a1b2.html)
    fallback_candidates = sorted(assets_dir.glob(f"{component_name}-*.html"))
    if fallback_candidates:
        return fallback_candidates[-1].read_text(encoding="utf8")

    raise FileNotFoundError(
        f"Widget HTML not found: {html_path}. "
        "Run `npm run build` to generate widget assets."
    )
