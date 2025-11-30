"""위젯 레지스트리."""
import logging
from typing import List

from server.config import Config
from server.models import Widget

logger = logging.getLogger(__name__)


def build_widgets(cfg: Config) -> List[Widget]:
    """Build list of available widgets.

    Note: HTML is not loaded here anymore. It's loaded fresh from disk
    each time via embedded_widget_resource() to support hot reload.

    Using simple widget names without hashing for easier development.

    Args:
        cfg: Server configuration

    Returns:
        List of Widget instances
    """
    widgets = []

    # Define base widgets with their names
    widget_definitions = [
        ("example", "Example Widget"),
        ("game-result-viewer", "Game Result Viewer"),
    ]

    for base_name, title in widget_definitions:
        # Use simple names without hashing
        identifier = base_name
        template_uri = f"ui://widget/{base_name}.html"
        logger.info(f"Widget '{base_name}' registered")

        widgets.append(
            Widget(
                identifier=identifier,
                title=title,
                template_uri=template_uri,
            )
        )

    return widgets
