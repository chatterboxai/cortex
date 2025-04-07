"""Default settings loader for chatbots."""
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_default_chatbot_settings_dict() -> dict:
    """
    Load default chatbot settings from the YAML configuration file as a dict.
    
    Returns:
        dict: Default settings as a dictionary
    """
    config_path = Path(__file__).parent / "default_chatbot_settings.yaml"
    logger.debug(f'Loading default chatbot settings from {config_path}')
    
    # Fallback default settings
    default_settings = {
        "embedding_model": {
            "provider": "openai",
            "name": "text-embedding-3-large",
            "dimensions": 3072
        }
    }
    
    try:
        with open(config_path, "r") as file:
            settings_dict = yaml.safe_load(file) or {}
            logger.debug(f'Settings dictionary: {settings_dict}')
            return settings_dict
    except Exception as e:
        logger.warning(
            f'Exception loading default settings file at {config_path}. '
            f'Error: {str(e)}. Using fallback settings.'
        )
        return default_settings 