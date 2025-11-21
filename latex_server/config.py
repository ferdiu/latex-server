"""
Configuration management for LaTeX Compilation Server.
"""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        self.host: str = os.getenv("LATEX_SERVER_HOST", "0.0.0.0")
        self.port: int = int(os.getenv("LATEX_SERVER_PORT", "9080"))
        self.log_level: str = os.getenv("LATEX_SERVER_LOG_LEVEL", "INFO")
        self.max_compilations: int = int(os.getenv("LATEX_SERVER_MAX_COMPILATIONS", "5"))
        self.command_timeout: int = int(os.getenv("LATEX_SERVER_COMMAND_TIMEOUT", "60"))
        self.latex_command: str = os.getenv("LATEX_SERVER_LATEX_COMMAND", "pdflatex")
        self.bibtex_command: str = os.getenv("LATEX_SERVER_BIBTEX_COMMAND", "bibtex")

    def get_latex_args(self) -> list[str]:
        """Get default LaTeX compilation arguments."""
        return ["-interaction=nonstopmode", "-halt-on-error"]


# Global settings instance
settings = Settings()
