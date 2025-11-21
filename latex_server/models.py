"""
Pydantic models for request/response validation.
"""

from typing import Dict

from pydantic import BaseModel, Field


class CompilationRequest(BaseModel):
    """Request model for LaTeX compilation."""

    main: str = Field(..., description="Content of the main LaTeX file")
    files: Dict[str, str] = Field(
        default_factory=dict, description="Additional files (path -> content mapping)", alias="files"
    )

    class Config:
        extra = "allow"  # Allow additional fields for file paths

    def get_all_files(self) -> Dict[str, str]:
        """
        Get all files including main and additional files.

        Returns:
            Dictionary mapping file paths to their content
        """
        all_files = {"main.tex": self.main}

        # Add files from the 'files' field
        all_files.update(self.files)

        # Add any additional fields that aren't 'main' or 'files'
        for key, value in self.__dict__.items():
            if key not in ("main", "files") and isinstance(value, str):
                all_files[key] = value

        return all_files


class CompilationResponse(BaseModel):
    """Response model for LaTeX compilation."""

    log: str = Field(..., description="Compilation log output")
    file: str = Field(..., description="Base64-encoded PDF file")