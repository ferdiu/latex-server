"""
FastAPI application for LaTeX compilation service.
"""

import base64
import logging

from fastapi import FastAPI, HTTPException

from latex_server import __version__
from latex_server.compiler import LaTeXCompiler
from latex_server.config import settings
from latex_server.models import CompilationRequest, CompilationResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LaTeX Compilation Server",
    description="Compile LaTeX documents to PDF with support for bibliographies and table of contents",
    version=__version__,
)

# Global compiler instance
compiler = LaTeXCompiler()


@app.get("/")
async def root() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Service status information
    """
    return {
        "status": "ok",
        "service": "LaTeX Compilation Server",
        "version": __version__,
    }


@app.post("/compile", response_model=CompilationResponse)
async def compile_latex(request: CompilationRequest) -> CompilationResponse:
    """
    Compile a LaTeX document to PDF.

    The request should include:
    - main: Content of the main LaTeX file
    - Additional fields for other files (path -> content)

    Returns:
        CompilationResponse with log and base64-encoded PDF

    Raises:
        HTTPException: On validation or compilation errors
    """
    try:
        # Get all files from request
        files = request.get_all_files()
        logger.info(f"Received compilation request with {len(files)} file(s)")

        # Compile the document
        pdf_bytes, log = compiler.compile(files)

        # Encode PDF to base64 (empty string if compilation failed)
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8") if pdf_bytes else ""

        if not pdf_bytes:
            logger.error("Compilation failed to produce PDF")

        return CompilationResponse(log=log, file=pdf_base64)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during compilation: {e}")
        raise HTTPException(status_code=500, detail=f"Compilation error: {str(e)}")