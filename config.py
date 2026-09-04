"""
Configuration module for 1688 Sourcing Tool.
Manages provider settings, API keys, actor IDs, and operational modes.
Supports environment variables (Replit Secrets / Docker), local JSON config, and runtime toggles.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent
LOCAL_CONFIG_FILE = BASE_DIR / "config.local.json"

class AppConfig:
    def __init__(self):
        self._runtime_demo_mode_override: Optional[bool] = None
        self.reload()

    def reload(self):
        """Reload configuration from defaults, config.local.json, and environment variables."""
        # 1. Start with defaults
        self.provider_name = "apify"
        self.provider_api_key = ""
        self.actor_id = "schnellscrapers/1688-supplier-leads"
        self.provider_base_url = "https://api.apify.com/v2"
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
                    self.actor_id = data.get("actor_id", self.actor_id)
                    self.provider_base_url = data.get("provider_base_url", self.provider_base_url)
                    if "demo_mode" in data:
                        self.demo_mode = bool(data["demo_mode"])
            except Exception as e:
                print(f"[Config] Warning: Failed to parse {LOCAL_CONFIG_FILE}: {e}")

        # 3. Environment variables take highest precedence (Replit Secrets / Docker / Cloud)
        env_provider = os.environ.get("PROVIDER_NAME")
        if env_provider:
            self.provider_name = env_provider.lower().strip()

        env_key = os.environ.get("PROVIDER_API_KEY") or os.environ.get("APIFY_API_TOKEN") or os.environ.get("APIFY_TOKEN")
        if env_key is not None:
            self.provider_api_key = env_key.strip()

        env_actor = os.environ.get("ACTOR_ID") or os.environ.get("APIFY_ACTOR_ID")
        if env_actor:
            self.actor_id = env_actor.strip()

        env_base_url = os.environ.get("PROVIDER_BASE_URL")
        if env_base_url:
            self.provider_base_url = env_base_url.strip()

        # Explicit DEMO_MODE environment variable check
        env_demo = os.environ.get("DEMO_MODE")
        if env_demo is not None:
            self.demo_mode = env_demo.lower().strip() in ("true", "1", "yes")

        # 4. If runtime override was set via UI toggle, preserve it
        if self._runtime_demo_mode_override is not None:
            self.demo_mode = self._runtime_demo_mode_override

        # 5. Safety check: If no API key is available anywhere, always force demo mode
        if not self.provider_api_key.strip():
            self.demo_mode = True

        # Auto-adjust provider_name if an API key is present but provider_name was left as "demo"
        if not self.demo_mode and self.provider_api_key and self.provider_name == "demo":
            self.provider_name = "apify"

        env_host = os.environ.get("HOST")
        if env_host:
            self.host = env_host

        env_port = os.environ.get("PORT")
        if env_port:
            try:
                self.port = int(env_port)
            except ValueError:
                pass

    def set_demo_mode(self, enabled: bool) -> bool:
        """
        Sets demo mode dynamically and updates runtime override & local config file.
        Returns True on successful mode change, False if cannot disable demo mode due to missing API key.
        """
        if not enabled and not self.provider_api_key.strip():
            self._runtime_demo_mode_override = True
            self.demo_mode = True
            return False

        self._runtime_demo_mode_override = enabled
        self.demo_mode = enabled
        if LOCAL_CONFIG_FILE.exists():
            try:
                with open(LOCAL_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["demo_mode"] = enabled
                with open(LOCAL_CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"[Config] Warning: Could not update {LOCAL_CONFIG_FILE}: {e}")
        return True

    def get_public_status(self) -> Dict[str, Any]:
        """Returns safe status information without exposing raw secrets."""
        has_key = bool(self.provider_api_key.strip())
        masked_key = ""
        if has_key:
            if len(self.provider_api_key) > 8:
                masked_key = f"{self.provider_api_key[:8]}...{self.provider_api_key[-4:]}"
            else:
                masked_key = "***"

        active_provider = "demo" if self.demo_mode or not has_key else self.provider_name

        if self.demo_mode:
            status_label = "Demo Mode (Realistic Mock Data)"
            reason = "Demo Mode is enabled. Using built-in realistic sample data." if has_key else "No API key configured. Using built-in sample data."
        else:
            status_label = f"Live Mode (Apify 1688 Scraper: {self.actor_id})"
            reason = f"Connected to Apify Actor '{self.actor_id}' at {self.provider_base_url}"

        return {
            "demo_mode": self.demo_mode,
            "provider_name": active_provider,
            "configured_provider": self.provider_name,
            "actor_id": self.actor_id,
            "has_api_key": has_key,
            "masked_api_key": masked_key,
            "base_url": self.provider_base_url if not self.demo_mode else "",
            "status_label": status_label,
            "status_reason": reason
        }

# Global singleton configuration
config = AppConfig()
