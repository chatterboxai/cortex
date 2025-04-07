"""Utilities for managing application settings."""
import yaml
from pathlib import Path
import logging
from app.schemas.chatbot_settings import ChatbotSettings, EmbeddingModel
from typing import Any
logger = logging.getLogger(__name__)


def load_default_chatbot_settings() -> ChatbotSettings:
    """
    Load default chatbot settings from the YAML configuration file as a dict.
    
    Returns:
        ChatbotSettings: Default settings as a ChatbotSettings object
    """
    config_path = Path(__file__).parent / "default_chatbot_settings.yaml"
    logger.debug(f'Loading default chatbot settings from {config_path}')
    
    # Fallback default settings
    default_settings = ChatbotSettings(
        embedding_model=EmbeddingModel(
            provider="openai",
            name="text-embedding-3-large",
            dimensions=3072
        )
    )
    
    try:
        with open(config_path, "r") as file:
            settings_dict = yaml.safe_load(file) or {}
            logger.debug(f'Settings dictionary: {settings_dict}')
            # Convert dict to ChatbotSettings object
            return ChatbotSettings.model_validate(settings_dict)
    except Exception as e:
        logger.warning(
            f'Exception loading default settings file at {config_path}. '
            f'Error: {str(e)}. Using fallback settings.'
        )
        return default_settings


def load_default_chatbot_settings_dict() -> dict[str, Any]:
    """
    Load default chatbot settings from the YAML configuration file as a dict.
    
    Returns:
        dict: Default settings as a dictionary
    """
    return load_default_chatbot_settings().model_dump()