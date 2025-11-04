"""위젯 레지스트리."""
from typing import List

from server.config import Config
from server.models import Widget
from server.services.asset_loader import load_widget_html


def build_widgets(cfg: Config) -> List[Widget]:
    """Build list of available widgets.

    Args:
        cfg: Server configuration

    Returns:
        List of Widget instances
    """
    example_html = load_widget_html("example", str(cfg.assets_dir))
    api_result_html = load_widget_html("api-result", str(cfg.assets_dir))

    return [
        Widget(
            identifier="example-widget",
            title="Example Widget",
            template_uri="ui://widget/example.html",
            html=example_html,
        ),
        Widget(
            identifier="api-result-widget",
            title="API Result Widget",
            template_uri="ui://widget/api-result.html",
            html=api_result_html,
        )
    ]
