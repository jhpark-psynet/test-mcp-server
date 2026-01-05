"""League configuration loader module."""
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Cache for loaded league configs
_league_cache: Dict[str, Dict[str, str]] = {}

# Path to league config files
CONFIG_DIR = Path(__file__).parent / "config"


def load_league_config(sport: str) -> Dict[str, str]:
    """Load league ID mapping from JSON config file.

    Args:
        sport: Sport name (e.g., 'soccer', 'basketball')

    Returns:
        Dictionary mapping league names to league IDs
    """
    # Return from cache if available
    if sport in _league_cache:
        return _league_cache[sport]

    config_path = CONFIG_DIR / f"{sport}.json"

    if not config_path.exists():
        logger.warning(f"League config not found: {config_path}")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        leagues = config.get("leagues", {})
        version = config.get("version", "unknown")

        # Cache the result
        _league_cache[sport] = leagues

        logger.info(f"Loaded {len(leagues)} leagues for {sport} (version: {version})")
        return leagues

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {config_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load league config for {sport}: {e}")
        return {}


def get_league_id(sport: str, league_name: str) -> Optional[str]:
    """Get league ID by sport and league name.

    Args:
        sport: Sport name
        league_name: League display name

    Returns:
        League ID or None if not found
    """
    leagues = load_league_config(sport)
    return leagues.get(league_name)


def reload_league_config(sport: Optional[str] = None) -> None:
    """Reload league config from file, clearing cache.

    Args:
        sport: Specific sport to reload, or None to reload all
    """
    if sport:
        _league_cache.pop(sport, None)
        load_league_config(sport)
    else:
        _league_cache.clear()
        # Reload all known sports
        for config_file in CONFIG_DIR.glob("*.json"):
            sport_name = config_file.stem
            load_league_config(sport_name)
