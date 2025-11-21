"""
LaTeX compilation logic with support for multiple passes and BibTeX.
"""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from latex_server.config import settings

logger = logging.getLogger(__name__)


class LaTeXCompiler:
    """Handles LaTeX document compilation with multiple passes."""

    def __init__(
        self,
        latex_command: Optional[str] = None,
        bibtex_command: Optional[str] = None,
        max_compilations: Optional[int] = None,
        command_timeout: Optional[int] = None,
    ) -> None:
        """
        Initialize the LaTeX compiler.

        Args:
            latex_command: LaTeX compilation command (default: from settings)
            bibtex_command: BibTeX compilation command (default: from settings)
            max_compilations: Maximum number of compilation passes (default: from settings)
            command_timeout: Command timeout in seconds (default: from settings)
        """
        self.latex_command = latex_command or settings.latex_command
        self.bibtex_command = bibtex_command or settings.bibtex_command
        self.max_compilations = max_compilations or settings.max_compilations
        self.command_timeout = command_timeout or settings.command_timeout

    def _run_command(
        self, command: list[str], cwd: Path, timeout: Optional[int] = None
    ) -> Tuple[int, str, str]:
        """
        Run a shell command and return exit code, stdout, and stderr.

        Args:
            command: Command and arguments as a list
            cwd: Working directory
            timeout: Command timeout in seconds (uses instance default if None)

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        timeout = timeout or self.command_timeout
        try:
            result = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return -1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return -1, "", str(e)

    def _needs_bibtex(self, log_content: str) -> bool:
        """
        Check if BibTeX compilation is needed.

        Args:
            log_content: LaTeX compilation log content

        Returns:
            True if BibTeX should be run
        """
        indicators = [
            "Citation",
            "There were undefined references",
            "Please (re)run Biber on the file",
            "Please (re)run BibTeX on the file",
        ]
        return any(indicator in log_content for indicator in indicators)

    def _needs_rerun(self, log_content: str) -> bool:
        """
        Check if another LaTeX pass is needed.

        Args:
            log_content: LaTeX compilation log content

        Returns:
            True if another pass is needed
        """
        indicators = [
            "Rerun to get cross-references right",
            "Label(s) may have changed",
            "Rerun LaTeX",
            "Table widths have changed. Rerun LaTeX",
            "No file main.aux.",
            "No file main.toc.",
        ]
        return any(indicator in log_content for indicator in indicators)

    def _compile_latex(self, work_dir: Path) -> Tuple[int, str]:
        """
        Run pdflatex compilation.

        Args:
            work_dir: Working directory containing LaTeX files

        Returns:
            Tuple of (exit_code, log_content)
        """
        command = [self.latex_command] + settings.get_latex_args() + ["main.tex"]

        exit_code, stdout, stderr = self._run_command(command, work_dir)
        log_content = stdout + "\n" + stderr

        return exit_code, log_content

    def _compile_bibtex(self, work_dir: Path) -> Tuple[int, str]:
        """
        Run bibtex compilation.

        Args:
            work_dir: Working directory containing LaTeX files

        Returns:
            Tuple of (exit_code, log_content)
        """
        command = [self.bibtex_command, "main"]

        exit_code, stdout, stderr = self._run_command(command, work_dir)
        log_content = stdout + "\n" + stderr

        return exit_code, log_content

    def compile(self, files: Dict[str, str]) -> Tuple[Optional[bytes], str]:
        """
        Compile LaTeX document with all necessary passes.

        Args:
            files: Dictionary mapping file paths to their content

        Returns:
            Tuple of (pdf_bytes, full_log)

        Raises:
            ValueError: If main.tex is not provided
        """
        if "main.tex" not in files:
            raise ValueError("main.tex must be provided")

        # Create temporary working directory
        work_dir = Path(tempfile.mkdtemp(prefix="latex_"))
        logger.info(f"Created working directory: {work_dir}")

        full_log = []
        pdf_bytes = None

        try:
            # Write all files to disk
            for file_path, content in files.items():
                file_full_path = work_dir / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(content, encoding="utf-8")
                logger.debug(f"Written file: {file_path}")

            # First compilation pass
            full_log.append("=== Initial LaTeX compilation ===")
            exit_code, log = self._compile_latex(work_dir)
            full_log.append(log)

            if exit_code != 0:
                logger.warning("First compilation failed, but continuing...")

            # Check if BibTeX is needed
            bibtex_run = False
            if self._needs_bibtex(log):
                full_log.append("\n=== BibTeX compilation ===")
                exit_code, log = self._compile_bibtex(work_dir)
                full_log.append(log)
                bibtex_run = True

                if exit_code == 0:
                    logger.info("BibTeX compilation successful")
                else:
                    logger.warning("BibTeX compilation had issues")

            # Additional LaTeX passes
            compilation_count = 1
            while compilation_count < self.max_compilations:
                # Check if we need another pass
                last_log = full_log[-1]
                needs_rerun = self._needs_rerun(last_log)

                # Always rerun after BibTeX
                if bibtex_run:
                    needs_rerun = True
                    bibtex_run = False

                if not needs_rerun:
                    break

                compilation_count += 1
                full_log.append(f"\n=== LaTeX compilation pass {compilation_count} ===")
                exit_code, log = self._compile_latex(work_dir)
                full_log.append(log)

                if exit_code != 0:
                    logger.warning(f"Compilation pass {compilation_count} had issues")

            # Check if PDF was generated
            pdf_path = work_dir / "main.pdf"
            if pdf_path.exists():
                pdf_bytes = pdf_path.read_bytes()
                logger.info(f"PDF generated successfully ({len(pdf_bytes)} bytes)")
            else:
                logger.error("PDF file was not generated")
                full_log.append("\n=== ERROR: PDF file was not generated ===")

        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(work_dir)
                logger.info(f"Cleaned up working directory: {work_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up: {e}")

        return pdf_bytes, "\n".join(full_log)