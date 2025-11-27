"""MCP server entry point."""
import logging

from server.config import CONFIG
from server.logging_config import setup_logging
from server.factory import create_app

# Setup logging
setup_logging(CONFIG.log_level, CONFIG.log_file if CONFIG.log_file else None)
logger = logging.getLogger(__name__)

# Log startup configuration
logger.info(f"Starting {CONFIG.app_name}")
logger.info(f"  Environment: {CONFIG.environment}")
logger.info(f"  Host: {CONFIG.host}:{CONFIG.port}")
logger.info(f"  Log level: {CONFIG.log_level}")
logger.info(f"  Log file: {CONFIG.log_file if CONFIG.log_file else '✗ Disabled'}")
logger.info(f"  Assets dir: {CONFIG.assets_dir}")
logger.info(f"  External API: {'✓ Configured' if CONFIG.has_external_api else '✗ Not configured'}")
logger.info(f"  Sports API: {'✓ Real API' if CONFIG.use_real_sports_api else '✓ Mock data' if CONFIG.use_mock_sports_data else '✗ Not configured'}")

# Create ASGI app
app = create_app(CONFIG)

# Uvicorn entry point
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {CONFIG.host}:{CONFIG.port}")
    uvicorn.run(
        "server.main:app",
        host=CONFIG.host,
        port=CONFIG.port,
        reload=True,
    )
