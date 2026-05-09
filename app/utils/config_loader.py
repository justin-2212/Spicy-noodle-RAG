import json
from pathlib import Path
from typing import Any, Dict
from app.utils.logger import logger

# Constants for config
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "ai-config.json"

DEFAULT_SYSTEM_PROMPT = """You are a helpful spicy noodle (mì cay) recommendation assistant for a spicy noodle restaurant.
You help customers find spicy noodle dishes that match their preferences, dietary requirements, and budget.
Always be friendly, professional, and provide personalized recommendations based on the available menu items.

When providing recommendations:
1. Consider the user's dietary preferences and restrictions
2. Suggest spicy noodle items within their budget
3. Explain why each recommendation is suitable
4. Ask follow-up questions if needed for better recommendations
5. Be specific about prices and availability
"""

def load_config() -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Returns:
        Dict containing configuration.
    """
    if not CONFIG_FILE.exists():
        logger.warning(f"Config file not found at {CONFIG_FILE}. Using defaults.")
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {CONFIG_FILE}: {e}. Using defaults.")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error reading {CONFIG_FILE}: {e}. Using defaults.")
        return {}

def load_system_prompt() -> str:
    """
    Load system prompt from config or use default.
    
    Returns:
        System prompt string.
    """
    config = load_config()
    return config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
