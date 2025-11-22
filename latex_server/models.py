"""
Pydantic models for request/response validation.
"""

import base64
from typing import Dict, Union

from pydantic import BaseModel, Field, field_validator


class FileContent(BaseModel):
    """Model for a single file's content."""

    data: str = Field(..., description="File content (text or base64-encoded binary)")
    binary: bool = Field(False, description="Whether the data is base64-encoded binary")

    def get_bytes(self) -> bytes:
        """
        Get the file content as bytes.

        Returns:
            File content as bytes (decoded from base64 if binary)
        """
        if self.binary:
            return base64.b64decode(self.data)
        else:
            return self.data.encode("utf-8")


class CompilationRequest(BaseModel):
    """Request model for LaTeX compilation."""

    main: str = Field(..., description="Content of the main LaTeX file")
    files: Dict[str, Union[str, FileContent]] = Field(
        default_factory=dict, description="Additional files (path -> content mapping)"
    )

    @field_validator("files", mode="before")
    @classmethod
    def normalize_files(cls, v: Dict) -> Dict:
        """
        Normalize files dict to ensure all values are FileContent objects.

        Args:
            v: Raw files dictionary

        Returns:
            Normalized dictionary with FileContent values
        """
        if not isinstance(v, dict):
            return v

        normalized = {}
        for key, value in v.items():
            if isinstance(value, str):
                # Backward compatibility: treat strings as text content
                normalized[key] = FileContent(data=value, binary=False)
            elif isinstance(value, dict):
                # New format: dict with 'data' and 'binary' keys
                normalized[key] = FileContent(**value)
            else:
                # Already a FileContent object
                normalized[key] = value

        return normalized

    def get_all_files(self) -> Dict[str, bytes]:
        """
        Get all files including main and additional files as bytes.

        Returns:
            Dictionary mapping file paths to their content as bytes
        """
        all_files = {"main.tex": self.main.encode("utf-8")}

        # Add files from the 'files' field
        for path, content in self.files.items():
            if isinstance(content, FileContent):
                all_files[path] = content.get_bytes()
            elif isinstance(content, str):
                # Backward compatibility
                all_files[path] = content.encode("utf-8")

        return all_files


class CompilationResponse(BaseModel):
    """Response model for LaTeX compilation."""

    log: str = Field(..., description="Compilation log output")
    file: str = Field(..., description="Base64-encoded PDF file")