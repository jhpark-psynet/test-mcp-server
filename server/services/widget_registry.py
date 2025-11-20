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
    game_stats_html = load_widget_html("game-stats", str(cfg.assets_dir))
    game_result_viewer_html = load_widget_html("game-result-viewer", str(cfg.assets_dir))

    return [
        Widget(
            identifier="example-widget",
            title="Example Widget",
            template_uri="ui://widget/example.html",
            html=example_html,
        ),
        Widget(
            identifier="game-stats-widget",
            title="Game Stats Widget",
            template_uri="ui://widget/game-stats.html",
            html=game_stats_html,
        ),
        Widget(
            identifier="game-result-viewer",
            title="Game Result Viewer",
            template_uri="ui://widget/game-result-viewer.html",
            html=game_result_viewer_html,
        )
    ]
