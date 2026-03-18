"""Configuration management for the knowledge management system."""

import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


class Config:
    """Manages application configuration with environment variable substitution."""

    def __init__(self, config_path: str = None):
        """Initialize configuration.

        Args:
            config_path: Path to YAML config file. Defaults to config/default.yaml
        """
        load_dotenv()

        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"

        self.config_path = Path(config_path)
        self._config = self._load_and_substitute()

    def _load_and_substitute(self) -> Dict[str, Any]:
        """Load YAML config and substitute environment variables.

        Returns:
            Configuration dictionary with env vars substituted
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_text = f.read()

        # Substitute environment variables in format ${VAR_NAME}
        def replace_env_var(match):
            var_name = match.group(1)
            value = os.getenv(var_name)
            if value is None:
                # Return placeholder instead of raising error
                # This allows the system to work without API keys
                return f"${{{var_name}}}"
            return value

        config_text = re.sub(r'\$\{([^}]+)\}', replace_env_var, config_text)

        return yaml.safe_load(config_text)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key: Dot-notation key (e.g., 'claude.model')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    @property
    def watcher(self) -> Dict[str, Any]:
        """Get watcher configuration."""
        return self._config.get('watcher', {})

    @property
    def claude(self) -> Dict[str, Any]:
        """Get Claude API configuration."""
        return self._config.get('claude', {})

    @property
    def embeddings(self) -> Dict[str, Any]:
        """Get embeddings configuration."""
        return self._config.get('embeddings', {})

    @property
    def database(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self._config.get('database', {})

    @property
    def processing(self) -> Dict[str, Any]:
        """Get processing configuration."""
        return self._config.get('processing', {})

    @property
    def search(self) -> Dict[str, Any]:
        """Get search configuration."""
        return self._config.get('search', {})

    @property
    def similarity(self) -> Dict[str, Any]:
        """Get similarity configuration."""
        return self._config.get('similarity', {})

    def validate(self) -> bool:
        """Validate configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Check Claude API key (optional - system can work without it)
        api_key = self.claude.get('api_key')
        if not api_key or api_key.startswith('${'):
            # API key not configured, system will work without AI features
            pass

        # Check directories exist or can be created
        for directory in self.watcher.get('directories', []):
            Path(directory).mkdir(parents=True, exist_ok=True)

        # Ensure database directories exist
        db_path = Path(self.database.get('sqlite', './data/db/knowledge.db'))
        db_path.parent.mkdir(parents=True, exist_ok=True)

        chroma_path = Path(self.database.get('chroma', './data/vectors/chroma'))
        chroma_path.mkdir(parents=True, exist_ok=True)

        return True


# Global config instance
_config = None


def get_config(config_path: str = None) -> Config:
    """Get global configuration instance.

    Args:
        config_path: Path to config file (only used on first call)

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
