"""위젯 HTML 자산 로딩."""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_widget_html(component_name: str, assets_dir_str: str) -> str:
    """Load widget HTML from assets directory.

    Args:
        component_name: Widget component name (e.g., 'example', 'game-result-viewer')
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
        html = html_path.read_text(encoding="utf8")
        logger.info(f"Loaded {html_path.name}")
        return html

    raise FileNotFoundError(
        f"Widget HTML not found: {html_path}. "
        "Run `npm run build` to generate widget assets."
    )
