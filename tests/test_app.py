"""
Unit tests for the LaTeX Compilation Server.

Run with: pytest -v
"""

import base64

import pytest
from fastapi.testclient import TestClient

from latex_server.app import app
from latex_server.compiler import LaTeXCompiler
from latex_server.models import CompilationRequest


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def compiler() -> LaTeXCompiler:
    """Create a LaTeXCompiler instance."""
    return LaTeXCompiler()


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test the root health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data


class TestCompilationRequest:
    """Tests for the compilation request model."""

    def test_simple_document_compilation(self, client: TestClient) -> None:
        """Test compilation of a simple LaTeX document."""
        latex_content = r"""
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
"""

        response = client.post("/compile", json={"main": latex_content})

        assert response.status_code == 200
        data = response.json()
        assert "log" in data
        assert "file" in data
        assert len(data["file"]) > 0  # PDF should be generated

        # Verify it's valid base64
        pdf_bytes = base64.b64decode(data["file"])
        assert pdf_bytes.startswith(b"%PDF")  # PDF magic number

    def test_document_with_additional_files(self, client: TestClient) -> None:
        """Test compilation with additional files."""
        main_content = r"""
\documentclass{article}
\begin{document}
\input{content.tex}
\end{document}
"""

        content_file = r"""
This is content from another file.
"""

        response = client.post(
            "/compile", json={"main": main_content, "files": {"content.tex": content_file}}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["file"]) > 0


    def test_document_with_additional_file_in_subdir(self, client: TestClient) -> None:
        """Test compilation with additional files in a subdirectory."""
        main_content = r"""
\documentclass{article}
\begin{document}
\input{subdir/content.tex}
\end{document}
"""

        content_file = r"""
This is content from another file.
"""

        response = client.post(
            "/compile", json={"main": main_content, "files": {"subdir/content.tex": content_file}}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["file"]) > 0

    def test_document_with_toc(self, client: TestClient) -> None:
        """Test compilation with table of contents (requires multiple passes)."""
        latex_content = r"""
\documentclass{article}
\begin{document}
\tableofcontents
\section{Introduction}
This is the introduction.
\section{Conclusion}
This is the conclusion.
\end{document}
"""

        response = client.post("/compile", json={"main": latex_content})

        assert response.status_code == 200
        data = response.json()
        assert len(data["file"]) > 0

        # Check that multiple passes were performed
        assert "pass 2" in data["log"].lower() or "compilation pass 2" in data["log"]

    def test_document_with_bibliography(self, client: TestClient) -> None:
        """Test compilation with bibliography."""
        main_content = r"""
\documentclass{article}
\begin{document}
This is a citation \cite{example}.
\bibliographystyle{plain}
\bibliography{refs}
\end{document}
"""

        bib_content = r"""
@article{example,
  author = {John Doe},
  title = {An Example Article},
  journal = {Journal of Examples},
  year = {2024}
}
"""

        response = client.post("/compile", json={"main": main_content, "refs.bib": bib_content})

        assert response.status_code == 200
        data = response.json()
        assert len(data["file"]) > 0

        # Check that BibTeX was run
        assert "bibtex" in data["log"].lower()

    def test_invalid_latex_document(self, client: TestClient) -> None:
        """Test compilation of invalid LaTeX document."""
        latex_content = r"""
\documentclass{article}
\begin{document}
\invalid_command
\end{document}
"""

        response = client.post("/compile", json={"main": latex_content})

        # Should return 200 with empty PDF and error log
        assert response.status_code == 200
        data = response.json()
        assert "log" in data
        assert data["file"] == ""  # No PDF generated

    def test_missing_main_field(self, client: TestClient) -> None:
        """Test request without main field."""
        response = client.post("/compile", json={"other.tex": "content"})

        assert response.status_code == 422  # Validation error


class TestLaTeXCompiler:
    """Tests for the LaTeXCompiler class."""

    def test_needs_bibtex_detection(self, compiler: LaTeXCompiler) -> None:
        """Test detection of BibTeX requirement."""
        log_with_citation = "LaTeX Warning: Citation `example' on page 1 undefined"
        assert compiler._needs_bibtex(log_with_citation)

        log_without_citation = "PDF generated successfully"
        assert not compiler._needs_bibtex(log_without_citation)

    def test_needs_rerun_detection(self, compiler: LaTeXCompiler) -> None:
        """Test detection of rerun requirement."""
        log_with_rerun = (
            "LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right."
        )
        assert compiler._needs_rerun(log_with_rerun)

        log_without_rerun = "PDF generated successfully"
        assert not compiler._needs_rerun(log_without_rerun)

    def test_compile_simple_document(self, compiler: LaTeXCompiler) -> None:
        """Test compilation of a simple document."""
        files = {
            "main.tex": r"""
\documentclass{article}
\begin{document}
Test document.
\end{document}
"""
        }

        pdf_bytes, log = compiler.compile(files)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")
        assert "main.tex" in log or "LaTeX" in log

    def test_compile_without_main_tex(self, compiler: LaTeXCompiler) -> None:
        """Test compilation without main.tex file."""
        files = {"other.tex": "content"}

        with pytest.raises(ValueError, match="main.tex must be provided"):
            compiler.compile(files)

    def test_compile_with_subdirectory(self, compiler: LaTeXCompiler) -> None:
        """Test compilation with files in subdirectories."""
        files = {
            "main.tex": r"""
\documentclass{article}
\begin{document}
\input{chapters/chapter1.tex}
\end{document}
""",
            "chapters/chapter1.tex": r"""
\section{Chapter 1}
This is chapter 1.
""",
        }

        pdf_bytes, log = compiler.compile(files)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0


class TestRequestModel:
    """Tests for the request model flexibility."""

    def test_get_all_files_with_main_only(self) -> None:
        """Test getting files with only main field."""
        request = CompilationRequest(main="content")
        files = request.get_all_files()

        assert "main.tex" in files
        assert files["main.tex"] == "content"

    def test_get_all_files_with_additional_fields(self) -> None:
        """Test getting files with additional fields."""
        request = CompilationRequest(
            main="main content", files={"file1.tex": "content1", "file2.tex": "content2"}
        )
        files = request.get_all_files()

        assert "main.tex" in files
        assert "file1.tex" in files
        assert "file2.tex" in files


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_document(self, client: TestClient) -> None:
        """Test compilation of empty document."""
        response = client.post("/compile", json={"main": ""})

        assert response.status_code == 200
        data = response.json()
        assert "log" in data
        # Empty document likely won't compile
        assert data["file"] == ""

    def test_very_large_document(self, client: TestClient) -> None:
        """Test compilation of a document with many sections."""
        sections = "\n".join(
            [f"\\section{{Section {i}}}\nContent for section {i}." for i in range(50)]
        )

        latex_content = f"""
\\documentclass{{article}}
\\begin{{document}}
\\tableofcontents
{sections}
\\end{{document}}
"""

        response = client.post("/compile", json={"main": latex_content})

        assert response.status_code == 200
        data = response.json()
        assert len(data["file"]) > 0

    def test_unicode_content(self, client: TestClient) -> None:
        """Test compilation with Unicode characters."""
        latex_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\begin{document}
Héllo Wörld! 你好世界
\end{document}
"""

        response = client.post("/compile", json={"main": latex_content})

        assert response.status_code == 200
        data = response.json()
        # May or may not compile depending on LaTeX setup
        assert "log" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])