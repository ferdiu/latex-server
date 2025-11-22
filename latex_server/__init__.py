"""
LaTeX Compilation Server

A FastAPI-based HTTP server for compiling LaTeX documents to PDF.
"""

__version__ = "1.0.0"
__author__ = "Federico Manzella"
__email__ = "ferdiu.manzella@gmail.com"

from latex_server.app import app
from latex_server.compiler import LaTeXCompiler
from latex_server.models import CompilationRequest, CompilationResponse
from latex_server.latex_watch import LatexWatcher, LatexIgnore

__all__ = [
    "app",
    "LaTeXCompiler",
    "CompilationRequest",
    "CompilationResponse",
    "LatexWatcher",
    "LatexIgnore",
]
