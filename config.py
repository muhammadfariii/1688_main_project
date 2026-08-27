"""
Configuration module for 1688 Sourcing Tool.
Manages provider settings, API keys, and operational modes.
Supports environment variables (Replit Secrets) with fallback to local JSON.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent
LOCAL_CONFIG_FILE = BASE_DIR / "config.local.json"

class AppConfig:
    def __init__(self):
        self._load_config()

    def _load_config(self):
        # 1. Start with defaults
        self.provider_name = "demo"
        self.provider_api_key = ""
        self.provider_base_url = ""
        self.demo_mode = True
        self.host = "0.0.0.0"
        self.port = int(os.environ.get("PORT", 8000))
        self.default_page_size = 20

        # 2. Check local config file if present
        if LOCAL_CONFIG_FILE.exists():
            try:
                with open(LOCAL_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.provider_name = data.get("provider_name", self.provider_name)
                    self.provider_api_key = data.get("provider_api_key", self.provider_api_key)
                    self.provider_base_url = data.get("provider_base_url", self.provider_base_url)
                    if "demo_mode" in data:
                        self.demo_mode = bool(data["demo_mode"])
            except Exception as e:
                print(f"[Config] Warning: Failed to parse {LOCAL_CONFIG_FILE}: {e}")

        # 3. Environment variables take highest precedence (Replit Secrets / Docker / Cloud)
        env_provider = os.environ.get("PROVIDER_NAME")
        if env_provider:
            self.provider_name = env_provider.lower()

        env_key = os.environ.get("PROVIDER_API_KEY") or os.environ.get("PARSEBOT_API_KEY")
        if env_key:
            self.provider_api_key = env_key

        env_base_url = os.environ.get("PROVIDER_BASE_URL")
        if env_base_url:
            self.provider_base_url = env_base_url

        env_demo = os.environ.get("DEMO_MODE")
        if env_demo is not None:
            self.demo_mode = env_demo.lower() in ("true", "1", "yes")
        elif not self.provider_api_key:
            # Auto-enable demo mode if no API key is provided
            self.demo_mode = True
        else:
            self.demo_mode = False

        env_host = os.environ.get("HOST")
        if env_host:
            self.host = env_host

        env_port = os.environ.get("PORT")
        if env_port:
            try:
                self.port = int(env_port)
            except ValueError:
                pass

    def get_public_status(self) -> Dict[str, Any]:
        """Returns safe status information without exposing raw secrets."""
        has_key = bool(self.provider_api_key.strip())
        masked_key = ""
        if has_key:
            masked_key = f"{self.provider_api_key[:4]}...{self.provider_api_key[-4:]}" if len(self.provider_api_key) > 8 else "***"

        return {
            "demo_mode": self.demo_mode,
            "provider_name": self.provider_name if not self.demo_mode else "demo",
            "has_api_key": has_key,
            "masked_api_key": masked_key,
            "status_label": "Demo Mode (Realistic Mock Data)" if self.demo_mode else f"Live Mode ({self.provider_name.title()})"
        }

# Global singleton configuration
config = AppConfig()
